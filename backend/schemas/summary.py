from pydantic import BaseModel


class BookSummaryResponse(BaseModel):
    success: bool
    book_id: str
    level: str
    summary: str
    message: str


class ChapterSummaryItem(BaseModel):
    chapter_id: str
    number: int
    title: str
    summary: str | None = None


class ChapterSummariesResponse(BaseModel):
    success: bool
    book_id: str
    chapters: list[ChapterSummaryItem]
    message: str
