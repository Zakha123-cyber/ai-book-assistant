from dataclasses import dataclass

from services.chunker.semantic_chunker import SemanticChunk
from services.embedding.dashscope_embedding import DashScopeEmbeddingService

DEFAULT_EMBEDDING_BATCH_SIZE = 10


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

    for batch in _batch_chunks(chunks, batch_size):
        vectors = await service.embed_texts([chunk.text for chunk in batch])
        chunk_embeddings.extend(
            ChunkEmbedding(chunk=chunk, embedding=vector)
            for chunk, vector in zip(batch, vectors, strict=True)
        )

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
