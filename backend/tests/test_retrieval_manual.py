import asyncio
import sys

from services.embedding import generate_question_embedding
from services.retriever import search_similar_chunks

DEFAULT_QUERY = "What happens when Alice follows the white rabbit?"


async def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: uv run python -m tests.test_retrieval_manual <book_id> "
            "[query]"
        )

    book_id = sys.argv[1]
    query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else DEFAULT_QUERY

    query_embedding = await generate_question_embedding(query)
    results = search_similar_chunks(
        query_embedding=query_embedding,
        book_id=book_id,
        top_k=5,
    )

    print(f"query: {query}")
    print(f"result_count: {len(results)}")
    for index, result in enumerate(results, start=1):
        metadata = result.metadata
        preview = result.document.replace("\n", " ")[:300]
        print(f"\n#{index}")
        print(f"id: {result.id}")
        print(f"distance: {result.distance}")
        print(
            "source: "
            f"chapter={metadata.get('chapter')} "
            f"title={metadata.get('chapter_title')} "
            f"pages={metadata.get('page_start')}-{metadata.get('page_end')}"
        )
        print(f"preview: {preview}")


if __name__ == "__main__":
    asyncio.run(main())
