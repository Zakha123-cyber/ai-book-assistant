import logging
from time import perf_counter

from openai import AsyncOpenAI, OpenAIError

from core.config import get_settings
from core.logging import preview_text
from services.prompt.summary_prompts import (
    build_book_summary_prompt,
    build_chapter_summary_prompt,
    build_chunk_summary_prompt,
)

logger = logging.getLogger(__name__)


class SummaryGenerationError(RuntimeError):
    pass


class QwenChunkSummaryClient:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.dashscope_api_key:
            raise SummaryGenerationError("DASHSCOPE_API_KEY is not configured.")
        if not settings.dashscope_base_url:
            raise SummaryGenerationError("DASHSCOPE_BASE_URL is not configured.")

        self.model = settings.qwen_model
        self.client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.dashscope_base_url,
        )

    async def summarize_chunk(self, chunk_text: str) -> str:
        prompt = build_chunk_summary_prompt(chunk_text)
        logger.info(
            "Qwen chunk summary request started: model=%s chunk_chars=%s preview=%s",
            self.model,
            len(chunk_text),
            preview_text(chunk_text),
        )
        start_time = perf_counter()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You summarize book passages accurately and concisely."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
        except OpenAIError as error:
            logger.exception("Qwen chunk summary request failed.")
            raise SummaryGenerationError("Chunk summary request failed.") from error

        summary = response.choices[0].message.content
        if not summary:
            raise SummaryGenerationError("Chunk summary response was empty.")

        logger.info(
            "Qwen chunk summary response received: model=%s duration_ms=%s "
            "summary_preview=%s",
            self.model,
            round((perf_counter() - start_time) * 1000, 2),
            preview_text(summary),
        )
        return summary.strip()


class QwenChapterSummaryClient:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.dashscope_api_key:
            raise SummaryGenerationError("DASHSCOPE_API_KEY is not configured.")
        if not settings.dashscope_base_url:
            raise SummaryGenerationError("DASHSCOPE_BASE_URL is not configured.")

        self.model = settings.qwen_model
        self.client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.dashscope_base_url,
        )

    async def summarize_chapter(self, chunk_summaries: list[str]) -> str:
        prompt = build_chapter_summary_prompt(chunk_summaries)
        logger.info(
            "Qwen chapter summary request started: model=%s chunk_summary_count=%s",
            self.model,
            len(chunk_summaries),
        )
        start_time = perf_counter()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You synthesize book chapter summaries accurately "
                            "and concisely."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
        except OpenAIError as error:
            logger.exception("Qwen chapter summary request failed.")
            raise SummaryGenerationError("Chapter summary request failed.") from error

        summary = response.choices[0].message.content
        if not summary:
            raise SummaryGenerationError("Chapter summary response was empty.")

        logger.info(
            "Qwen chapter summary response received: model=%s duration_ms=%s "
            "summary_preview=%s",
            self.model,
            round((perf_counter() - start_time) * 1000, 2),
            preview_text(summary),
        )
        return summary.strip()


class QwenBookSummaryClient:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.dashscope_api_key:
            raise SummaryGenerationError("DASHSCOPE_API_KEY is not configured.")
        if not settings.dashscope_base_url:
            raise SummaryGenerationError("DASHSCOPE_BASE_URL is not configured.")

        self.model = settings.qwen_model
        self.client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.dashscope_base_url,
        )

    async def summarize_book(self, chapter_summaries: list[str]) -> str:
        prompt = build_book_summary_prompt(chapter_summaries)
        logger.info(
            "Qwen book summary request started: model=%s chapter_summary_count=%s",
            self.model,
            len(chapter_summaries),
        )
        start_time = perf_counter()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You synthesize complete book summaries accurately "
                            "and concisely."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
        except OpenAIError as error:
            logger.exception("Qwen book summary request failed.")
            raise SummaryGenerationError("Book summary request failed.") from error

        summary = response.choices[0].message.content
        if not summary:
            raise SummaryGenerationError("Book summary response was empty.")

        logger.info(
            "Qwen book summary response received: model=%s duration_ms=%s "
            "summary_preview=%s",
            self.model,
            round((perf_counter() - start_time) * 1000, 2),
            preview_text(summary),
        )
        return summary.strip()
