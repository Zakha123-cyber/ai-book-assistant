import logging
from typing import Protocol

from services.retriever.chroma_store import (
    DEFAULT_TOP_K,
    ChromaChunkStore,
    RetrievedChunk,
)

logger = logging.getLogger(__name__)


class SimilaritySearchError(ValueError):
    pass


class ChunkVectorStore(Protocol):
    def query_by_embedding(
        self,
        query_embedding: list[float],
        book_id: str,
        top_k: int = DEFAULT_TOP_K,
    ) -> list[RetrievedChunk]:
        pass


def search_similar_chunks(
    query_embedding: list[float],
    book_id: str,
    top_k: int = DEFAULT_TOP_K,
    store: ChunkVectorStore | None = None,
) -> list[RetrievedChunk]:
    normalized_book_id = book_id.strip()
    if not normalized_book_id:
        raise SimilaritySearchError("Book ID cannot be empty.")
    if not query_embedding:
        raise SimilaritySearchError("Query embedding cannot be empty.")
    if top_k <= 0:
        raise SimilaritySearchError("top_k must be greater than zero.")

    vector_store = store or ChromaChunkStore()
    results = vector_store.query_by_embedding(
        query_embedding=query_embedding,
        book_id=normalized_book_id,
        top_k=top_k,
    )
    logger.info(
        "Similarity search completed: book_id=%s top_k=%s result_count=%s "
        "top_distance=%s top_source=%s",
        normalized_book_id,
        top_k,
        len(results),
        results[0].distance if results else None,
        results[0].id if results else None,
    )
    return results
