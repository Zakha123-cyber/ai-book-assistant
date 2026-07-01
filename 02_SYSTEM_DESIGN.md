# AI Book Assistant

# 02_SYSTEM_DESIGN.md

> Version: 1.0

------------------------------------------------------------------------

# 1. System Architecture

``` text
                 ┌──────────────────────────┐
                 │        Frontend          │
                 │ Next.js + Tailwind CSS   │
                 └─────────────┬────────────┘
                               │ REST API
                 ┌─────────────▼────────────┐
                 │      FastAPI Backend     │
                 └─────────────┬────────────┘
        ┌──────────────────────┼────────────────────────┐
        ▼                      ▼                        ▼
 Document Service      AI Service               Chat Service
        │                      │                        │
        ▼                      ▼                        ▼
 PDF Parser            Summarizer               QA Engine
        │                      │                        │
        └──────────────┬───────┴──────────────┬─────────┘
                       ▼                      ▼
                 PostgreSQL             ChromaDB
```

------------------------------------------------------------------------

# 2. Main Components

## Frontend

Responsibilities:

-   Authentication
-   Upload book
-   Display summaries
-   Chat with book
-   View references

------------------------------------------------------------------------

## Backend API

Responsibilities:

-   REST API
-   Authentication
-   File upload
-   Book management
-   Chat endpoint
-   Summary endpoint

------------------------------------------------------------------------

## Document Service

Pipeline:

``` text
Upload PDF
    ↓
Extract Text
    ↓
Clean Text
    ↓
Detect Chapters
    ↓
Semantic Chunking
    ↓
Generate Metadata
```

------------------------------------------------------------------------

## Embedding Service

``` text
Chunks
    ↓
Embedding Model
    ↓
Store Embedding
```

Recommended:

-   text-embedding-3-small

------------------------------------------------------------------------

## Vector Database

Recommended:

-   ChromaDB

Metadata:

-   book_id
-   chapter
-   section
-   page
-   chunk_id

------------------------------------------------------------------------

## Summarization Service

Flow:

``` text
Chunk
  ↓
Chunk Summary
  ↓
Chapter Summary
  ↓
Book Summary
```

Persist all summaries in PostgreSQL.

------------------------------------------------------------------------

## Retrieval Service

``` text
Question
   ↓
Embedding
   ↓
Top-K Search
   ↓
Context Builder
```

Default:

-   Top K = 5

------------------------------------------------------------------------

## QA Service

Prompt receives:

-   User question
-   Retrieved context
-   Metadata

Returns:

-   Answer
-   Source references

------------------------------------------------------------------------

# 3. Database Design

## PostgreSQL

### books

  Column        Type
  ------------- -----------
  id            UUID
  title         TEXT
  author        TEXT
  filename      TEXT
  uploaded_at   TIMESTAMP

### chapters

  Column    Type
  --------- ---------
  id        UUID
  book_id   UUID
  number    INTEGER
  title     TEXT
  summary   TEXT

### chunks

  Column        Type
  ------------- ---------
  id            UUID
  chapter_id    UUID
  chunk_index   INTEGER
  content       TEXT

### summaries

  Column         Type
  -------------- --------------------------
  id             UUID
  level          ENUM(chunk,chapter,book)
  reference_id   UUID
  summary        TEXT

### chat_history

  Column       Type
  ------------ -----------
  id           UUID
  book_id      UUID
  question     TEXT
  answer       TEXT
  created_at   TIMESTAMP

------------------------------------------------------------------------

# 4. API Design

## POST /books/upload

Upload PDF.

Returns:

``` json
{
  "book_id":"uuid"
}
```

------------------------------------------------------------------------

## GET /books

List books.

------------------------------------------------------------------------

## GET /books/{book_id}

Book detail.

------------------------------------------------------------------------

## GET /books/{book_id}/summary

Book summary.

------------------------------------------------------------------------

## GET /books/{book_id}/chapters

Chapter summaries.

------------------------------------------------------------------------

## POST /chat

Request

``` json
{
  "book_id":"uuid",
  "question":"What is Habit Stacking?"
}
```

Response

``` json
{
  "answer":"...",
  "sources":[
    {
      "chapter":4,
      "page":56
    }
  ]
}
```

------------------------------------------------------------------------

# 5. Processing Flow

## Indexing

``` text
Upload
 ↓
Extract
 ↓
Clean
 ↓
Chunk
 ↓
Embedding
 ↓
Save Metadata
 ↓
Save Vector
 ↓
Generate Summaries
```

## Question Answering

``` text
Question
 ↓
Embedding
 ↓
Similarity Search
 ↓
Prompt Builder
 ↓
Qwen 3.5
 ↓
Answer
```

------------------------------------------------------------------------

# 6. Non-Functional Requirements

-   Modular architecture
-   Async processing for indexing
-   Reusable services
-   Environment-based configuration
-   Logging
-   Error handling
-   API documentation (OpenAPI)

------------------------------------------------------------------------

# 7. Future Improvements

-   Hybrid Search (BM25 + Vector)
-   Reranking Model
-   Multi-book chat
-   Streaming responses
-   Background task queue
-   Redis cache
-   OCR support
