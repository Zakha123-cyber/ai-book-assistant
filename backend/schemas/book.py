from datetime import datetime

from pydantic import BaseModel


class BookListItem(BaseModel):
    id: str
    title: str
    author: str | None = None
    filename: str
<<<<<<< Updated upstream
    uploaded_at: str
=======
    uploaded_at: datetime
    chapter_count: int
    chunk_count: int
>>>>>>> Stashed changes


class BookListResponse(BaseModel):
    success: bool
    books: list[BookListItem]
    message: str


<<<<<<< Updated upstream
class BookIndexingStatusResponse(BaseModel):
    success: bool
    book_id: str
    embedding_ready: bool
    chunk_summary_ready: bool
    chapter_summary_ready: bool
    book_summary_ready: bool
    chunk_count: int
    chunk_summary_count: int
    chapter_count: int
    chapter_summary_count: int
    status: str
=======
class BookDetailResponse(BaseModel):
    success: bool
    book: BookListItem
>>>>>>> Stashed changes
    message: str


class BookUploadResponse(BaseModel):
    success: bool
    book_id: str | None = None
    filename: str
    stored_path: str | None = None
    extracted_path: str | None = None
    page_count: int | None = None
    chapter_count: int | None = None
    section_count: int | None = None
    chunk_count: int | None = None
    extracted_text_length: int | None = None
    message: str
