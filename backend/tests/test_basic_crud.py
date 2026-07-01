import asyncio

from database.session import async_session_factory, engine
from models import Book, Chapter, ChatHistory, Chunk, Summary, SummaryLevel
from repositories import (
    BookRepository,
    ChapterRepository,
    ChatHistoryRepository,
    ChunkRepository,
    SummaryRepository,
)


async def run_basic_crud_check() -> None:
    async with async_session_factory() as session:
        transaction = await session.begin()
        try:
            book_repository = BookRepository(session)
            chapter_repository = ChapterRepository(session)
            chunk_repository = ChunkRepository(session)
            summary_repository = SummaryRepository(session)
            chat_history_repository = ChatHistoryRepository(session)

            book = await book_repository.add(
                Book(
                    title="CRUD Smoke Test Book",
                    author="AI Book Assistant",
                    filename="crud-smoke-test.pdf",
                )
            )
            assert await book_repository.get_by_id(book.id) is not None

            chapter = await chapter_repository.add(
                Chapter(
                    book_id=book.id,
                    number=1,
                    title="Smoke Test Chapter",
                    summary="Chapter summary.",
                )
            )
            chapters = await chapter_repository.list_by_book_id(book.id)
            assert len(chapters) == 1
            assert chapters[0].id == chapter.id

            chunk = await chunk_repository.add(
                Chunk(
                    chapter_id=chapter.id,
                    chunk_index=0,
                    content="Smoke test chunk content.",
                )
            )
            chunks = await chunk_repository.list_by_chapter_id(chapter.id)
            assert len(chunks) == 1
            assert chunks[0].id == chunk.id

            summary = await summary_repository.add(
                Summary(
                    level=SummaryLevel.CHUNK,
                    reference_id=chunk.id,
                    summary="Smoke test summary.",
                )
            )
            summaries = await summary_repository.list_by_reference(
                chunk.id,
                SummaryLevel.CHUNK,
            )
            assert len(summaries) == 1
            assert summaries[0].id == summary.id

            chat_history = await chat_history_repository.add(
                ChatHistory(
                    book_id=book.id,
                    question="Smoke test question?",
                    answer="Smoke test answer.",
                )
            )
            chat_entries = await chat_history_repository.list_by_book_id(book.id)
            assert len(chat_entries) == 1
            assert chat_entries[0].id == chat_history.id

            await book_repository.delete(book)
            assert await book_repository.get_by_id(book.id) is None
        finally:
            await transaction.rollback()


async def main() -> None:
    try:
        await run_basic_crud_check()
    finally:
        await engine.dispose()
    print("Basic CRUD check passed.")


if __name__ == "__main__":
    asyncio.run(main())
