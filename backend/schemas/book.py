from pydantic import BaseModel


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
