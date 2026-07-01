from pydantic import BaseModel


class BookUploadResponse(BaseModel):
    success: bool
    filename: str
    stored_path: str | None = None
    extracted_path: str | None = None
    page_count: int | None = None
    extracted_text_length: int | None = None
    message: str
