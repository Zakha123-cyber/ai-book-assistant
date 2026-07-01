import unittest

from services.chunker.section_detector import DetectedSection
from services.chunker.semantic_chunker import create_semantic_chunks
from services.embedding.chunk_embedding import ChunkEmbedding
from services.retriever.chroma_store import ChromaChunkStore


class FakeCollection:
    def __init__(self) -> None:
        self.upsert_payload: dict[str, object] | None = None
        self.query_payload: dict[str, object] | None = None

    def upsert(self, **kwargs: object) -> None:
        self.upsert_payload = kwargs

    def query(self, **kwargs: object) -> dict[str, object]:
        self.query_payload = kwargs
        return {
            "ids": [["book-1:chunk-0"]],
            "documents": [["Alpha beta gamma."]],
            "metadatas": [[{"book_id": "book-1", "chapter": 1}]],
            "distances": [[0.12]],
        }


class FakeChromaClient:
    def __init__(self) -> None:
        self.collection = FakeCollection()
        self.collection_name: str | None = None

    def get_or_create_collection(self, name: str) -> FakeCollection:
        self.collection_name = name
        return self.collection


class ChromaChunkStoreTest(unittest.TestCase):
    def test_upserts_chunk_embeddings(self) -> None:
        section = DetectedSection(
            chapter_number=1,
            chapter_title="Chapter",
            number=1,
            title="Main",
            start_page=1,
            end_page=2,
            text="Alpha beta gamma.",
        )
        chunk = create_semantic_chunks(
            [section],
            base_metadata={"book_id": "book-1"},
        )[0]
        fake_client = FakeChromaClient()
        store = ChromaChunkStore(client=fake_client, collection_name="test_chunks")

        store.upsert_chunk_embeddings([
            ChunkEmbedding(chunk=chunk, embedding=[0.1, 0.2, 0.3])
        ])

        payload = fake_client.collection.upsert_payload
        self.assertEqual(fake_client.collection_name, "test_chunks")
        self.assertIsNotNone(payload)
        self.assertEqual(payload["ids"], ["book-1:chunk-0"])
        self.assertEqual(payload["embeddings"], [[0.1, 0.2, 0.3]])
        self.assertEqual(payload["documents"], ["Alpha beta gamma."])
        self.assertEqual(payload["metadatas"][0]["book_id"], "book-1")

    def test_queries_by_embedding_and_book_id(self) -> None:
        fake_client = FakeChromaClient()
        store = ChromaChunkStore(client=fake_client, collection_name="test_chunks")

        results = store.query_by_embedding(
            query_embedding=[0.1, 0.2, 0.3],
            book_id="book-1",
            top_k=5,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "book-1:chunk-0")
        self.assertEqual(results[0].document, "Alpha beta gamma.")
        self.assertEqual(results[0].metadata["book_id"], "book-1")
        self.assertEqual(results[0].distance, 0.12)
        self.assertEqual(fake_client.collection.query_payload["where"], {"book_id": "book-1"})


if __name__ == "__main__":
    unittest.main()
