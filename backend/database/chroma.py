from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.api import ClientAPI

from core.config import get_settings


@lru_cache
def get_chroma_client() -> ClientAPI:
    settings = get_settings()
    persist_path = Path(settings.chroma_persist_dir)
    persist_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(persist_path))
