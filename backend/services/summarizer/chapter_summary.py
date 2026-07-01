import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from models import Chapter, Summary, SummaryLevel
from repositories import ChunkRepository, SummaryRepository
from services.summarizer.qwen_summary import QwenChapterSummaryClient


class ChapterSummaryClient(Protocol):
    async def summarize_chapter(self, chunk_summaries: list[str]) -> str:
        pass


class MissingChunkSummariesError(ValueError):
    def __init__(
        self,
        chapter_id: uuid.UUID,
        chapter_title: str,
        missing_count: int,
        total_count: int,
    ) -> None:
        self.chapter_id = chapter_id
        self.chapter_title = chapter_title
        self.missing_count = missing_count
        self.total_count = total_count
        super().__init__(
            "Missing chunk summaries for chapter "
            f"{chapter_title} ({chapter_id}): {missing_count}/{total_count}"
        )


@dataclass(frozen=True)
class ChapterSummaryResult:
    chapter_id: uuid.UUID
    chapter_title: str
    summary: str
    chunk_summary_count: int
    cached: bool = False


async def summarize_chapter_from_chunk_summaries(
    chunk_summaries: list[str],
    client: ChapterSummaryClient | None = None,
) -> str:
    summary_client = client or QwenChapterSummaryClient()
    return await summary_client.summarize_chapter(chunk_summaries)


async def summarize_and_store_chapters(
    session: AsyncSession,
    chapters: Sequence[Chapter],
    client: ChapterSummaryClient | None = None,
    use_cache: bool = True,
) -> list[ChapterSummaryResult]:
    summary_client = client or QwenChapterSummaryClient()
    summary_repository = SummaryRepository(session)
    chunk_repository = ChunkRepository(session)
    results: list[ChapterSummaryResult] = []

    for chapter in chapters:
        if use_cache:
            existing_summary = await _get_existing_chapter_summary(
                summary_repository,
                chapter.id,
            )
            if existing_summary is not None:
                chunk_summary_count = await _count_existing_chunk_summaries(
                    chunk_repository,
                    summary_repository,
                    chapter,
                )
                results.append(
                    ChapterSummaryResult(
                        chapter_id=chapter.id,
                        chapter_title=chapter.title,
                        summary=existing_summary.summary,
                        chunk_summary_count=chunk_summary_count,
                        cached=True,
                    )
                )
                continue

        chunk_summaries = await _get_complete_chunk_summaries(
            chunk_repository,
            summary_repository,
            chapter,
        )
        summary_text = await summary_client.summarize_chapter(chunk_summaries)
        await summary_repository.add(
            Summary(
                level=SummaryLevel.CHAPTER,
                reference_id=chapter.id,
                summary=summary_text,
            )
        )
        results.append(
            ChapterSummaryResult(
                chapter_id=chapter.id,
                chapter_title=chapter.title,
                summary=summary_text,
                chunk_summary_count=len(chunk_summaries),
                cached=False,
            )
        )

    return results


async def _get_existing_chapter_summary(
    repository: SummaryRepository,
    chapter_id: uuid.UUID,
) -> Summary | None:
    summaries = await repository.list_by_reference(
        reference_id=chapter_id,
        level=SummaryLevel.CHAPTER,
    )
    return summaries[0] if summaries else None


async def _get_complete_chunk_summaries(
    chunk_repository: ChunkRepository,
    summary_repository: SummaryRepository,
    chapter: Chapter,
) -> list[str]:
    chunks = list(await chunk_repository.list_by_chapter_id(chapter.id))
    summaries: list[str] = []
    missing_count = 0

    for chunk in chunks:
        chunk_summary = await _get_first_summary(
            summary_repository,
            chunk.id,
            SummaryLevel.CHUNK,
        )
        if chunk_summary is None:
            missing_count += 1
            continue
        summaries.append(chunk_summary.summary)

    if missing_count > 0 or not chunks:
        raise MissingChunkSummariesError(
            chapter_id=chapter.id,
            chapter_title=chapter.title,
            missing_count=missing_count if chunks else 1,
            total_count=len(chunks),
        )

    return summaries


async def _count_existing_chunk_summaries(
    chunk_repository: ChunkRepository,
    summary_repository: SummaryRepository,
    chapter: Chapter,
) -> int:
    chunks = list(await chunk_repository.list_by_chapter_id(chapter.id))
    count = 0
    for chunk in chunks:
        summary = await _get_first_summary(
            summary_repository,
            chunk.id,
            SummaryLevel.CHUNK,
        )
        if summary is not None:
            count += 1
    return count


async def _get_first_summary(
    repository: SummaryRepository,
    reference_id: uuid.UUID,
    level: SummaryLevel,
) -> Summary | None:
    summaries = await repository.list_by_reference(
        reference_id=reference_id,
        level=level,
    )
    return summaries[0] if summaries else None
