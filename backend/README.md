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

## Embedding Service

Embeddings use Alibaba DashScope through the OpenAI-compatible API.
Chunk embeddings are sent in batches of 10 because `text-embedding-v4` rejects
larger batches.

Required environment variables:

```text
DASHSCOPE_API_KEY
DASHSCOPE_BASE_URL
DASHSCOPE_EMBEDDING_MODEL=text-embedding-v4
```

Manual smoke test:

```powershell
uv run python -m tests.test_embedding_manual
```

Chunk embedding unit test:

```powershell
uv run python -m unittest tests.test_chunk_embedding
```

Chroma store unit test:

```powershell
uv run python -m unittest tests.test_chroma_store
```

Manual retrieval smoke test:

```powershell
uv run python -m tests.test_retrieval_manual <book_id> "What happens when Alice follows the white rabbit?"
```

## Upload Endpoint

```text
POST /books/upload
Content-Type: multipart/form-data
Field: file
```

The upload flow validates the PDF, stores it under `UPLOAD_DIR`, extracts raw
text with PyMuPDF, cleans it, and stores a sidecar `.extracted.json` file.
