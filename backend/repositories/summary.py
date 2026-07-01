import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.summary import Summary, SummaryLevel
from repositories.base import BaseRepository


class SummaryRepository(BaseRepository[Summary]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Summary)

    async def list_by_reference(
        self,
        reference_id: uuid.UUID,
        level: SummaryLevel | None = None,
    ) -> Sequence[Summary]:
        query = select(Summary).where(Summary.reference_id == reference_id)
        if level is not None:
            query = query.where(Summary.level == level)

        result = await self.session.execute(query)
        return result.scalars().all()

