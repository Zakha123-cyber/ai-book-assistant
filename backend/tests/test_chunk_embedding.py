import unittest

from services.chunker.section_detector import DetectedSection
from services.chunker.semantic_chunker import create_semantic_chunks
from services.embedding.chunk_embedding import generate_chunk_embeddings


class FakeEmbeddingService:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [[float(len(text)), float(index)] for index, text in enumerate(texts)]


class ChunkEmbeddingTest(unittest.IsolatedAsyncioTestCase):
    async def test_generates_embeddings_for_every_chunk_in_batches(self) -> None:
        section = DetectedSection(
            chapter_number=1,
            chapter_title="Chapter",
            number=1,
            title="Main",
            start_page=1,
            end_page=2,
            text="Alpha beta gamma.\n\nDelta epsilon zeta.\n\nEta theta iota.",
        )
        chunks = create_semantic_chunks(
            [section],
            target_tokens=5,
            overlap_tokens=0,
        )
        fake_service = FakeEmbeddingService()

        chunk_embeddings = await generate_chunk_embeddings(
            chunks,
            embedding_service=fake_service,
            batch_size=2,
        )

        self.assertEqual(len(chunk_embeddings), len(chunks))
        self.assertEqual(len(fake_service.calls), 2)
        self.assertEqual(chunk_embeddings[0].chunk.chunk_id, chunks[0].chunk_id)
        self.assertEqual(chunk_embeddings[0].embedding[0], float(len(chunks[0].text)))

    async def test_returns_empty_list_for_no_chunks(self) -> None:
        fake_service = FakeEmbeddingService()

        chunk_embeddings = await generate_chunk_embeddings(
            [],
            embedding_service=fake_service,
        )

        self.assertEqual(chunk_embeddings, [])
        self.assertEqual(fake_service.calls, [])


if __name__ == "__main__":
    unittest.main()

