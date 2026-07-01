import asyncio
import sys
import uuid

from database.session import async_session_factory, engine
from repositories import ChunkRepository
from services.summarizer import summarize_and_store_chunks

DEFAULT_LIMIT = 3


async def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: uv run python -m tests.test_chunk_summary_manual <book_id> "
            "[limit]"
        )

    book_id = uuid.UUID(sys.argv[1])
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_LIMIT

    try:
        async with async_session_factory() as session:
            chunks = list(await ChunkRepository(session).list_by_book_id(book_id))
            selected_chunks = chunks[:limit]
            if not selected_chunks:
                raise SystemExit(f"No chunks found for book_id={book_id}")

            results = await summarize_and_store_chunks(session, selected_chunks)
            await session.commit()

            print(f"book_id: {book_id}")
            print(f"chunk_count: {len(chunks)}")
            print(f"summarized_count: {len(results)}")
            for index, result in enumerate(results, start=1):
                cache_status = "cached" if result.cached else "generated"
                preview = result.summary.replace("\n", " ")[:240]
                print(f"\n#{index} chunk_id={result.chunk_id} status={cache_status}")
                print(preview)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
