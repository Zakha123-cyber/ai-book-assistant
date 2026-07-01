import uuid
from collections.abc import Sequence
from dataclasses import dataclass
import logging
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import preview_text
from models import Chunk, Summary, SummaryLevel
from repositories import SummaryRepository
from services.summarizer.qwen_summary import QwenChunkSummaryClient

logger = logging.getLogger(__name__)


class ChunkSummaryClient(Protocol):
    async def summarize_chunk(self, chunk_text: str) -> str:
        pass


@dataclass(frozen=True)
class ChunkSummaryResult:
    chunk_id: uuid.UUID
    summary: str
    cached: bool = False


async def summarize_chunks(
    chunks: Sequence[Chunk],
    client: ChunkSummaryClient | None = None,
) -> list[ChunkSummaryResult]:
    summary_client = client or QwenChunkSummaryClient()
    results: list[ChunkSummaryResult] = []

    for chunk in chunks:
        summary = await summary_client.summarize_chunk(chunk.content)
        results.append(
            ChunkSummaryResult(
                chunk_id=chunk.id,
                summary=summary,
                cached=False,
            )
        )

    return results


async def summarize_and_store_chunks(
    session: AsyncSession,
    chunks: Sequence[Chunk],
    client: ChunkSummaryClient | None = None,
    use_cache: bool = True,
) -> list[ChunkSummaryResult]:
    summary_client = client or QwenChunkSummaryClient()
    repository = SummaryRepository(session)
    results: list[ChunkSummaryResult] = []
    logger.info("Chunk summary persistence started: chunk_count=%s", len(chunks))

    for index, chunk in enumerate(chunks, start=1):
        if use_cache:
            existing_summary = await _get_existing_chunk_summary(repository, chunk.id)
            if existing_summary is not None:
                logger.info(
                    "Chunk summary cache hit: index=%s/%s chunk_id=%s preview=%s",
                    index,
                    len(chunks),
                    chunk.id,
                    preview_text(existing_summary.summary),
                )
                results.append(
                    ChunkSummaryResult(
                        chunk_id=chunk.id,
                        summary=existing_summary.summary,
                        cached=True,
                    )
                )
                continue

        logger.info(
            "Chunk summary generating: index=%s/%s chunk_id=%s content_preview=%s",
            index,
            len(chunks),
            chunk.id,
            preview_text(chunk.content),
        )
        summary_text = await summary_client.summarize_chunk(chunk.content)
        await repository.add(
            Summary(
                level=SummaryLevel.CHUNK,
                reference_id=chunk.id,
                summary=summary_text,
            )
        )
        results.append(
            ChunkSummaryResult(
                chunk_id=chunk.id,
                summary=summary_text,
                cached=False,
            )
        )
        logger.info(
            "Chunk summary stored: index=%s/%s chunk_id=%s summary_preview=%s",
            index,
            len(chunks),
            chunk.id,
            preview_text(summary_text),
        )

    logger.info("Chunk summary persistence completed: result_count=%s", len(results))
    return results


async def _get_existing_chunk_summary(
    repository: SummaryRepository,
    chunk_id: uuid.UUID,
) -> Summary | None:
    summaries = await repository.list_by_reference(
        reference_id=chunk_id,
        level=SummaryLevel.CHUNK,
    )
    return summaries[0] if summaries else None
