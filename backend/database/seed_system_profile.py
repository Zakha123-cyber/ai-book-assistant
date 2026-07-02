import asyncio

from core.config import get_settings
from database.session import async_session_factory, engine
from repositories import SystemProfileRepository


async def seed_system_profile() -> None:
    settings = get_settings()
    async with async_session_factory() as session:
        profile = await SystemProfileRepository(session).upsert_default(
            assistant_name=settings.app_assistant_name,
            assistant_description=settings.app_assistant_description,
            creator_name=settings.app_creator_name or "Unknown creator",
            creator_description=(
                settings.app_creator_description
                or "Creator description has not been configured."
            ),
        )
        await session.commit()

    await engine.dispose()
    print(f"System profile seeded: id={profile.id} key={profile.profile_key}")


if __name__ == "__main__":
    asyncio.run(seed_system_profile())
