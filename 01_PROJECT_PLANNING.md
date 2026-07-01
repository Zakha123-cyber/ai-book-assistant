# AI Book Assistant

## RAG-Based Long Document Understanding using Qwen 3.5

> **Version:** 1.0\
> **Status:** Planning\
> **Model:** Qwen 3.5 API\
> **Architecture:** Retrieval-Augmented Generation (RAG)

------------------------------------------------------------------------

# 1. Project Overview

## Project Name

**AI Book Assistant**

## Description

AI Book Assistant adalah sistem berbasis **Retrieval-Augmented
Generation (RAG)** yang mampu memahami buku berukuran besar melalui
proses:

-   Document Parsing
-   Text Cleaning
-   Semantic Chunking
-   Embedding
-   Vector Retrieval
-   Hierarchical Summarization
-   Question Answering (QA)

Sistem hanya menjawab berdasarkan isi buku yang diunggah sehingga
mengurangi hallucination.

------------------------------------------------------------------------

# 2. Project Goals

## Core Features

### 1. Chat with Book

Pengguna dapat mengajukan pertanyaan menggunakan bahasa alami.

**Contoh:**

-   Apa inti Chapter 3?
-   Jelaskan konsep Habit Stacking.
-   Apa kesimpulan buku ini?

------------------------------------------------------------------------

### 2. Hierarchical Summarization

Ringkasan dibuat secara bertingkat:

1.  Chunk Summary
2.  Chapter Summary
3.  Book Summary

------------------------------------------------------------------------

### 3. Question Answering (QA)

Jawaban dihasilkan melalui proses retrieval dari Vector Database dan
**tidak menggunakan pengetahuan di luar buku**.

------------------------------------------------------------------------

# 3. High Level Architecture

``` text
                Upload Book
                     │
                     ▼
              Document Parser
                     │
                     ▼
              Text Cleaning
                     │
                     ▼
              Semantic Chunking
                     │
                     ▼
               Embedding Model
                     │
                     ▼
                 ChromaDB
              (Vector Database)
                     │
      ┌──────────────┴──────────────┐
      │                             │
      ▼                             ▼
Summarization Engine          Retrieval Engine
      │                             │
      ▼                             ▼
 Book Summary                Relevant Chunks
      │                             │
      └──────────────┬──────────────┘
                     ▼
                Qwen 3.5 API
                     │
                     ▼
                  Frontend
```

------------------------------------------------------------------------

# 4. Processing Pipeline

``` text
Upload Book
      │
      ▼
Extract Text
      │
      ▼
Text Cleaning
      │
      ▼
Semantic Chunking
      │
      ▼
Generate Metadata
      │
      ▼
Embedding
      │
      ▼
Store into ChromaDB
```

------------------------------------------------------------------------

# 5. Chunking Strategy

Gunakan **semantic chunking**, bukan pemotongan berdasarkan jumlah
karakter.

## Hierarchy

``` text
Book
 └── Chapter
      └── Section
           └── Paragraph
                └── Chunk
```

### Configuration

  Parameter           Value
  ------------ ------------
  Chunk Size     800 Tokens
  Overlap        100 Tokens

------------------------------------------------------------------------

# 6. Parent--Child Chunk Strategy

``` text
Parent Chunk (2000 Tokens)

├── Child Chunk 1 (500)
├── Child Chunk 2 (500)
├── Child Chunk 3 (500)
└── Child Chunk 4 (500)
```

-   Retrieval menggunakan Child Chunk.
-   Context dikirim menggunakan Parent Chunk.

------------------------------------------------------------------------

# 7. Hierarchical Summarization

``` text
Chunks
   │
   ▼
Chunk Summary
   │
   ▼
Chapter Summary
   │
   ▼
Book Summary
```

Jenis ringkasan:

-   Quick Summary
-   Detailed Summary
-   Bullet Summary

------------------------------------------------------------------------

# 8. Chat with Book Pipeline

``` text
Question
    │
    ▼
Question Embedding
    │
    ▼
Similarity Search
    │
    ▼
Top-K Chunks
    │
    ▼
Prompt Builder
    │
    ▼
Qwen 3.5
    │
    ▼
Answer + Source Reference
```

------------------------------------------------------------------------

# 9. Prompt Engineering

## QA Prompt

``` text
You are an AI Book Assistant.

Answer ONLY using the provided context.

If the answer cannot be found inside the provided context,
reply:

"I could not find that information inside this book."

Do not use external knowledge.
```

## Summarization Prompt

``` text
Summarize the provided text.

Requirements:
- Maximum 5 key points.
- Preserve important terminology.
- Do not introduce new information.
- Keep factual accuracy.
```

------------------------------------------------------------------------

# 10. Hallucination Prevention

-   Answer only from retrieved context.
-   Reject unsupported questions.
-   Show source references.
-   Use Top-K Retrieval.
-   Keep prompts strict.
-   Future improvements:
    -   Hybrid Search
    -   Reranker
    -   Confidence Score

------------------------------------------------------------------------

# 11. Technology Stack

  Component         Technology
  ----------------- ------------------------
  Frontend          Next.js + Tailwind CSS
  Backend           FastAPI
  LLM               Qwen 3.5 API
  Embedding         text-embedding-3-small
  Vector Database   ChromaDB
  Database          PostgreSQL
  Parser            PyMuPDF
  ORM               SQLAlchemy

------------------------------------------------------------------------

# 12. Recommended Folder Structure

``` text
ai-book-assistant/

├── backend/
│   ├── api/
│   ├── services/
│   │   ├── parser/
│   │   ├── chunker/
│   │   ├── embedding/
│   │   ├── retriever/
│   │   ├── summarizer/
│   │   ├── qa/
│   │   └── prompt/
│   ├── database/
│   ├── models/
│   └── main.py
│
├── frontend/
├── chroma_db/
├── uploads/
├── summaries/
└── README.md
```

------------------------------------------------------------------------

# 13. Development Roadmap

1.  Project Initialization
2.  PDF Upload & Parsing
3.  Cleaning & Chunking
4.  Embedding & ChromaDB
5.  Hierarchical Summarization
6.  Chat with Book
7.  Evaluation & Deployment

------------------------------------------------------------------------

# 14. Expected Outcome

Sistem mampu:

-   Memahami buku berukuran besar.
-   Menghasilkan ringkasan bertingkat.
-   Menjawab pertanyaan berdasarkan isi buku.
-   Mengurangi hallucination.
-   Menunjukkan efektivitas RAG menggunakan Small Language Model (Qwen
    3.5).
