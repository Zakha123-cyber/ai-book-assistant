from fastapi import UploadFile, status

PDF_CONTENT_TYPES = {"application/pdf", "application/x-pdf"}
PDF_EXTENSION = ".pdf"
BYTES_PER_MB = 1024 * 1024
READ_CHUNK_SIZE = 1024 * 1024


class UploadValidationError(ValueError):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def validate_pdf_upload(file: UploadFile, max_size_mb: int) -> int:
    filename = file.filename or ""
    content_type = file.content_type or ""

    if not filename.lower().endswith(PDF_EXTENSION):
        raise UploadValidationError(
            "Only PDF files are allowed.",
            status.HTTP_400_BAD_REQUEST,
        )

    if content_type not in PDF_CONTENT_TYPES:
        raise UploadValidationError(
            "Invalid file type. Expected application/pdf.",
            status.HTTP_400_BAD_REQUEST,
        )

    max_size_bytes = max_size_mb * BYTES_PER_MB
    size_bytes = await _measure_upload_size(file, max_size_bytes)

    if size_bytes > max_size_bytes:
        raise UploadValidationError(
            f"File size exceeds the {max_size_mb} MB limit.",
            status.HTTP_413_CONTENT_TOO_LARGE,
        )

    return size_bytes


async def _measure_upload_size(file: UploadFile, max_size_bytes: int) -> int:
    size_bytes = 0
    await file.seek(0)

    while chunk := await file.read(READ_CHUNK_SIZE):
        size_bytes += len(chunk)
        if size_bytes > max_size_bytes:
            break

    await file.seek(0)
    return size_bytes
