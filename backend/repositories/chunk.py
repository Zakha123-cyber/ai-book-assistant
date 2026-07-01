import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.chapter import Chapter
from models.chunk import Chunk
from repositories.base import BaseRepository


class ChunkRepository(BaseRepository[Chunk]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Chunk)

    async def list_by_chapter_id(self, chapter_id: uuid.UUID) -> Sequence[Chunk]:
        result = await self.session.execute(
            select(Chunk)
            .where(Chunk.chapter_id == chapter_id)
            .order_by(Chunk.chunk_index.asc())
        )
        return result.scalars().all()

    async def list_by_book_id(self, book_id: uuid.UUID) -> Sequence[Chunk]:
        result = await self.session.execute(
            select(Chunk)
            .join(Chapter, Chunk.chapter_id == Chapter.id)
            .where(Chapter.book_id == book_id)
            .order_by(Chapter.number.asc(), Chunk.chunk_index.asc())
        )
        return result.scalars().all()
