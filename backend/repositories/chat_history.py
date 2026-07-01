import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.chat_history import ChatHistory
from repositories.base import BaseRepository


class ChatHistoryRepository(BaseRepository[ChatHistory]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ChatHistory)

    async def list_by_book_id(self, book_id: uuid.UUID) -> Sequence[ChatHistory]:
        result = await self.session.execute(
            select(ChatHistory)
            .where(ChatHistory.book_id == book_id)
            .order_by(ChatHistory.created_at.asc())
        )
        return result.scalars().all()

