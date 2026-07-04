import uuid
from typing import TypedDict

from models import Book
from services.qa.app_identity import AppIdentityRoute
from services.qa.context_builder import SourceReference
from services.qa.question_router import QuestionRoute


class ChatGraphState(TypedDict, total=False):
    book_id: uuid.UUID
    question: str
    normalized_question: str
    top_k: int

    book: Book
    question_route: QuestionRoute
    identity_route: AppIdentityRoute

    identity_context: str
    summary_context: str
    sources: list[SourceReference]

    answer: str
    message: str
    response_mode: str
