import logging

from fastapi import APIRouter, HTTPException, status

from core.logging import preview_text
from schemas.chat import ChatRequest, ChatResponse, ChatSource
from services.embedding import EmbeddingServiceError, QuestionEmbeddingError
from services.qa import (
    ANSWER_NOT_FOUND,
    ChatGraphBookNotFoundError,
    ChatGraphSummaryNotFoundError,
    ChatGraphSystemProfileNotFoundError,
    QAServiceError,
    SourceReference,
    format_page_range,
    format_source_label,
    run_chat_graph,
)
from services.retriever import SimilaritySearchError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_book(request: ChatRequest) -> ChatResponse:
    normalized_question = request.question.strip()
    logger.info(
        "Chat request received: book_id=%s top_k=%s question=%s",
        request.book_id,
        request.top_k,
        preview_text(normalized_question),
    )

    try:
        graph_state = await run_chat_graph(
            book_id=request.book_id,
            question=normalized_question,
            top_k=request.top_k,
        )
        answer = graph_state.get("answer", ANSWER_NOT_FOUND)
        sources = graph_state.get("sources", [])
        message = graph_state.get("message", "Chat answer generated successfully.")
        response_mode = graph_state.get("response_mode", "unknown")
    except ChatGraphBookNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": str(error),
            },
        ) from error
    except ChatGraphSummaryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": str(error),
            },
        ) from error
    except ChatGraphSystemProfileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": str(error),
            },
        ) from error
    except (QuestionEmbeddingError, SimilaritySearchError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": str(error),
            },
        ) from error
    except (EmbeddingServiceError, QAServiceError) as error:
        logger.exception("Chat service failed: book_id=%s", request.book_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "success": False,
                "message": "Chat service failed.",
            },
        ) from error

    logger.info(
        "Chat response ready: book_id=%s mode=%s answer_preview=%s source_count=%s",
        request.book_id,
        response_mode,
        preview_text(answer),
        len(sources),
    )

    return ChatResponse(
        success=True,
        book_id=str(request.book_id),
        question=normalized_question,
        answer=answer,
        sources=_sources_to_response(sources),
        message=message,
    )


def _sources_to_response(sources: list[SourceReference]) -> list[ChatSource]:
    return [
        ChatSource(
            source_index=index,
            chunk_id=source.chunk_id,
            label=format_source_label(source),
            chapter=source.chapter,
            chapter_title=source.chapter_title,
            page_start=source.page_start,
            page_end=source.page_end,
            page_range=format_page_range(source),
            distance=source.distance,
        )
        for index, source in enumerate(sources, start=1)
    ]
