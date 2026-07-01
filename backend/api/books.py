import logging
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from core.config import get_settings
from core.logging import preview_text
from database.session import async_session_factory
from models import SummaryLevel
from repositories import BookRepository, ChapterRepository, SummaryRepository
from schemas.book import BookUploadResponse
from schemas.summary import (
    BookSummaryResponse,
    ChapterSummariesResponse,
    ChapterSummaryItem,
)
from services.chunker.chapter_detector import detect_chapters
from services.chunker.section_detector import detect_sections
from services.chunker.semantic_chunker import create_semantic_chunks
from services.book_indexing import persist_book_metadata
from services.embedding import EmbeddingServiceError, generate_chunk_embeddings
from services.parser.extraction_storage import save_extracted_text
from services.parser.pdf_parser import PDFParsingError, extract_text_from_pdf
from services.parser.text_cleaner import (
    normalize_whitespace,
    remove_boilerplate_lines,
    remove_page_numbers,
    remove_repeated_headers_footers,
)
from services.parser.upload_storage import save_uploaded_pdf
from services.retriever import ChromaChunkStore
from utils.upload_validation import UploadValidationError, validate_pdf_upload

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/{book_id}/summary", response_model=BookSummaryResponse)
async def get_book_summary(book_id: uuid.UUID) -> BookSummaryResponse:
    async with async_session_factory() as session:
        book = await BookRepository(session).get_by_id(book_id)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "message": "Book not found.",
                },
            )

        summaries = await SummaryRepository(session).list_by_reference(
            reference_id=book_id,
            level=SummaryLevel.BOOK,
        )
        if not summaries:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "message": "Book summary not found.",
                },
            )

        return BookSummaryResponse(
            success=True,
            book_id=str(book.id),
            level=SummaryLevel.BOOK.value,
            summary=summaries[0].summary,
            message="Book summary retrieved successfully.",
        )


@router.get("/{book_id}/chapters", response_model=ChapterSummariesResponse)
async def get_chapter_summaries(book_id: uuid.UUID) -> ChapterSummariesResponse:
    async with async_session_factory() as session:
        book = await BookRepository(session).get_by_id(book_id)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "message": "Book not found.",
                },
            )

        chapters = await ChapterRepository(session).list_by_book_id(book_id)
        summary_repository = SummaryRepository(session)
        chapter_items: list[ChapterSummaryItem] = []

        for chapter in chapters:
            summaries = await summary_repository.list_by_reference(
                reference_id=chapter.id,
                level=SummaryLevel.CHAPTER,
            )
            chapter_items.append(
                ChapterSummaryItem(
                    chapter_id=str(chapter.id),
                    number=chapter.number,
                    title=chapter.title,
                    summary=summaries[0].summary if summaries else None,
                )
            )

        return ChapterSummariesResponse(
            success=True,
            book_id=str(book.id),
            chapters=chapter_items,
            message="Chapter summaries retrieved successfully.",
        )


@router.post(
    "/upload",
    response_model=BookUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_book(file: UploadFile = File(...)) -> BookUploadResponse:
    logger.info("Upload received: filename=%s", file.filename)
    try:
        size_bytes = await validate_pdf_upload(file, settings.max_upload_mb)
    except UploadValidationError as error:
        logger.warning(
            "Book upload rejected: filename=%s reason=%s",
            file.filename,
            error,
        )
        raise HTTPException(
            status_code=error.status_code,
            detail={
                "success": False,
                "message": error.message,
            },
        ) from error

    try:
        stored_path = await save_uploaded_pdf(file)
        logger.info(
            "Upload stored: filename=%s size_bytes=%s stored_path=%s",
            file.filename,
            size_bytes,
            stored_path,
        )
    except OSError as error:
        logger.exception("Failed to store uploaded file: filename=%s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Failed to store uploaded file.",
            },
        ) from error

    try:
        parsed_pdf = extract_text_from_pdf(stored_path)
        logger.info(
            "PDF extracted: filename=%s page_count=%s text_length=%s preview=%s",
            file.filename,
            parsed_pdf.page_count,
            len(parsed_pdf.text),
            preview_text(parsed_pdf.text),
        )
        cleaned_pdf = remove_boilerplate_lines(parsed_pdf)
        cleaned_pdf = remove_repeated_headers_footers(cleaned_pdf)
        cleaned_pdf = remove_page_numbers(cleaned_pdf)
        cleaned_pdf = normalize_whitespace(cleaned_pdf)
        logger.info(
            "PDF cleaned: filename=%s text_length=%s preview=%s",
            file.filename,
            len(cleaned_pdf.text),
            preview_text(cleaned_pdf.text),
        )
        chapters = detect_chapters(cleaned_pdf)
        sections = detect_sections(chapters)
        chunks = create_semantic_chunks(
            sections,
            base_metadata={
                "book_id": stored_path.stem,
                "filename": file.filename or "",
                "stored_path": str(stored_path),
            },
        )
        logger.info(
            "Book chunked: filename=%s chapters=%s sections=%s chunks=%s "
            "first_chapter=%s first_chunk_preview=%s",
            file.filename,
            len(chapters),
            len(sections),
            len(chunks),
            chapters[0].title if chapters else None,
            preview_text(chunks[0].text) if chunks else "",
        )
    except PDFParsingError as error:
        logger.warning(
            "Book parsing failed: filename=%s stored_path=%s",
            file.filename,
            stored_path,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": str(error),
            },
        ) from error

    try:
        extracted_path = save_extracted_text(cleaned_pdf, stored_path)
    except OSError as error:
        logger.exception(
            "Failed to store extracted text: filename=%s stored_path=%s",
            file.filename,
            stored_path,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Failed to store extracted text.",
            },
        ) from error

    try:
        async with async_session_factory() as session:
            book = await persist_book_metadata(
                session=session,
                original_filename=file.filename or "",
                stored_path=stored_path,
                chapters=chapters,
                chunks=chunks,
            )
            await session.commit()
        logger.info(
            "Book metadata persisted: book_id=%s title=%s chapters=%s chunks=%s",
            book.id,
            book.title,
            len(chapters),
            len(chunks),
        )
    except Exception as error:
        logger.exception(
            "Failed to persist book metadata: filename=%s stored_path=%s",
            file.filename,
            stored_path,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Failed to persist book metadata.",
            },
        ) from error

    for chunk in chunks:
        chunk.metadata["book_id"] = str(book.id)

    try:
        chunk_embeddings = await generate_chunk_embeddings(chunks)
        ChromaChunkStore().upsert_chunk_embeddings(chunk_embeddings)
        logger.info(
            "Book embeddings indexed: book_id=%s embedding_count=%s",
            book.id,
            len(chunk_embeddings),
        )
    except EmbeddingServiceError as error:
        logger.exception("Failed to generate embeddings: book_id=%s", book.id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "success": False,
                "message": "Failed to generate chunk embeddings.",
            },
        ) from error
    except Exception as error:
        logger.exception("Failed to store embeddings in ChromaDB: book_id=%s", book.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Failed to store chunk embeddings.",
            },
        ) from error

    logger.info(
        "Book upload accepted: book_id=%s filename=%s size_bytes=%s stored_path=%s "
        "extracted_path=%s page_count=%s chapter_count=%s section_count=%s "
        "chunk_count=%s",
        book.id,
        file.filename,
        size_bytes,
        stored_path,
        extracted_path,
        cleaned_pdf.page_count,
        len(chapters),
        len(sections),
        len(chunks),
    )
    return BookUploadResponse(
        success=True,
        book_id=str(book.id),
        filename=file.filename or "",
        stored_path=str(stored_path),
        extracted_path=str(extracted_path),
        page_count=cleaned_pdf.page_count,
        chapter_count=len(chapters),
        section_count=len(sections),
        chunk_count=len(chunks),
        extracted_text_length=len(cleaned_pdf.text),
        message="Upload indexed successfully.",
    )
