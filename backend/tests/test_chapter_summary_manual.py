import asyncio
import sys
import uuid

from database.session import async_session_factory, engine
from repositories import ChapterRepository
from services.summarizer import (
    MissingChunkSummariesError,
    summarize_and_store_chapters,
)

DEFAULT_LIMIT = 1


async def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: uv run python -m tests.test_chapter_summary_manual <book_id> "
            "[chapter_limit]"
        )

    book_id = uuid.UUID(sys.argv[1])
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_LIMIT

    try:
        async with async_session_factory() as session:
            chapters = list(await ChapterRepository(session).list_by_book_id(book_id))
            selected_chapters = chapters[:limit]
            if not selected_chapters:
                raise SystemExit(f"No chapters found for book_id={book_id}")

            try:
                results = await summarize_and_store_chapters(
                    session,
                    selected_chapters,
                )
            except MissingChunkSummariesError as error:
                raise SystemExit(
                    "Cannot summarize chapter yet. Generate missing chunk summaries "
                    "first. "
                    f"chapter={error.chapter_title} "
                    f"missing={error.missing_count} "
                    f"total={error.total_count}"
                ) from error

            await session.commit()

            print(f"book_id: {book_id}")
            print(f"chapter_count: {len(chapters)}")
            print(f"summarized_count: {len(results)}")
            for index, result in enumerate(results, start=1):
                cache_status = "cached" if result.cached else "generated"
                preview = result.summary.replace("\n", " ")[:300]
                print(
                    f"\n#{index} chapter_id={result.chapter_id} "
                    f"title={result.chapter_title} status={cache_status} "
                    f"chunk_summaries={result.chunk_summary_count}"
                )
                print(preview)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
