import unittest

from services.retriever import SimilaritySearchError, search_similar_chunks
from services.retriever.chroma_store import RetrievedChunk


class FakeVectorStore:
    def __init__(self) -> None:
        self.request: dict[str, object] | None = None

    def query_by_embedding(
        self,
        query_embedding: list[float],
        book_id: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        self.request = {
            "query_embedding": query_embedding,
            "book_id": book_id,
            "top_k": top_k,
        }
        return [
            RetrievedChunk(
                id="book-1:chunk-0",
                document="Nara menemukan surat di loteng.",
                metadata={"book_id": "book-1", "chapter": 1},
                distance=0.21,
            )
        ]


class SimilaritySearchTest(unittest.TestCase):
    def test_searches_similar_chunks_with_top_k(self) -> None:
        store = FakeVectorStore()

        results = search_similar_chunks(
            query_embedding=[0.1, 0.2, 0.3],
            book_id=" book-1 ",
            top_k=3,
            store=store,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "book-1:chunk-0")
        self.assertEqual(store.request["book_id"], "book-1")
        self.assertEqual(store.request["top_k"], 3)

    def test_rejects_empty_book_id(self) -> None:
        with self.assertRaises(SimilaritySearchError):
            search_similar_chunks([0.1], "   ", store=FakeVectorStore())

    def test_rejects_empty_query_embedding(self) -> None:
        with self.assertRaises(SimilaritySearchError):
            search_similar_chunks([], "book-1", store=FakeVectorStore())

    def test_rejects_invalid_top_k(self) -> None:
        with self.assertRaises(SimilaritySearchError):
            search_similar_chunks([0.1], "book-1", top_k=0, store=FakeVectorStore())


if __name__ == "__main__":
    unittest.main()
