import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import preview_text
from models import ChatHistory, SummaryLevel
from repositories import (
    BookRepository,
    ChapterRepository,
    ChatHistoryRepository,
    SummaryRepository,
    SystemProfileRepository,
)
from services.qa.app_identity import (
    build_app_identity_context,
    detect_app_identity_question,
)
from services.qa.chat_pipeline import ANSWER_NOT_FOUND, answer_book_question
from services.qa.chat_graph_state import ChatGraphState
from services.qa.qwen_qa import QwenQAService
from services.qa.question_router import route_question
from services.qa.context_builder import SourceReference
from services.qa.question_router import QuestionMode

logger = logging.getLogger(__name__)


class ChatGraphBookNotFoundError(ValueError):
    pass


class ChatGraphSummaryNotFoundError(ValueError):
    pass


class ChatGraphSystemProfileNotFoundError(ValueError):
    pass


async def validate_book_node(
    state: ChatGraphState,
    session: AsyncSession,
) -> ChatGraphState:
    book_id = state["book_id"]
    book = await BookRepository(session).get_by_id(book_id)
    if book is None:
        logger.info("LangGraph node validate_book: book not found book_id=%s", book_id)
        raise ChatGraphBookNotFoundError("Book not found.")

    logger.info(
        "LangGraph node validate_book: book_id=%s title=%s question=%s",
        book_id,
        book.title,
        preview_text(state.get("normalized_question") or state.get("question", "")),
    )
    return {
        **state,
        "book": book,
    }


async def detect_identity_node(
    state: ChatGraphState,
    session: AsyncSession,
) -> ChatGraphState:
    question = state.get("normalized_question") or state.get("question", "")
    identity_route = detect_app_identity_question(question)
    system_profile = None

    if identity_route is None:
        system_profile = await SystemProfileRepository(session).get_default()
        if system_profile is not None:
            identity_route = detect_app_identity_question(
                question,
                profile=system_profile,
            )

    if identity_route is None:
        logger.info(
            "LangGraph node detect_identity: no identity route book_id=%s question=%s",
            state["book_id"],
            preview_text(question),
        )
        return state

    if system_profile is None:
        system_profile = await SystemProfileRepository(session).get_default()
        if system_profile is None:
            logger.info(
                "LangGraph node detect_identity: system profile missing book_id=%s",
                state["book_id"],
            )
            raise ChatGraphSystemProfileNotFoundError("System profile not configured.")

    identity_context = build_app_identity_context(system_profile, identity_route)
    logger.info(
        "LangGraph node detect_identity: book_id=%s mode=%s context_chars=%s",
        state["book_id"],
        identity_route.mode.value,
        len(identity_context),
    )
    return {
        **state,
        "identity_route": identity_route,
        "identity_context": identity_context,
        "response_mode": "app_identity",
    }


async def route_question_node(state: ChatGraphState) -> ChatGraphState:
    if state.get("identity_context"):
        logger.info(
            "LangGraph node route_question: skipped for identity book_id=%s",
            state["book_id"],
        )
        return state

    question = state.get("normalized_question") or state.get("question", "")
    question_route = route_question(question)
    logger.info(
        "LangGraph node route_question: book_id=%s mode=%s chapter=%s question=%s",
        state["book_id"],
        question_route.mode.value,
        question_route.chapter_number,
        preview_text(question),
    )
    if question_route.mode == QuestionMode.OUT_OF_SCOPE:
        return {
            **state,
            "question_route": question_route,
            "answer": ANSWER_NOT_FOUND,
            "sources": [],
            "message": "Question is outside the scope of this book.",
            "response_mode": question_route.mode.value,
        }

    return {
        **state,
        "question_route": question_route,
        "response_mode": question_route.mode.value,
    }


async def resolve_summary_context_node(
    state: ChatGraphState,
    session: AsyncSession,
) -> ChatGraphState:
    if state.get("identity_context"):
        logger.info(
            "LangGraph node resolve_summary_context: skipped for identity book_id=%s",
            state["book_id"],
        )
        return state

    question_route = state.get("question_route")
    if question_route is None or question_route.mode not in {
        QuestionMode.BOOK_SUMMARY,
        QuestionMode.CHAPTER_SUMMARY,
    }:
        logger.info(
            "LangGraph node resolve_summary_context: skipped book_id=%s",
            state["book_id"],
        )
        return state

    if question_route.mode == QuestionMode.BOOK_SUMMARY:
        summary_context, sources = await _get_book_summary_context(
            session=session,
            state=state,
        )
    else:
        summary_context, sources = await _get_chapter_summary_context(
            session=session,
            state=state,
        )

    logger.info(
        "LangGraph node resolve_summary_context: book_id=%s mode=%s "
        "context_chars=%s source_count=%s",
        state["book_id"],
        question_route.mode.value,
        len(summary_context),
        len(sources),
    )
    return {
        **state,
        "summary_context": summary_context,
        "sources": sources,
    }


async def _get_book_summary_context(
    session: AsyncSession,
    state: ChatGraphState,
) -> tuple[str, list[SourceReference]]:
    summaries = await SummaryRepository(session).list_by_reference(
        reference_id=state["book_id"],
        level=SummaryLevel.BOOK,
    )
    if not summaries:
        raise ChatGraphSummaryNotFoundError("Book summary not found.")

    return (
        f"[Book Summary]\n{summaries[0].summary}",
        [
            SourceReference(
                chunk_id="book-summary",
                chapter=None,
                chapter_title=None,
                page_start=None,
                page_end=None,
                distance=None,
            )
        ],
    )


async def _get_chapter_summary_context(
    session: AsyncSession,
    state: ChatGraphState,
) -> tuple[str, list[SourceReference]]:
    question_route = state["question_route"]
    if question_route.chapter_number is None:
        raise ChatGraphSummaryNotFoundError("Chapter summary not found.")

    chapters = await ChapterRepository(session).list_by_book_id(state["book_id"])
    chapter = next(
        (item for item in chapters if item.number == question_route.chapter_number),
        None,
    )
    if chapter is None:
        raise ChatGraphSummaryNotFoundError("Chapter not found.")

    summaries = await SummaryRepository(session).list_by_reference(
        reference_id=chapter.id,
        level=SummaryLevel.CHAPTER,
    )
    if not summaries:
        raise ChatGraphSummaryNotFoundError("Chapter summary not found.")

    return (
        f"[Chapter Summary] Chapter {chapter.number}: {chapter.title}\n"
        f"{summaries[0].summary}",
        [
            SourceReference(
                chunk_id=f"chapter-summary:{chapter.id}",
                chapter=chapter.number,
                chapter_title=chapter.title,
                page_start=None,
                page_end=None,
                distance=None,
            )
        ],
    )


async def run_retrieval_qa_node(state: ChatGraphState) -> ChatGraphState:
    if state.get("identity_context") or state.get("summary_context"):
        logger.info(
            "LangGraph node run_retrieval_qa: skipped existing context book_id=%s",
            state["book_id"],
        )
        return state

    question_route = state.get("question_route")
    if question_route is None or question_route.mode != QuestionMode.RETRIEVAL_QA:
        logger.info(
            "LangGraph node run_retrieval_qa: skipped book_id=%s mode=%s",
            state["book_id"],
            question_route.mode.value if question_route else None,
        )
        return state

    result = await answer_book_question(
        book_id=str(state["book_id"]),
        question=state.get("normalized_question") or state["question"],
        top_k=state["top_k"],
    )
    logger.info(
        "LangGraph node run_retrieval_qa: book_id=%s source_count=%s "
        "answer_preview=%s",
        state["book_id"],
        len(result.sources),
        preview_text(result.answer),
    )
    return {
        **state,
        "answer": result.answer,
        "sources": result.sources,
        "message": "Chat answer generated successfully.",
        "response_mode": QuestionMode.RETRIEVAL_QA.value,
    }


async def generate_identity_or_summary_answer_node(
    state: ChatGraphState,
) -> ChatGraphState:
    if state.get("answer"):
        logger.info(
            "LangGraph node generate_identity_or_summary_answer: skipped "
            "existing answer book_id=%s",
            state["book_id"],
        )
        return state

    context = state.get("identity_context") or state.get("summary_context")
    if not context:
        logger.info(
            "LangGraph node generate_identity_or_summary_answer: skipped no context "
            "book_id=%s",
            state["book_id"],
        )
        return state

    answer = await QwenQAService().answer_question(
        question=state.get("normalized_question") or state["question"],
        retrieved_context=context,
    )
    if state.get("identity_context"):
        message = "Application identity answer generated successfully."
        response_mode = "app_identity"
        sources: list[SourceReference] = []
    else:
        message = "Summary answer generated successfully."
        response_mode = state.get("response_mode", "summary")
        sources = [] if _is_not_found_answer(answer) else state.get("sources", [])

    logger.info(
        "LangGraph node generate_identity_or_summary_answer: book_id=%s "
        "mode=%s source_count=%s answer_preview=%s",
        state["book_id"],
        response_mode,
        len(sources),
        preview_text(answer),
    )
    return {
        **state,
        "answer": answer,
        "sources": sources,
        "message": message,
        "response_mode": response_mode,
    }


def _is_not_found_answer(answer: str) -> bool:
    normalized_answer = " ".join(answer.casefold().split())
    return ANSWER_NOT_FOUND.casefold() in normalized_answer


async def persist_chat_history_node(
    state: ChatGraphState,
    session: AsyncSession,
) -> ChatGraphState:
    answer = state.get("answer")
    if not answer:
        logger.info(
            "LangGraph node persist_chat_history: skipped missing answer book_id=%s",
            state["book_id"],
        )
        return state

    await ChatHistoryRepository(session).add(
        ChatHistory(
            book_id=state["book_id"],
            question=state.get("normalized_question") or state["question"],
            answer=answer,
        )
    )
    logger.info(
        "LangGraph node persist_chat_history: book_id=%s answer_preview=%s",
        state["book_id"],
        preview_text(answer),
    )
    return state
