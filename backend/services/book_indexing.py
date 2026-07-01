import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from models import Book, Chapter, Chunk
from repositories import BookRepository, ChapterRepository, ChunkRepository
from services.chunker.chapter_detector import DetectedChapter
from services.chunker.semantic_chunker import SemanticChunk


async def persist_book_metadata(
    session: AsyncSession,
    original_filename: str,
    stored_path: Path,
    chapters: list[DetectedChapter],
    chunks: list[SemanticChunk],
) -> Book:
    book_repository = BookRepository(session)
    chapter_repository = ChapterRepository(session)
    chunk_repository = ChunkRepository(session)

    book = await book_repository.add(
        Book(
            title=_title_from_filename(original_filename),
            author=None,
            filename=str(stored_path),
        )
    )

    chapter_ids = await _persist_chapters(chapter_repository, book.id, chapters)
    await _persist_chunks(chunk_repository, chapter_ids, chunks)
    return book


async def _persist_chapters(
    chapter_repository: ChapterRepository,
    book_id: uuid.UUID,
    chapters: list[DetectedChapter],
) -> dict[int, uuid.UUID]:
    chapter_ids: dict[int, uuid.UUID] = {}
    for detected_chapter in chapters:
        chapter = await chapter_repository.add(
            Chapter(
                book_id=book_id,
                number=detected_chapter.number,
                title=detected_chapter.title,
                summary=None,
            )
        )
        chapter_ids[detected_chapter.number] = chapter.id

    return chapter_ids


async def _persist_chunks(
    chunk_repository: ChunkRepository,
    chapter_ids: dict[int, uuid.UUID],
    chunks: list[SemanticChunk],
) -> None:
    for semantic_chunk in chunks:
        chapter_id = chapter_ids[semantic_chunk.chapter_number]
        await chunk_repository.add(
            Chunk(
                chapter_id=chapter_id,
                chunk_index=semantic_chunk.chunk_index,
                content=semantic_chunk.text,
            )
        )


def _title_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    return stem.replace("_", " ").replace("-", " ").strip() or "Untitled Book"

