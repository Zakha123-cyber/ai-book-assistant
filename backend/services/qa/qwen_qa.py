import logging
from time import perf_counter

from openai import AsyncOpenAI, OpenAIError

from core.config import get_settings
from core.logging import preview_text
from services.prompt.qa_prompts import build_qa_prompt

logger = logging.getLogger(__name__)


class QAServiceError(RuntimeError):
    pass


class QwenQAService:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.dashscope_api_key:
            raise QAServiceError("DASHSCOPE_API_KEY is not configured.")
        if not settings.dashscope_base_url:
            raise QAServiceError("DASHSCOPE_BASE_URL is not configured.")

        self.model = settings.qwen_model
        self.client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.dashscope_base_url,
        )

    async def answer_question(self, question: str, retrieved_context: str) -> str:
        prompt = build_qa_prompt(
            question=question,
            retrieved_context=retrieved_context,
        )
        logger.info(
            "Qwen QA request started: model=%s question=%s context_chars=%s",
            self.model,
            preview_text(question),
            len(retrieved_context),
        )
        start_time = perf_counter()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You answer questions about a book using only the "
                            "provided retrieved context."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )
        except OpenAIError as error:
            logger.exception("Qwen QA request failed.")
            raise QAServiceError("QA request failed.") from error

        answer = response.choices[0].message.content
        if not answer:
            raise QAServiceError("QA response was empty.")

        logger.info(
            "Qwen QA response received: model=%s duration_ms=%s answer_preview=%s",
            self.model,
            round((perf_counter() - start_time) * 1000, 2),
            preview_text(answer),
        )
        return answer.strip()
