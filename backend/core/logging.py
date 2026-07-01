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
