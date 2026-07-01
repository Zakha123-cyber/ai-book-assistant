import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from models import Book, SummaryLevel
from repositories import ChapterRepository, ChunkRepository, SummaryRepository


@dataclass(frozen=True)
class BookIndexingStatus:
    book_id: uuid.UUID
    embedding_ready: bool
    chunk_count: int
    chunk_summary_count: int
    chapter_count: int
    chapter_summary_count: int
    book_summary_ready: bool

    @property
    def chunk_summary_ready(self) -> bool:
        return self.chunk_count > 0 and self.chunk_summary_count >= self.chunk_count

    @property
    def chapter_summary_ready(self) -> bool:
        return (
            self.chapter_count > 0
            and self.chapter_summary_count >= self.chapter_count
        )

    @property
    def status(self) -> str:
        if self.book_summary_ready:
            return "ready"
        if self.chunk_summary_count > 0 or self.chapter_summary_count > 0:
            return "summarizing"
        if self.embedding_ready:
            return "embedding_ready"
        return "uploaded"


async def get_book_indexing_status(
    session: AsyncSession,
    book: Book,
) -> BookIndexingStatus:
    chapters = list(await ChapterRepository(session).list_by_book_id(book.id))
    chunks = list(await ChunkRepository(session).list_by_book_id(book.id))
    summary_repository = SummaryRepository(session)

    chunk_summary_count = 0
    for chunk in chunks:
        summaries = await summary_repository.list_by_reference(
            reference_id=chunk.id,
            level=SummaryLevel.CHUNK,
        )
        if summaries:
            chunk_summary_count += 1

    chapter_summary_count = 0
    for chapter in chapters:
        summaries = await summary_repository.list_by_reference(
            reference_id=chapter.id,
            level=SummaryLevel.CHAPTER,
        )
        if summaries:
            chapter_summary_count += 1

    book_summaries = await summary_repository.list_by_reference(
        reference_id=book.id,
        level=SummaryLevel.BOOK,
    )

    return BookIndexingStatus(
        book_id=book.id,
        embedding_ready=bool(chunks),
        chunk_count=len(chunks),
        chunk_summary_count=chunk_summary_count,
        chapter_count=len(chapters),
        chapter_summary_count=chapter_summary_count,
        book_summary_ready=bool(book_summaries),
    )
