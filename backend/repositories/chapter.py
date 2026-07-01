import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.chapter import Chapter
from repositories.base import BaseRepository


class ChapterRepository(BaseRepository[Chapter]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Chapter)

    async def list_by_book_id(self, book_id: uuid.UUID) -> Sequence[Chapter]:
        result = await self.session.execute(
            select(Chapter)
            .where(Chapter.book_id == book_id)
            .order_by(Chapter.number.asc())
        )
        return result.scalars().all()

