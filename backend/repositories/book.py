from sqlalchemy.ext.asyncio import AsyncSession

from models.book import Book
from repositories.base import BaseRepository


class BookRepository(BaseRepository[Book]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Book)

