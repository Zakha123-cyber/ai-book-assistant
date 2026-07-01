from dataclasses import dataclass
import logging
import re
from typing import Protocol

from core.logging import preview_text
from services.embedding import generate_question_embedding
from services.qa.context_builder import SourceReference, build_retrieved_context
from services.qa.qwen_qa import QwenQAService
from services.retriever import RetrievedChunk, search_similar_chunks
from services.retriever.chroma_store import DEFAULT_TOP_K

ANSWER_NOT_FOUND = "I could not find that information inside this book."
DEFAULT_MAX_RETRIEVAL_DISTANCE = 1.0
MIN_LEXICAL_MATCHES = 2
STOPWORDS = {
    "a",
    "about",
    "apa",
    "apakah",
    "are",
    "dalam",
    "di",
    "in",
    "ini",
    "is",
    "itu",
    "kah",
    "siapa",
    "siapakah",
    "the",
    "this",
    "who",
    "what",
    "yang",
}
WORD_PATTERN = re.compile(r"[a-zA-Z0-9]+")
logger = logging.getLogger(__name__)


class EmbeddingService(Protocol):
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        pass


class VectorStore(Protocol):
    def query_by_embedding(
        self,
        query_embedding: list[float],
        book_id: str,
        top_k: int = DEFAULT_TOP_K,
    ) -> list[RetrievedChunk]:
        pass


class QAAnswerService(Protocol):
    async def answer_question(self, question: str, retrieved_context: str) -> str:
        pass


@dataclass(frozen=True)
class ChatAnswer:
    answer: str
    sources: list[SourceReference]


async def answer_book_question(
    book_id: str,
    question: str,
    top_k: int = DEFAULT_TOP_K,
    max_retrieval_distance: float = DEFAULT_MAX_RETRIEVAL_DISTANCE,
    embedding_service: EmbeddingService | None = None,
    vector_store: VectorStore | None = None,
    qa_service: QAAnswerService | None = None,
) -> ChatAnswer:
    if max_retrieval_distance <= 0:
        raise ValueError("max_retrieval_distance must be greater than zero.")

    logger.info(
        "Chat retrieval QA started: book_id=%s top_k=%s question=%s",
        book_id,
        top_k,
        preview_text(question),
    )
    query_embedding = await generate_question_embedding(
        question,
        embedding_service=embedding_service,
    )
    logger.info(
        "Question embedding generated: book_id=%s dimension=%s sample=%s",
        book_id,
        len(query_embedding),
        query_embedding[:5],
    )
    chunks = search_similar_chunks(
        query_embedding=query_embedding,
        book_id=book_id,
        top_k=top_k,
        store=vector_store,
    )
    if not _has_confident_match(chunks, question, max_retrieval_distance):
        logger.info(
            "Retrieval guard rejected context: book_id=%s top_distance=%s "
            "threshold=%s top_source=%s",
            book_id,
            chunks[0].distance if chunks else None,
            max_retrieval_distance,
            chunks[0].id if chunks else None,
        )
        return ChatAnswer(answer=ANSWER_NOT_FOUND, sources=[])

    retrieved_context = build_retrieved_context(chunks)
    if not retrieved_context.context:
        logger.info("Retrieved context empty: book_id=%s", book_id)
        return ChatAnswer(answer=ANSWER_NOT_FOUND, sources=[])
    logger.info(
        "Retrieved context built: book_id=%s source_count=%s context_chars=%s "
        "preview=%s",
        book_id,
        len(retrieved_context.sources),
        len(retrieved_context.context),
        preview_text(retrieved_context.context),
    )

    service = qa_service or QwenQAService()
    answer = await service.answer_question(
        question=question,
        retrieved_context=retrieved_context.context,
    )
    logger.info(
        "Chat retrieval QA completed: book_id=%s answer_preview=%s source_count=%s",
        book_id,
        preview_text(answer),
        0 if _is_not_found_answer(answer) else len(retrieved_context.sources),
    )
    return ChatAnswer(
        answer=answer,
        sources=[] if _is_not_found_answer(answer) else retrieved_context.sources,
    )


def _has_confident_match(
    chunks: list[RetrievedChunk],
    question: str,
    max_retrieval_distance: float,
) -> bool:
    if not chunks:
        return False

    top_distance = chunks[0].distance
    if top_distance is None:
        return False

    lexical_support = _has_lexical_support(question, chunks[0])
    accepted = top_distance <= max_retrieval_distance or lexical_support
    logger.info(
        "Retrieval guard evaluated: top_distance=%s threshold=%s "
        "lexical_support=%s accepted=%s top_source=%s",
        top_distance,
        max_retrieval_distance,
        lexical_support,
        accepted,
        chunks[0].id,
    )
    return accepted


def _has_lexical_support(question: str, chunk: RetrievedChunk) -> bool:
    keywords = _extract_keywords(question)
    if len(keywords) < MIN_LEXICAL_MATCHES:
        return False

    haystack = _source_text(chunk)
    matched_keywords = {keyword for keyword in keywords if keyword in haystack}
    return len(matched_keywords) >= MIN_LEXICAL_MATCHES


def _extract_keywords(text: str) -> set[str]:
    words = {
        word
        for word in WORD_PATTERN.findall(text.casefold())
        if len(word) > 2 and word not in STOPWORDS
    }
    return words


def _source_text(chunk: RetrievedChunk) -> str:
    metadata_text = " ".join(str(value) for value in chunk.metadata.values())
    return f"{chunk.document} {metadata_text}".casefold()


def _is_not_found_answer(answer: str) -> bool:
    normalized_answer = " ".join(answer.casefold().split())
    return ANSWER_NOT_FOUND.casefold() in normalized_answer
