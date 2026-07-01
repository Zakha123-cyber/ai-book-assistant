import logging
import uuid

from database.session import async_session_factory
from repositories import BookRepository, ChapterRepository, ChunkRepository
from services.indexing_status import get_book_indexing_status
from services.summarizer import (
    MissingChapterSummariesError,
    MissingChunkSummariesError,
    SummaryGenerationError,
    summarize_and_store_book,
    summarize_and_store_chapters,
    summarize_and_store_chunks,
)

logger = logging.getLogger(__name__)


async def run_summary_indexing(book_id: uuid.UUID) -> None:
    logger.info("BACKGROUND INDEXING STARTED: book_id=%s", book_id)
    try:
        async with async_session_factory() as session:
            book = await BookRepository(session).get_by_id(book_id)
            if book is None:
                logger.warning(
                    "Background summary indexing skipped: book not found book_id=%s",
                    book_id,
                )
                return

            chunks = list(await ChunkRepository(session).list_by_book_id(book_id))
            chapters = list(await ChapterRepository(session).list_by_book_id(book_id))
            logger.info(
                "BACKGROUND INDEXING DATA LOADED: book_id=%s title=%s chunks=%s "
                "chapters=%s",
                book_id,
                book.title,
                len(chunks),
                len(chapters),
            )
            await _log_status(session, book, "initial")

            logger.info(
                "BACKGROUND PHASE START: book_id=%s phase=chunk_summaries total=%s",
                book_id,
                len(chunks),
            )
            chunk_results = await summarize_and_store_chunks(session, chunks)
            await session.commit()
            logger.info(
                "BACKGROUND PHASE DONE: book_id=%s phase=chunk_summaries count=%s",
                book_id,
                len(chunk_results),
            )
            await _log_status(session, book, "after_chunk_summaries")

            logger.info(
                "BACKGROUND PHASE START: book_id=%s phase=chapter_summaries total=%s",
                book_id,
                len(chapters),
            )
            chapter_results = await summarize_and_store_chapters(session, chapters)
            await session.commit()
            logger.info(
                "BACKGROUND PHASE DONE: book_id=%s phase=chapter_summaries count=%s",
                book_id,
                len(chapter_results),
            )
            await _log_status(session, book, "after_chapter_summaries")

            logger.info(
                "BACKGROUND PHASE START: book_id=%s phase=book_summary",
                book_id,
            )
            book_result = await summarize_and_store_book(session, book)
            await session.commit()
            logger.info(
                "BACKGROUND PHASE DONE: book_id=%s phase=book_summary cached=%s",
                book_id,
                book_result.cached,
            )
            await _log_status(session, book, "after_book_summary")
    except (
        MissingChunkSummariesError,
        MissingChapterSummariesError,
        SummaryGenerationError,
    ):
        logger.exception("BACKGROUND INDEXING FAILED: book_id=%s", book_id)
    except Exception:
        logger.exception(
            "UNEXPECTED BACKGROUND INDEXING FAILURE: book_id=%s",
            book_id,
        )
    else:
        logger.info("BACKGROUND INDEXING FINISHED: book_id=%s", book_id)


async def _log_status(session, book, checkpoint: str) -> None:
    status = await get_book_indexing_status(session, book)
    logger.info(
        "BACKGROUND STATUS: checkpoint=%s book_id=%s status=%s "
        "chunk_summaries=%s/%s chapter_summaries=%s/%s book_summary_ready=%s",
        checkpoint,
        book.id,
        status.status,
        status.chunk_summary_count,
        status.chunk_count,
        status.chapter_summary_count,
        status.chapter_count,
        status.book_summary_ready,
    )
