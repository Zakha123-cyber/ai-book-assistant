import asyncio
from pathlib import Path

from database.session import async_session_factory, engine
from repositories import ChapterRepository, ChunkRepository
from services.book_indexing import persist_book_metadata
from services.chunker.chapter_detector import DetectedChapter
from services.chunker.semantic_chunker import SemanticChunk


async def run_book_indexing_check() -> None:
    async with async_session_factory() as session:
        transaction = await session.begin()
        try:
            book = await persist_book_metadata(
                session=session,
                original_filename="sample_book.pdf",
                stored_path=Path("uploads/sample_book.pdf"),
                chapters=[
                    DetectedChapter(
                        number=1,
                        title="Chapter One",
                        start_page=1,
                        end_page=3,
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
                        text="Chunk text.",
                        token_count=3,
                        metadata={},
                    )
                ],
            )

            chapters = await ChapterRepository(session).list_by_book_id(book.id)
            chunks = await ChunkRepository(session).list_by_chapter_id(chapters[0].id)

            assert book.title == "sample book"
            assert len(chapters) == 1
            assert chapters[0].title == "Chapter One"
            assert len(chunks) == 1
            assert chunks[0].content == "Chunk text."
        finally:
            await transaction.rollback()


async def main() -> None:
    try:
        await run_book_indexing_check()
    finally:
        await engine.dispose()
    print("Book indexing persistence check passed.")


if __name__ == "__main__":
    asyncio.run(main())

