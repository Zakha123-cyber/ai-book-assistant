import logging

from openai import AsyncOpenAI, OpenAIError

from core.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingServiceError(RuntimeError):
    pass


class DashScopeEmbeddingService:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.dashscope_api_key:
            raise EmbeddingServiceError("DASHSCOPE_API_KEY is not configured.")
        if not settings.dashscope_base_url:
            raise EmbeddingServiceError("DASHSCOPE_BASE_URL is not configured.")

        self.model = settings.dashscope_embedding_model
        self.client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.dashscope_base_url,
        )

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts,
            )
        except OpenAIError as error:
            logger.exception("DashScope embedding request failed.")
            raise EmbeddingServiceError("Embedding request failed.") from error

        embeddings = [item.embedding for item in response.data]
        logger.info(
            "Generated embeddings: model=%s input_count=%s",
            self.model,
            len(texts),
        )
        return embeddings
