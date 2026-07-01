import re
import uuid
from pathlib import Path

from fastapi import UploadFile

from core.config import get_settings

READ_CHUNK_SIZE = 1024 * 1024
SAFE_FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


async def save_uploaded_pdf(file: UploadFile) -> Path:
    settings = get_settings()
    upload_dir = _resolve_backend_relative_path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = _safe_filename(file.filename or "uploaded.pdf")
    stored_path = upload_dir / f"{uuid.uuid4()}_{safe_filename}"

    await file.seek(0)
    with stored_path.open("wb") as output_file:
        while chunk := await file.read(READ_CHUNK_SIZE):
            output_file.write(chunk)
    await file.seek(0)

    return stored_path


def _resolve_backend_relative_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path

    backend_dir = Path(__file__).resolve().parents[2]
    return (backend_dir / path).resolve()


def _safe_filename(filename: str) -> str:
    name = Path(filename).name.strip()
    safe_name = SAFE_FILENAME_PATTERN.sub("_", name)
    return safe_name or "uploaded.pdf"
