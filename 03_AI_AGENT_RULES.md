# 03_AI_AGENT_RULES.md

> Version: 1.0

# Purpose

Dokumen ini mendefinisikan aturan yang WAJIB diikuti AI Agent selama
proses pengembangan AI Book Assistant agar implementasi tetap konsisten,
modular, mudah dipelihara, dan sesuai dengan arsitektur proyek.

------------------------------------------------------------------------

# 1. General Principles

-   Selalu ikuti `01_PROJECT_PLANNING.md`.
-   Selalu ikuti `02_SYSTEM_DESIGN.md`.
-   Jangan mengubah arsitektur tanpa instruksi pengguna.
-   Utamakan maintainability dibanding kecepatan implementasi.
-   Hindari duplikasi kode (DRY).
-   Terapkan SOLID bila relevan.
-   Setiap fitur harus modular.

------------------------------------------------------------------------

# 2. Development Order

Implementasi wajib mengikuti urutan berikut:

1.  Project setup
2.  Database
3.  Authentication
4.  Upload PDF
5.  Document parser
6.  Cleaning
7.  Chunking
8.  Embedding
9.  ChromaDB
10. Summarization
11. Chat with Book
12. UI Enhancement
13. Testing
14. Optimization

Jangan melompati tahapan.

------------------------------------------------------------------------

# 3. Coding Standards

## Python

-   Python 3.12+
-   Gunakan type hints.
-   Gunakan async bila memungkinkan.
-   Maksimal ±300 baris per file.
-   Fungsi maksimal ±50 baris bila memungkinkan.

## Naming

Class: - PascalCase

Function: - snake_case

Variable: - snake_case

Constant: - UPPER_CASE

------------------------------------------------------------------------

# 4. Project Structure

``` text
backend/
    api/
    services/
    repositories/
    database/
    models/
    schemas/
    core/
    utils/
    tests/

frontend/
    app/
    components/
    hooks/
    services/
```

Jangan membuat folder baru tanpa alasan yang jelas.

------------------------------------------------------------------------

# 5. Layer Responsibilities

## Router

-   Validasi request
-   Memanggil service
-   Mengembalikan response

Tidak boleh berisi business logic.

## Service

-   Seluruh business logic.
-   Mengorkestrasi proses.

## Repository

-   Seluruh akses database.

## Utils

-   Helper reusable.

------------------------------------------------------------------------

# 6. RAG Rules

Pipeline wajib:

``` text
Upload
→ Extract
→ Clean
→ Chunk
→ Embed
→ Store Vector
→ Retrieve
→ Prompt
→ LLM
```

Tidak boleh melewati retrieval untuk proses QA.

------------------------------------------------------------------------

# 7. Prompt Engineering Rules

QA Prompt wajib:

-   Jawab hanya berdasarkan context.
-   Jangan menggunakan pengetahuan eksternal.
-   Jika context tidak cukup, katakan bahwa informasi tidak ditemukan.

Prompt harus dipisahkan dari business logic (mis. folder
`services/prompt/`).

------------------------------------------------------------------------

# 8. Chunking Rules

Gunakan semantic chunking.

Prioritas:

1.  Chapter
2.  Section
3.  Paragraph
4.  Token limit

Default:

-   Chunk: 800 token
-   Overlap: 100 token

------------------------------------------------------------------------

# 9. Database Rules

PostgreSQL:

-   Metadata
-   Chat history
-   Summary

ChromaDB:

-   Embeddings
-   Metadata retrieval

Jangan menyimpan embedding di PostgreSQL.

------------------------------------------------------------------------

# 10. API Rules

Semua endpoint harus:

-   JSON response
-   HTTP status code yang tepat
-   Error format konsisten

Contoh:

``` json
{
  "success": false,
  "message": "Book not found"
}
```

------------------------------------------------------------------------

# 11. Logging

Gunakan logging untuk:

-   Upload
-   Parsing
-   Embedding
-   Retrieval
-   LLM Request
-   Error

Jangan menggunakan print() pada production code.

------------------------------------------------------------------------

# 12. Error Handling

Tangani dengan jelas:

-   Invalid PDF
-   Empty document
-   Embedding failure
-   Vector DB failure
-   LLM timeout
-   Database error

Jangan membiarkan exception tidak tertangani.

------------------------------------------------------------------------

# 13. Security

-   Validasi tipe file upload.
-   Batasi ukuran file.
-   Simpan API Key pada environment variable.
-   Jangan commit secret.
-   Sanitasi input pengguna.

------------------------------------------------------------------------

# 14. Performance

-   Gunakan background task untuk indexing.
-   Hindari pemanggilan LLM berulang.
-   Cache hasil summary jika memungkinkan.
-   Simpan hasil summary ke database.

------------------------------------------------------------------------

# 15. Testing

Minimal:

-   Unit Test
-   Integration Test

Komponen yang wajib diuji:

-   Parser
-   Chunker
-   Embedding
-   Retrieval
-   Summarizer
-   QA

------------------------------------------------------------------------

# 16. Git Rules

Commit kecil dan deskriptif.

Contoh:

-   feat: add semantic chunking
-   feat: integrate chromadb
-   fix: parser page detection
-   refactor: move prompt builder

------------------------------------------------------------------------

# 17. Documentation

Setiap service harus memiliki:

-   Tujuan
-   Input
-   Output
-   Dependency

Function kompleks harus memiliki docstring.

------------------------------------------------------------------------

# 18. Definition of Done

Suatu task dianggap selesai apabila:

-   Berjalan tanpa error.
-   Memiliki validasi.
-   Memiliki logging.
-   Memiliki test (jika relevan).
-   Tidak merusak fitur lain.
-   Mengikuti struktur proyek.

------------------------------------------------------------------------

# 19. Forbidden Practices

AI Agent TIDAK BOLEH:

-   Menaruh business logic di router.
-   Hardcode API key.
-   Menyalin kode tanpa refactor.
-   Mengubah struktur proyek tanpa izin.
-   Menghapus komentar penting.
-   Menambahkan dependency tanpa alasan.

------------------------------------------------------------------------

# 20. Guiding Principle

Selalu prioritaskan:

1.  Correctness
2.  Maintainability
3.  Readability
4.  Modularity
5.  Performance

Optimasi hanya dilakukan setelah fitur berfungsi dengan benar.
