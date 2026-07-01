import logging
from typing import Protocol

from core.logging import preview_text
from services.embedding.dashscope_embedding import DashScopeEmbeddingService

logger = logging.getLogger(__name__)


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

    logger.info("Question embedding started: question=%s", preview_text(normalized_question))
    service = embedding_service or DashScopeEmbeddingService()
    embeddings = await service.embed_texts([normalized_question])
    if not embeddings:
        raise QuestionEmbeddingError("Embedding service returned no vectors.")

    logger.info(
        "Question embedding completed: dimension=%s sample=%s",
        len(embeddings[0]),
        embeddings[0][:5],
    )
    return embeddings[0]
