import logging
from dataclasses import dataclass

from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection

from database.chroma import get_chroma_client
from services.embedding.chunk_embedding import ChunkEmbedding

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_COLLECTION = "book_chunks"
DEFAULT_TOP_K = 5


@dataclass(frozen=True)
class RetrievedChunk:
    id: str
    document: str
    metadata: dict[str, int | str]
    distance: float | None = None


class ChromaChunkStore:
    def __init__(
        self,
        client: ClientAPI | None = None,
        collection_name: str = DEFAULT_CHUNK_COLLECTION,
    ) -> None:
        self.client = client or get_chroma_client()
        self.collection_name = collection_name

    def upsert_chunk_embeddings(
        self,
        chunk_embeddings: list[ChunkEmbedding],
    ) -> None:
        if not chunk_embeddings:
            return

        collection = self._get_collection()
        collection.upsert(
            ids=[self._document_id(item) for item in chunk_embeddings],
            embeddings=[item.embedding for item in chunk_embeddings],
            documents=[item.chunk.text for item in chunk_embeddings],
            metadatas=[item.chunk.metadata for item in chunk_embeddings],
        )
        logger.info(
            "Stored chunk embeddings in ChromaDB: collection=%s count=%s",
            self.collection_name,
            len(chunk_embeddings),
        )

    def query_by_embedding(
        self,
        query_embedding: list[float],
        book_id: str,
        top_k: int = DEFAULT_TOP_K,
    ) -> list[RetrievedChunk]:
        collection = self._get_collection()
        result = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"book_id": book_id},
            include=["documents", "metadatas", "distances"],
        )

        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        return [
            RetrievedChunk(
                id=item_id,
                document=document,
                metadata=metadata,
                distance=distance,
            )
            for item_id, document, metadata, distance in zip(
                ids,
                documents,
                metadatas,
                distances,
            )
        ]

    def _get_collection(self) -> Collection:
        return self.client.get_or_create_collection(name=self.collection_name)

    def _document_id(self, item: ChunkEmbedding) -> str:
        book_id = item.chunk.metadata.get("book_id", "unknown-book")
        chunk_id = item.chunk.metadata.get("chunk_id", item.chunk.chunk_id)
        return f"{book_id}:{chunk_id}"
