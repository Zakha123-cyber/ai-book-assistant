# 05_PROMPT_LIBRARY.md

> **Version:** 1.0\
> **Purpose:** Kumpulan prompt yang digunakan oleh AI Book Assistant.
> Seluruh prompt disimpan terpusat agar mudah dievaluasi dan diperbarui.

------------------------------------------------------------------------

# Global System Prompt

``` text
You are AI Book Assistant.

Your responsibility is to understand and explain the uploaded book.

Rules:
- Answer ONLY from the provided context.
- Never use external knowledge.
- If the answer is not supported by the context, explicitly say so.
- Never fabricate facts.
- Cite the relevant chapter and page when available.
- Be concise, factual, and educational.
```

------------------------------------------------------------------------

# Prompt 1 --- Chunk Summary

## Purpose

Meringkas satu chunk.

``` text
Summarize the following passage.

Requirements:
- Maximum 5 bullet points.
- Preserve important terminology.
- Do not introduce new information.
- Keep factual accuracy.
- Output in Markdown.

Context:
{{chunk}}
```

------------------------------------------------------------------------

# Prompt 2 --- Chapter Summary

## Purpose

Menggabungkan ringkasan chunk menjadi ringkasan bab.

``` text
You are given summaries from multiple chunks within the same chapter.

Generate a coherent chapter summary.

Requirements:
- Explain the main ideas.
- Remove duplicated information.
- Preserve key concepts.
- Output:
  1. Overview
  2. Key Points
  3. Important Terms
  4. Chapter Conclusion

Chunk Summaries:
{{chunk_summaries}}
```

------------------------------------------------------------------------

# Prompt 3 --- Book Summary

## Purpose

Menghasilkan ringkasan keseluruhan buku.

``` text
Create a complete summary of the book using the provided chapter summaries.

Output format:

# Overview

# Main Concepts

# Key Takeaways

# Important Terms

# Final Conclusion

Chapter Summaries:
{{chapter_summaries}}
```

------------------------------------------------------------------------

# Prompt 4 --- Question Answering (QA)

## Purpose

Menjawab pertanyaan pengguna berdasarkan hasil retrieval.

``` text
Answer the user's question ONLY using the supplied context.

If the answer cannot be found in the context, reply:

"I could not find that information inside this book."

Requirements:
- Do not use external knowledge.
- Quote relevant concepts when appropriate.
- Mention chapter and page if available.

Question:
{{question}}

Context:
{{retrieved_context}}
```

------------------------------------------------------------------------

# Prompt 5 --- Query Expansion

## Purpose

Memperbaiki query sebelum retrieval.

``` text
Rewrite the user's question into several semantically related search queries.

Return ONLY a JSON array.

Question:
{{question}}
```

------------------------------------------------------------------------

# Prompt 6 --- Retrieval Verification

## Purpose

Memastikan context memang relevan.

``` text
Determine whether the supplied context is sufficient to answer the user's question.

Return:

- sufficient
- insufficient

Question:
{{question}}

Context:
{{retrieved_context}}
```

------------------------------------------------------------------------

# Prompt 7 --- Hallucination Check

## Purpose

Memeriksa apakah jawaban didukung context.

``` text
Compare the answer with the provided context.

Return:

- Supported
- Partially Supported
- Unsupported

Explain briefly.

Context:
{{retrieved_context}}

Answer:
{{answer}}
```

------------------------------------------------------------------------

# Prompt 8 --- Key Insights

## Purpose

Menghasilkan insight penting setelah indexing.

``` text
Extract the following from the book:

- Main Themes
- Key Concepts
- Important Terms
- Notable Quotes
- Practical Lessons

Use only the supplied summaries.

Summaries:
{{book_summary}}
```

------------------------------------------------------------------------

# Prompt 9 --- Flashcard Generator (Future)

``` text
Generate learning flashcards.

Each flashcard must contain:

Question:
Answer:

Maximum 20 flashcards.

Context:
{{chapter_summary}}
```

------------------------------------------------------------------------

# Prompt 10 --- Quiz Generator (Future)

``` text
Generate 10 multiple-choice questions.

Each question must include:

- Question
- Four options
- Correct answer
- Short explanation

Context:
{{chapter_summary}}
```

------------------------------------------------------------------------

# Prompt Variables

  Variable                Description
  ----------------------- ---------------------------
  {{chunk}}               Original chunk text
  {{chunk_summaries}}     List of chunk summaries
  {{chapter_summaries}}   List of chapter summaries
  {{book_summary}}        Final book summary
  {{question}}            User question
  {{retrieved_context}}   Retrieved RAG context
  {{answer}}              Model-generated answer

------------------------------------------------------------------------

# Prompt Engineering Guidelines

-   Gunakan instruksi yang eksplisit.
-   Hindari prompt terlalu panjang.
-   Pisahkan system prompt dan user prompt.
-   Jangan mencampur business logic dengan prompt.
-   Simpan setiap prompt sebagai template terpisah.
-   Selalu lakukan evaluasi kualitas prompt menggunakan dataset uji.

------------------------------------------------------------------------

# Recommended Folder Structure

``` text
backend/
└── services/
    └── prompt/
        ├── system_prompt.txt
        ├── chunk_summary.txt
        ├── chapter_summary.txt
        ├── book_summary.txt
        ├── qa_prompt.txt
        ├── query_expansion.txt
        ├── retrieval_verification.txt
        ├── hallucination_check.txt
        ├── flashcard.txt
        └── quiz.txt
```
