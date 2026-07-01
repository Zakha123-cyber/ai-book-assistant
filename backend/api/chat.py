import logging
import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import async_session_factory
from models import ChatHistory, SummaryLevel
from repositories import (
    BookRepository,
    ChapterRepository,
    ChatHistoryRepository,
    SummaryRepository,
)
from schemas.chat import ChatRequest, ChatResponse, ChatSource
from services.embedding import EmbeddingServiceError, QuestionEmbeddingError
from services.qa import (
    ANSWER_NOT_FOUND,
    QAServiceError,
    QwenQAService,
    SourceReference,
    answer_book_question,
    format_page_range,
    format_source_label,
)
from services.qa.question_router import QuestionMode, QuestionRoute, route_question
from services.retriever import SimilaritySearchError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_book(request: ChatRequest) -> ChatResponse:
    normalized_question = request.question.strip()
    question_route = route_question(normalized_question)
    summary_context: str | None = None
    summary_sources: list[SourceReference] = []

    async with async_session_factory() as session:
        book = await BookRepository(session).get_by_id(request.book_id)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "message": "Book not found.",
                },
            )

        if question_route.mode in {
            QuestionMode.BOOK_SUMMARY,
            QuestionMode.CHAPTER_SUMMARY,
        }:
            summary_context, summary_sources = await _get_summary_context(
                session=session,
                book_id=request.book_id,
                route=question_route,
            )

    try:
        if question_route.mode == QuestionMode.OUT_OF_SCOPE:
            answer = ANSWER_NOT_FOUND
            sources: list[SourceReference] = []
            message = "Question is outside the scope of this book."
        elif summary_context is not None:
            answer = await QwenQAService().answer_question(
                question=normalized_question,
                retrieved_context=summary_context,
            )
            sources = [] if _is_not_found_answer(answer) else summary_sources
            message = "Summary answer generated successfully."
        else:
            result = await answer_book_question(
                book_id=str(request.book_id),
                question=normalized_question,
                top_k=request.top_k,
            )
            answer = result.answer
            sources = result.sources
            message = "Chat answer generated successfully."
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

    async with async_session_factory() as session:
        await ChatHistoryRepository(session).add(
            ChatHistory(
                book_id=request.book_id,
                question=normalized_question,
                answer=answer,
            )
        )
        await session.commit()

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


async def _get_summary_context(
    session: AsyncSession,
    book_id: uuid.UUID,
    route: QuestionRoute,
) -> tuple[str, list[SourceReference]]:
    if route.mode == QuestionMode.BOOK_SUMMARY:
        summaries = await SummaryRepository(session).list_by_reference(
            reference_id=book_id,
            level=SummaryLevel.BOOK,
        )
        if not summaries:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "message": "Book summary not found.",
                },
            )
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

    if route.mode == QuestionMode.CHAPTER_SUMMARY and route.chapter_number is not None:
        chapters = await ChapterRepository(session).list_by_book_id(book_id)
        chapter = next(
            (item for item in chapters if item.number == route.chapter_number),
            None,
        )
        if chapter is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "message": "Chapter not found.",
                },
            )

        summaries = await SummaryRepository(session).list_by_reference(
            reference_id=chapter.id,
            level=SummaryLevel.CHAPTER,
        )
        if not summaries:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "message": "Chapter summary not found.",
                },
            )
        return (
            (
                f"[Chapter Summary] Chapter {chapter.number}: {chapter.title}\n"
                f"{summaries[0].summary}"
            ),
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

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "success": False,
            "message": "Unsupported question route.",
        },
    )


def _is_not_found_answer(answer: str) -> bool:
    normalized_answer = " ".join(answer.casefold().split())
    return ANSWER_NOT_FOUND.casefold() in normalized_answer
