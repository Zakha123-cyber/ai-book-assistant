import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status

from core.config import get_settings
from core.logging import preview_text
from database.session import async_session_factory
<<<<<<< Updated upstream
from models import SummaryLevel
from repositories import BookRepository, ChapterRepository, SummaryRepository
from schemas.book import (
    BookIndexingStatusResponse,
=======
from models import Book, SummaryLevel
from repositories import (
    BookRepository,
    ChapterRepository,
    ChatHistoryRepository,
    ChunkRepository,
    SummaryRepository,
)
from schemas.book import (
    BookDetailResponse,
>>>>>>> Stashed changes
    BookListItem,
    BookListResponse,
    BookUploadResponse,
)
<<<<<<< Updated upstream
=======
from schemas.chat import ChatHistoryItem, ChatHistoryResponse
>>>>>>> Stashed changes
from schemas.summary import (
    BookSummaryResponse,
    ChapterSummariesResponse,
    ChapterSummaryItem,
)
from services.chunker.chapter_detector import detect_chapters
from services.chunker.section_detector import detect_sections
from services.chunker.semantic_chunker import create_semantic_chunks
from services.background_summary import run_summary_indexing
from services.book_indexing import persist_book_metadata
from services.embedding import EmbeddingServiceError, generate_chunk_embeddings
from services.indexing_status import get_book_indexing_status
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


@router.get("", response_model=BookListResponse)
async def list_books() -> BookListResponse:
    async with async_session_factory() as session:
<<<<<<< Updated upstream
        books = await BookRepository(session).list_recent()

    logger.info("Book list retrieved: count=%s", len(books))
    return BookListResponse(
        success=True,
        books=[
            BookListItem(
                id=str(book.id),
                title=book.title,
                author=book.author,
                filename=book.filename,
                uploaded_at=book.uploaded_at.isoformat(),
            )
            for book in books
        ],
=======
        book_repository = BookRepository(session)
        chapter_repository = ChapterRepository(session)
        chunk_repository = ChunkRepository(session)
        books = await book_repository.list_recent()
        items = [
            await _book_to_list_item(book, chapter_repository, chunk_repository)
            for book in books
        ]

    logger.info("Book list retrieved: count=%s", len(items))
    return BookListResponse(
        success=True,
        books=items,
>>>>>>> Stashed changes
        message="Books retrieved successfully.",
    )


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


@router.get("/{book_id}/status", response_model=BookIndexingStatusResponse)
async def get_book_status(book_id: uuid.UUID) -> BookIndexingStatusResponse:
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

        indexing_status = await get_book_indexing_status(session, book)

    logger.info(
        "Book indexing status retrieved: book_id=%s status=%s chunks=%s/%s "
        "chapters=%s/%s book_summary_ready=%s",
        book_id,
        indexing_status.status,
        indexing_status.chunk_summary_count,
        indexing_status.chunk_count,
        indexing_status.chapter_summary_count,
        indexing_status.chapter_count,
        indexing_status.book_summary_ready,
    )
    return BookIndexingStatusResponse(
        success=True,
        book_id=str(book_id),
        embedding_ready=indexing_status.embedding_ready,
        chunk_summary_ready=indexing_status.chunk_summary_ready,
        chapter_summary_ready=indexing_status.chapter_summary_ready,
        book_summary_ready=indexing_status.book_summary_ready,
        chunk_count=indexing_status.chunk_count,
        chunk_summary_count=indexing_status.chunk_summary_count,
        chapter_count=indexing_status.chapter_count,
        chapter_summary_count=indexing_status.chapter_summary_count,
        status=indexing_status.status,
        message="Book indexing status retrieved successfully.",
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


@router.get("/{book_id}/chat-history", response_model=ChatHistoryResponse)
async def get_book_chat_history(book_id: uuid.UUID) -> ChatHistoryResponse:
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

        history = await ChatHistoryRepository(session).list_by_book_id(book_id)

    logger.info(
        "Book chat history retrieved: book_id=%s count=%s",
        book_id,
        len(history),
    )
    return ChatHistoryResponse(
        success=True,
        book_id=str(book_id),
        history=[
            ChatHistoryItem(
                id=str(item.id),
                book_id=str(item.book_id),
                question=item.question,
                answer=item.answer,
                created_at=item.created_at,
            )
            for item in history
        ],
        message="Chat history retrieved successfully.",
    )


@router.post(
    "/upload",
    response_model=BookUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_book(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> BookUploadResponse:
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
        background_tasks.add_task(run_summary_indexing, book.id)
        logger.info("Background summary indexing scheduled: book_id=%s", book.id)
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


@router.get("/{book_id}", response_model=BookDetailResponse)
async def get_book_detail(book_id: uuid.UUID) -> BookDetailResponse:
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

        item = await _book_to_list_item(
            book,
            ChapterRepository(session),
            ChunkRepository(session),
        )

    logger.info("Book detail retrieved: book_id=%s title=%s", book_id, item.title)
    return BookDetailResponse(
        success=True,
        book=item,
        message="Book detail retrieved successfully.",
    )


async def _book_to_list_item(
    book: Book,
    chapter_repository: ChapterRepository,
    chunk_repository: ChunkRepository,
) -> BookListItem:
    chapters = await chapter_repository.list_by_book_id(book.id)
    chunks = await chunk_repository.list_by_book_id(book.id)
    return BookListItem(
        id=str(book.id),
        title=book.title,
        author=book.author,
        filename=book.filename,
        uploaded_at=book.uploaded_at,
        chapter_count=len(chapters),
        chunk_count=len(chunks),
    )
