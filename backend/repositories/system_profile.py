from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.system_profile import SystemProfile
from repositories.base import BaseRepository

DEFAULT_SYSTEM_PROFILE_KEY = "default"


class SystemProfileRepository(BaseRepository[SystemProfile]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SystemProfile)

    async def get_default(self) -> SystemProfile | None:
        result = await self.session.execute(
            select(SystemProfile).where(
                SystemProfile.profile_key == DEFAULT_SYSTEM_PROFILE_KEY
            )
        )
        return result.scalar_one_or_none()

    async def upsert_default(
        self,
        assistant_name: str,
        assistant_description: str,
        creator_name: str,
        creator_description: str,
    ) -> SystemProfile:
        profile = await self.get_default()
        if profile is None:
            return await self.add(
                SystemProfile(
                    profile_key=DEFAULT_SYSTEM_PROFILE_KEY,
                    assistant_name=assistant_name,
                    assistant_description=assistant_description,
                    creator_name=creator_name,
                    creator_description=creator_description,
                )
            )

        profile.assistant_name = assistant_name
        profile.assistant_description = assistant_description
        profile.creator_name = creator_name
        profile.creator_description = creator_description
        await self.session.flush()
        await self.session.refresh(profile)
        return profile
