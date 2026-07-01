# AI Book Assistant Backend

FastAPI backend for the AI Book Assistant project.

## Manual Setup

```powershell
cd D:\blockdev\PROJECT\backend
uv sync
uv run uvicorn main:app --reload
```

Run `uv sync` again after backend dependencies change.

## ChromaDB

This project uses embedded persistent ChromaDB storage at `CHROMA_PERSIST_DIR`.
Install backend dependencies with:

```powershell
uv sync
```

## Linting and Formatting

```powershell
uv sync --extra dev
uv run ruff check .
uv run ruff format .
```

## Database Schema Initialization

Create configured PostgreSQL tables with:

```powershell
uv run python -m database.init_db
```

## Basic CRUD Check

Run a rollback-only repository smoke test with:

```powershell
uv run python -m tests.test_basic_crud
```

## Chunking Unit Tests

```powershell
uv run python -m unittest tests.test_chunking
```

## Book Metadata Persistence Check

```powershell
uv run python -m tests.test_book_indexing
```

## Upload Endpoint

```text
POST /books/upload
Content-Type: multipart/form-data
Field: file
```

The upload flow validates the PDF, stores it under `UPLOAD_DIR`, extracts raw
text with PyMuPDF, cleans it, and stores a sidecar `.extracted.json` file.
