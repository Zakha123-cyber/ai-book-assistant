from typing import Protocol

from services.embedding.dashscope_embedding import DashScopeEmbeddingService


class QuestionEmbeddingError(ValueError):
    pass


class TextEmbeddingService(Protocol):
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        pass


async def generate_question_embedding(
    question: str,
    embedding_service: TextEmbeddingService | None = None,
) -> list[float]:
    normalized_question = question.strip()
    if not normalized_question:
        raise QuestionEmbeddingError("Question cannot be empty.")

    service = embedding_service or DashScopeEmbeddingService()
    embeddings = await service.embed_texts([normalized_question])
    if not embeddings:
        raise QuestionEmbeddingError("Embedding service returned no vectors.")

    return embeddings[0]
