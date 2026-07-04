import logging
import uuid
from collections.abc import Awaitable, Callable
from functools import lru_cache
from time import perf_counter

from langgraph.graph import END, StateGraph

from database.session import async_session_factory
from services.qa.question_router import QuestionMode
from services.qa.chat_graph_nodes import (
    detect_identity_node,
    generate_identity_or_summary_answer_node,
    persist_chat_history_node,
    resolve_summary_context_node,
    route_question_node,
    run_retrieval_qa_node,
    validate_book_node,
)
from services.qa.chat_graph_state import ChatGraphState

logger = logging.getLogger(__name__)


async def run_chat_graph(
    book_id: uuid.UUID,
    question: str,
    top_k: int,
) -> ChatGraphState:
    graph = _build_chat_graph()
    initial_state: ChatGraphState = {
        "book_id": book_id,
        "question": question,
        "normalized_question": question.strip(),
        "top_k": top_k,
        "sources": [],
    }
    logger.info(
        "LangGraph chat workflow started: book_id=%s top_k=%s",
        book_id,
        top_k,
    )
    final_state = await graph.ainvoke(initial_state)
    logger.info(
        "LangGraph chat workflow finished: book_id=%s mode=%s source_count=%s",
        book_id,
        final_state.get("response_mode"),
        len(final_state.get("sources", [])),
    )
    return final_state


@lru_cache(maxsize=1)
def _build_chat_graph():
    workflow = StateGraph(ChatGraphState)
    workflow.add_node("validate_book", _validate_book)
    workflow.add_node("detect_identity", _detect_identity)
    workflow.add_node("route_question", _route_question)
    workflow.add_node("resolve_summary_context", _resolve_summary_context)
    workflow.add_node("run_retrieval_qa", _run_retrieval_qa)
    workflow.add_node(
        "generate_identity_or_summary_answer",
        _generate_identity_or_summary_answer,
    )
    workflow.add_node("persist_chat_history", _persist_chat_history)

    workflow.set_entry_point("validate_book")
    workflow.add_edge("validate_book", "detect_identity")
    workflow.add_conditional_edges(
        "detect_identity",
        _next_after_detect_identity,
        {
            "generate": "generate_identity_or_summary_answer",
            "route": "route_question",
        },
    )
    workflow.add_conditional_edges(
        "route_question",
        _next_after_route_question,
        {
            "persist": "persist_chat_history",
            "summary": "resolve_summary_context",
            "retrieval": "run_retrieval_qa",
        },
    )
    workflow.add_edge("resolve_summary_context", "generate_identity_or_summary_answer")
    workflow.add_edge("run_retrieval_qa", "persist_chat_history")
    workflow.add_edge("generate_identity_or_summary_answer", "persist_chat_history")
    workflow.add_edge("persist_chat_history", END)
    return workflow.compile()


def _next_after_detect_identity(state: ChatGraphState) -> str:
    if state.get("identity_context"):
        return "generate"
    return "route"


def _next_after_route_question(state: ChatGraphState) -> str:
    if state.get("answer"):
        return "persist"

    question_route = state.get("question_route")
    if question_route is not None and question_route.mode in {
        QuestionMode.BOOK_SUMMARY,
        QuestionMode.CHAPTER_SUMMARY,
    }:
        return "summary"

    return "retrieval"


async def _validate_book(state: ChatGraphState) -> ChatGraphState:
    return await _run_logged_node("validate_book", state, _validate_book_impl)


async def _detect_identity(state: ChatGraphState) -> ChatGraphState:
    return await _run_logged_node("detect_identity", state, _detect_identity_impl)


async def _route_question(state: ChatGraphState) -> ChatGraphState:
    return await _run_logged_node("route_question", state, route_question_node)


async def _resolve_summary_context(state: ChatGraphState) -> ChatGraphState:
    return await _run_logged_node(
        "resolve_summary_context",
        state,
        _resolve_summary_context_impl,
    )


async def _run_retrieval_qa(state: ChatGraphState) -> ChatGraphState:
    return await _run_logged_node("run_retrieval_qa", state, run_retrieval_qa_node)


async def _generate_identity_or_summary_answer(
    state: ChatGraphState,
) -> ChatGraphState:
    return await _run_logged_node(
        "generate_identity_or_summary_answer",
        state,
        generate_identity_or_summary_answer_node,
    )


async def _persist_chat_history(state: ChatGraphState) -> ChatGraphState:
    return await _run_logged_node(
        "persist_chat_history",
        state,
        _persist_chat_history_impl,
    )


async def _validate_book_impl(state: ChatGraphState) -> ChatGraphState:
    async with async_session_factory() as session:
        return await validate_book_node(state, session)


async def _detect_identity_impl(state: ChatGraphState) -> ChatGraphState:
    async with async_session_factory() as session:
        return await detect_identity_node(state, session)


async def _resolve_summary_context_impl(state: ChatGraphState) -> ChatGraphState:
    async with async_session_factory() as session:
        return await resolve_summary_context_node(state, session)


async def _persist_chat_history_impl(state: ChatGraphState) -> ChatGraphState:
    async with async_session_factory() as session:
        state = await persist_chat_history_node(state, session)
        await session.commit()
        return state


async def _run_logged_node(
    node_name: str,
    state: ChatGraphState,
    node: Callable[[ChatGraphState], Awaitable[ChatGraphState]],
) -> ChatGraphState:
    start_time = perf_counter()
    try:
        next_state = await node(state)
    except Exception:
        logger.exception(
            "LangGraph node failed: node=%s book_id=%s duration_ms=%s",
            node_name,
            state.get("book_id"),
            round((perf_counter() - start_time) * 1000, 2),
        )
        raise

    logger.info(
        "LangGraph node completed: node=%s book_id=%s mode=%s has_answer=%s "
        "source_count=%s duration_ms=%s",
        node_name,
        next_state.get("book_id"),
        next_state.get("response_mode"),
        bool(next_state.get("answer")),
        len(next_state.get("sources", [])),
        round((perf_counter() - start_time) * 1000, 2),
    )
    return next_state
