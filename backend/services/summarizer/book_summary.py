import uuid
from dataclasses import dataclass
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from models import Book, Summary, SummaryLevel
from repositories import ChapterRepository, SummaryRepository
from services.summarizer.qwen_summary import QwenBookSummaryClient


class BookSummaryClient(Protocol):
    async def summarize_book(self, chapter_summaries: list[str]) -> str:
        pass


class MissingChapterSummariesError(ValueError):
    def __init__(
        self,
        book_id: uuid.UUID,
        missing_count: int,
        total_count: int,
    ) -> None:
        self.book_id = book_id
        self.missing_count = missing_count
        self.total_count = total_count
        super().__init__(
            "Missing chapter summaries for book "
            f"{book_id}: {missing_count}/{total_count}"
        )


@dataclass(frozen=True)
class BookSummaryResult:
    book_id: uuid.UUID
    book_title: str
    summary: str
    chapter_summary_count: int
    cached: bool = False


async def summarize_book_from_chapter_summaries(
    chapter_summaries: list[str],
    client: BookSummaryClient | None = None,
) -> str:
    summary_client = client or QwenBookSummaryClient()
    return await summary_client.summarize_book(chapter_summaries)


async def summarize_and_store_book(
    session: AsyncSession,
    book: Book,
    client: BookSummaryClient | None = None,
    use_cache: bool = True,
) -> BookSummaryResult:
    summary_client = client or QwenBookSummaryClient()
    summary_repository = SummaryRepository(session)
    chapter_repository = ChapterRepository(session)

    if use_cache:
        existing_summary = await _get_existing_book_summary(
            summary_repository,
            book.id,
        )
        if existing_summary is not None:
            chapter_summary_count = await _count_existing_chapter_summaries(
                chapter_repository,
                summary_repository,
                book,
            )
            return BookSummaryResult(
                book_id=book.id,
                book_title=book.title,
                summary=existing_summary.summary,
                chapter_summary_count=chapter_summary_count,
                cached=True,
            )

    chapter_summaries = await _get_complete_chapter_summaries(
        chapter_repository,
        summary_repository,
        book,
    )
    summary_text = await summary_client.summarize_book(chapter_summaries)
    await summary_repository.add(
        Summary(
            level=SummaryLevel.BOOK,
            reference_id=book.id,
            summary=summary_text,
        )
    )
    return BookSummaryResult(
        book_id=book.id,
        book_title=book.title,
        summary=summary_text,
        chapter_summary_count=len(chapter_summaries),
        cached=False,
    )


async def _get_existing_book_summary(
    repository: SummaryRepository,
    book_id: uuid.UUID,
) -> Summary | None:
    summaries = await repository.list_by_reference(
        reference_id=book_id,
        level=SummaryLevel.BOOK,
    )
    return summaries[0] if summaries else None


async def _get_complete_chapter_summaries(
    chapter_repository: ChapterRepository,
    summary_repository: SummaryRepository,
    book: Book,
) -> list[str]:
    chapters = list(await chapter_repository.list_by_book_id(book.id))
    summaries: list[str] = []
    missing_count = 0

    for chapter in chapters:
        chapter_summary = await _get_first_summary(
            summary_repository,
            chapter.id,
            SummaryLevel.CHAPTER,
        )
        if chapter_summary is None:
            missing_count += 1
            continue
        summaries.append(chapter_summary.summary)

    if missing_count > 0 or not chapters:
        raise MissingChapterSummariesError(
            book_id=book.id,
            missing_count=missing_count if chapters else 1,
            total_count=len(chapters),
        )

    return summaries


async def _count_existing_chapter_summaries(
    chapter_repository: ChapterRepository,
    summary_repository: SummaryRepository,
    book: Book,
) -> int:
    chapters = list(await chapter_repository.list_by_book_id(book.id))
    count = 0
    for chapter in chapters:
        summary = await _get_first_summary(
            summary_repository,
            chapter.id,
            SummaryLevel.CHAPTER,
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
