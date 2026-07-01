import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from models import Chunk, Summary, SummaryLevel
from repositories import SummaryRepository
from services.summarizer.qwen_summary import QwenChunkSummaryClient


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

    for chunk in chunks:
        if use_cache:
            existing_summary = await _get_existing_chunk_summary(repository, chunk.id)
            if existing_summary is not None:
                results.append(
                    ChunkSummaryResult(
                        chunk_id=chunk.id,
                        summary=existing_summary.summary,
                        cached=True,
                    )
                )
                continue

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
