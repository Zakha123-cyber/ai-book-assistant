import logging

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from core.config import get_settings
from database.session import async_session_factory
from schemas.book import BookUploadResponse
from services.chunker.chapter_detector import detect_chapters
from services.chunker.section_detector import detect_sections
from services.chunker.semantic_chunker import create_semantic_chunks
from services.book_indexing import persist_book_metadata
from services.parser.extraction_storage import save_extracted_text
from services.parser.pdf_parser import PDFParsingError, extract_text_from_pdf
from services.parser.text_cleaner import (
    normalize_whitespace,
    remove_page_numbers,
    remove_repeated_headers_footers,
)
from services.parser.upload_storage import save_uploaded_pdf
from utils.upload_validation import UploadValidationError, validate_pdf_upload

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/books", tags=["books"])


@router.post(
    "/upload",
    response_model=BookUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_book(file: UploadFile = File(...)) -> BookUploadResponse:
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
        cleaned_pdf = remove_repeated_headers_footers(parsed_pdf)
        cleaned_pdf = remove_page_numbers(cleaned_pdf)
        cleaned_pdf = normalize_whitespace(cleaned_pdf)
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
        message="Upload stored and extracted text saved successfully.",
    )
