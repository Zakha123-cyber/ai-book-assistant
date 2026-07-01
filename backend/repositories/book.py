from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.book import Book
from repositories.base import BaseRepository


class BookRepository(BaseRepository[Book]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Book)

    async def list_recent(self) -> Sequence[Book]:
        result = await self.session.execute(
            select(Book).order_by(Book.uploaded_at.desc())
        )
        return result.scalars().all()
