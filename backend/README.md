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
