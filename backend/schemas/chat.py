from datetime import datetime
import uuid

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    book_id: uuid.UUID
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class ChatSource(BaseModel):
    source_index: int
    chunk_id: str
    label: str
    chapter: int | None = None
    chapter_title: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    page_range: str | None = None
    distance: float | None = None


class ChatResponse(BaseModel):
    success: bool
    book_id: str
    question: str
    answer: str
    sources: list[ChatSource]
    message: str


class ChatHistoryItem(BaseModel):
    id: str
    book_id: str
    question: str
    answer: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    success: bool
    book_id: str
    history: list[ChatHistoryItem]
    message: str
