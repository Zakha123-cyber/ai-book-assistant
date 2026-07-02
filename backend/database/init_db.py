import asyncio
import logging

from database.base import Base
from database.session import engine
from models import Book, Chapter, ChatHistory, Chunk, Summary, SystemProfile

logger = logging.getLogger(__name__)


async def init_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    await engine.dispose()

    model_names = [
        Book.__tablename__,
        Chapter.__tablename__,
        Chunk.__tablename__,
        Summary.__tablename__,
        ChatHistory.__tablename__,
        SystemProfile.__tablename__,
    ]
    logger.info("Database schema initialized for tables: %s", ", ".join(model_names))


if __name__ == "__main__":
    try:
        asyncio.run(init_database())
    except Exception as error:
        raise SystemExit(f"Failed to initialize database schema: {error}") from None
