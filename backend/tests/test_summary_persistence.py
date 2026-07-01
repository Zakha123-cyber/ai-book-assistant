import asyncio
from pathlib import Path

from database.session import async_session_factory, engine
from models import SummaryLevel
from repositories import ChapterRepository, ChunkRepository, SummaryRepository
from services.book_indexing import persist_book_metadata
from services.chunker.chapter_detector import DetectedChapter
from services.chunker.semantic_chunker import SemanticChunk
from services.summarizer import (
    summarize_and_store_book,
    summarize_and_store_chapters,
    summarize_and_store_chunks,
)


class FakeChunkSummaryClient:
    async def summarize_chunk(self, chunk_text: str) -> str:
        return f"- Chunk summary: {chunk_text}"


class FakeChapterSummaryClient:
    async def summarize_chapter(self, chunk_summaries: list[str]) -> str:
        return "1. Overview\n" + "\n".join(chunk_summaries)


class FakeBookSummaryClient:
    async def summarize_book(self, chapter_summaries: list[str]) -> str:
        return "# Overview\n" + "\n".join(chapter_summaries)


async def run_summary_persistence_check() -> None:
    async with async_session_factory() as session:
        transaction = await session.begin()
        try:
            book = await persist_book_metadata(
                session=session,
                original_filename="summary_test.pdf",
                stored_path=Path("uploads/summary_test.pdf"),
                chapters=[
                    DetectedChapter(
                        number=1,
                        title="Chapter One",
                        start_page=1,
                        end_page=2,
                        text="Chapter text.",
                    )
                ],
                chunks=[
                    SemanticChunk(
                        chunk_id="chunk-0",
                        chapter_number=1,
                        chapter_title="Chapter One",
                        section_number=1,
                        section_title="Main Section",
                        chunk_index=0,
                        text="First chunk text.",
                        token_count=3,
                        metadata={},
                    ),
                    SemanticChunk(
                        chunk_id="chunk-1",
                        chapter_number=1,
                        chapter_title="Chapter One",
                        section_number=1,
                        section_title="Main Section",
                        chunk_index=1,
                        text="Second chunk text.",
                        token_count=3,
                        metadata={},
                    ),
                ],
            )

            chapters = list(await ChapterRepository(session).list_by_book_id(book.id))
            chunks = list(await ChunkRepository(session).list_by_chapter_id(chapters[0].id))

            chunk_results = await summarize_and_store_chunks(
                session,
                chunks,
                client=FakeChunkSummaryClient(),
            )
            chapter_results = await summarize_and_store_chapters(
                session,
                chapters,
                client=FakeChapterSummaryClient(),
            )
            book_result = await summarize_and_store_book(
                session,
                book,
                client=FakeBookSummaryClient(),
            )

            summary_repository = SummaryRepository(session)
            chunk_summaries = [
                await summary_repository.list_by_reference(
                    result.chunk_id,
                    SummaryLevel.CHUNK,
                )
                for result in chunk_results
            ]
            chapter_summaries = await summary_repository.list_by_reference(
                chapter_results[0].chapter_id,
                SummaryLevel.CHAPTER,
            )
            book_summaries = await summary_repository.list_by_reference(
                book_result.book_id,
                SummaryLevel.BOOK,
            )

            assert len(chunk_results) == 2
            assert all(len(items) == 1 for items in chunk_summaries)
            assert len(chapter_summaries) == 1
            assert len(book_summaries) == 1
            assert chapter_summaries[0].reference_id == chapters[0].id
            assert book_summaries[0].reference_id == book.id
        finally:
            await transaction.rollback()


async def main() -> None:
    try:
        await run_summary_persistence_check()
    finally:
        await engine.dispose()
    print("Summary persistence check passed.")


if __name__ == "__main__":
    asyncio.run(main())
