import unittest

from services.embedding import QuestionEmbeddingError, generate_question_embedding


class FakeEmbeddingService:
    def __init__(self) -> None:
        self.requests: list[list[str]] = []

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.requests.append(texts)
        return [[0.1, 0.2, 0.3]]


class EmptyEmbeddingService:
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return []


class QuestionEmbeddingTest(unittest.IsolatedAsyncioTestCase):
    async def test_generates_embedding_for_normalized_question(self) -> None:
        service = FakeEmbeddingService()

        vector = await generate_question_embedding(
            "  Apa yang ditemukan Nara di loteng?  ",
            embedding_service=service,
        )

        self.assertEqual(service.requests, [["Apa yang ditemukan Nara di loteng?"]])
        self.assertEqual(vector, [0.1, 0.2, 0.3])

    async def test_rejects_empty_question(self) -> None:
        with self.assertRaises(QuestionEmbeddingError):
            await generate_question_embedding("   ", embedding_service=FakeEmbeddingService())

    async def test_rejects_empty_embedding_response(self) -> None:
        with self.assertRaises(QuestionEmbeddingError):
            await generate_question_embedding(
                "Apa isi buku ini?",
                embedding_service=EmptyEmbeddingService(),
            )


if __name__ == "__main__":
    unittest.main()
