import asyncio
import sys
import uuid

from database.session import async_session_factory, engine
from repositories import BookRepository
from services.summarizer import (
    MissingChapterSummariesError,
    summarize_and_store_book,
)


async def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: uv run python -m tests.test_book_summary_manual <book_id>"
        )

    book_id = uuid.UUID(sys.argv[1])

    try:
        async with async_session_factory() as session:
            book = await BookRepository(session).get_by_id(book_id)
            if book is None:
                raise SystemExit(f"No book found for book_id={book_id}")

            try:
                result = await summarize_and_store_book(session, book)
            except MissingChapterSummariesError as error:
                raise SystemExit(
                    "Cannot summarize book yet. Generate missing chapter summaries "
                    "first. "
                    f"missing={error.missing_count} "
                    f"total={error.total_count}"
                ) from error

            await session.commit()

            cache_status = "cached" if result.cached else "generated"
            preview = result.summary.replace("\n", " ")[:500]
            print(f"book_id: {result.book_id}")
            print(f"title: {result.book_title}")
            print(f"status: {cache_status}")
            print(f"chapter_summaries: {result.chapter_summary_count}")
            print(f"preview: {preview}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
