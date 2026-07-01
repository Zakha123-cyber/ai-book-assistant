import logging
import sys

from core.config import get_settings


def setup_logging() -> None:
    settings = get_settings()
    log_level = settings.log_level.upper()

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    logging.getLogger("uvicorn.access").setLevel(log_level)


def preview_text(value: str, limit: int = 240) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[:limit].rstrip()}..."
