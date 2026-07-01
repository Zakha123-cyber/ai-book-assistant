from dataclasses import dataclass
import logging

from services.chunker.semantic_chunker import SemanticChunk
from services.embedding.dashscope_embedding import DashScopeEmbeddingService

DEFAULT_EMBEDDING_BATCH_SIZE = 10
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ChunkEmbedding:
    chunk: SemanticChunk
    embedding: list[float]


async def generate_chunk_embeddings(
    chunks: list[SemanticChunk],
    embedding_service: DashScopeEmbeddingService | None = None,
    batch_size: int = DEFAULT_EMBEDDING_BATCH_SIZE,
) -> list[ChunkEmbedding]:
    if not chunks:
        return []

    service = embedding_service or DashScopeEmbeddingService()
    chunk_embeddings: list[ChunkEmbedding] = []
    batches = _batch_chunks(chunks, batch_size)
    logger.info(
        "Chunk embedding started: chunk_count=%s batch_size=%s batch_count=%s",
        len(chunks),
        batch_size,
        len(batches),
    )

    for batch_index, batch in enumerate(batches, start=1):
        logger.info(
            "Embedding batch started: batch=%s/%s size=%s first_chunk=%s",
            batch_index,
            len(batches),
            len(batch),
            batch[0].chunk_id if batch else None,
        )
        vectors = await service.embed_texts([chunk.text for chunk in batch])
        chunk_embeddings.extend(
            ChunkEmbedding(chunk=chunk, embedding=vector)
            for chunk, vector in zip(batch, vectors, strict=True)
        )
        logger.info(
            "Embedding batch completed: batch=%s/%s vector_count=%s dimension=%s",
            batch_index,
            len(batches),
            len(vectors),
            len(vectors[0]) if vectors else 0,
        )

    logger.info("Chunk embedding completed: embedding_count=%s", len(chunk_embeddings))
    return chunk_embeddings


def _batch_chunks(
    chunks: list[SemanticChunk],
    batch_size: int,
) -> list[list[SemanticChunk]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero.")

    return [
        chunks[index : index + batch_size]
        for index in range(0, len(chunks), batch_size)
    ]
