import unittest

from services.qa import ANSWER_NOT_FOUND, answer_book_question
from services.retriever import RetrievedChunk


class FakeEmbeddingService:
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3]]


class FakeVectorStore:
    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self.chunks = chunks
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
        return self.chunks


class FakeQAService:
    def __init__(self) -> None:
        self.request: dict[str, str] | None = None
        self.call_count = 0

    async def answer_question(self, question: str, retrieved_context: str) -> str:
        self.call_count += 1
        self.request = {
            "question": question,
            "retrieved_context": retrieved_context,
        }
        return "Nara menemukan surat di loteng."


class ChatPipelineTest(unittest.IsolatedAsyncioTestCase):
    async def test_answers_book_question_with_sources(self) -> None:
        chunk = RetrievedChunk(
            id="book-1:chunk-0",
            document="Nara menemukan surat di loteng.",
            metadata={
                "chunk_id": "chunk-0",
                "chapter": 1,
                "chapter_title": "Surat dari Loteng",
                "page_start": 1,
                "page_end": 1,
            },
            distance=0.2,
        )
        vector_store = FakeVectorStore([chunk])
        qa_service = FakeQAService()

        result = await answer_book_question(
            book_id="book-1",
            question="Apa yang ditemukan Nara?",
            top_k=3,
            embedding_service=FakeEmbeddingService(),
            vector_store=vector_store,
            qa_service=qa_service,
        )

        self.assertEqual(result.answer, "Nara menemukan surat di loteng.")
        self.assertEqual(vector_store.request["book_id"], "book-1")
        self.assertEqual(vector_store.request["top_k"], 3)
        self.assertIn("Nara menemukan surat", qa_service.request["retrieved_context"])
        self.assertEqual(len(result.sources), 1)
        self.assertEqual(result.sources[0].chapter, 1)

    async def test_returns_not_found_answer_when_no_chunks_found(self) -> None:
        result = await answer_book_question(
            book_id="book-1",
            question="Apa warna rumah Nara?",
            embedding_service=FakeEmbeddingService(),
            vector_store=FakeVectorStore([]),
            qa_service=FakeQAService(),
        )

        self.assertEqual(result.answer, ANSWER_NOT_FOUND)
        self.assertEqual(result.sources, [])

    async def test_skips_qa_when_top_distance_is_too_high(self) -> None:
        chunk = RetrievedChunk(
            id="book-1:chunk-0",
            document="Pak Wira menjaga kebun.",
            metadata={"chunk_id": "chunk-0"},
            distance=1.62,
        )
        qa_service = FakeQAService()

        result = await answer_book_question(
            book_id="book-1",
            question="Siapa presiden Amerika Serikat?",
            embedding_service=FakeEmbeddingService(),
            vector_store=FakeVectorStore([chunk]),
            qa_service=qa_service,
        )

        self.assertEqual(result.answer, ANSWER_NOT_FOUND)
        self.assertEqual(result.sources, [])
        self.assertEqual(qa_service.call_count, 0)

    async def test_allows_high_distance_when_top_chunk_has_lexical_support(self) -> None:
        chunk = RetrievedChunk(
            id="book-1:chunk-3",
            document="Pak Wira adalah penjaga kebun di sekitar Bukit Angin.",
            metadata={
                "chunk_id": "chunk-3",
                "chapter": 4,
                "chapter_title": "Bertemu Pak Wira",
            },
            distance=1.08,
        )
        qa_service = FakeQAService()

        result = await answer_book_question(
            book_id="book-1",
            question="siapa pak wira?",
            embedding_service=FakeEmbeddingService(),
            vector_store=FakeVectorStore([chunk]),
            qa_service=qa_service,
        )

        self.assertEqual(result.answer, "Nara menemukan surat di loteng.")
        self.assertEqual(len(result.sources), 1)
        self.assertEqual(qa_service.call_count, 1)

    async def test_clears_sources_when_qwen_returns_not_found_answer(self) -> None:
        class NotFoundQAService(FakeQAService):
            async def answer_question(
                self,
                question: str,
                retrieved_context: str,
            ) -> str:
                self.call_count += 1
                return ANSWER_NOT_FOUND

        chunk = RetrievedChunk(
            id="book-1:chunk-0",
            document="Nara menemukan surat di loteng.",
            metadata={"chunk_id": "chunk-0"},
            distance=0.2,
        )

        result = await answer_book_question(
            book_id="book-1",
            question="Apa warna rumah Nara?",
            embedding_service=FakeEmbeddingService(),
            vector_store=FakeVectorStore([chunk]),
            qa_service=NotFoundQAService(),
        )

        self.assertEqual(result.answer, ANSWER_NOT_FOUND)
        self.assertEqual(result.sources, [])


if __name__ == "__main__":
    unittest.main()
