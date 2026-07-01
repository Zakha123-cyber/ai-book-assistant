# 06_EVALUATION_PLAN.md

> Version: 1.0\
> Purpose: Menentukan metode evaluasi AI Book Assistant agar setiap
> komponen dapat diukur secara objektif.

------------------------------------------------------------------------

# 1. Evaluation Objectives

Evaluasi dilakukan untuk memastikan bahwa sistem:

-   Menghasilkan retrieval yang relevan.
-   Menghasilkan ringkasan yang akurat.
-   Menjawab pertanyaan berdasarkan isi buku.
-   Meminimalkan hallucination.
-   Memiliki performa yang baik.
-   Menggunakan API secara efisien.

------------------------------------------------------------------------

# 2. Evaluation Scope

  Component          Objective
  ------------------ ----------------------------------------
  Document Parsing   Teks berhasil diekstraksi dengan benar
  Chunking           Chunk memiliki konteks yang utuh
  Embedding          Representasi semantik berkualitas
  Retrieval          Mengambil chunk yang relevan
  Summarization      Ringkasan akurat dan mudah dipahami
  QA                 Jawaban sesuai isi buku
  UI                 Pengalaman pengguna baik
  Performance        Respon cepat dan stabil

------------------------------------------------------------------------

# 3. Retrieval Evaluation

## Metrics

-   Recall@5
-   Recall@10
-   Precision@5
-   Mean Reciprocal Rank (MRR)

## Manual Checklist

-   [ ] Chunk relevan ditemukan.
-   [ ] Chapter yang dikembalikan benar.
-   [ ] Page reference sesuai.
-   [ ] Context cukup untuk menjawab.

Target:

  Metric        Target
  ------------- --------
  Recall@5      \> 80%
  Precision@5   \> 75%

------------------------------------------------------------------------

# 4. Summarization Evaluation

Evaluasi dilakukan secara manual menggunakan rubrik berikut.

  Aspect           Weight
  -------------- --------
  Accuracy            35%
  Completeness        25%
  Clarity             20%
  Consistency         20%

Skor:

1 = Poor\
2 = Fair\
3 = Good\
4 = Very Good\
5 = Excellent

Target:

-   Nilai rata-rata ≥ 4.

------------------------------------------------------------------------

# 5. Question Answering Evaluation

Untuk setiap pertanyaan, nilai:

  Aspect         Description
  -------------- ------------------------
  Correctness    Jawaban benar
  Relevance      Menjawab pertanyaan
  Faithfulness   Didukung context
  Completeness   Tidak kurang informasi

Target:

-   Faithfulness ≥ 95%
-   Correctness ≥ 90%

------------------------------------------------------------------------

# 6. Hallucination Evaluation

Kategori:

-   Supported
-   Partially Supported
-   Unsupported

Hallucination Rate

``` text
Unsupported Answers
-----------------------------
Total Answers
```

Target:

-   Hallucination \< 5%

------------------------------------------------------------------------

# 7. Prompt Evaluation

Evaluasi setiap prompt berdasarkan:

-   Konsistensi
-   Kejelasan
-   Panjang prompt
-   Stabilitas hasil
-   Kepatuhan terhadap instruksi

Catat perubahan prompt beserta dampaknya.

------------------------------------------------------------------------

# 8. Performance Evaluation

## Indexing

Target:

  Metric           Target
  ---------------- ----------------------
  Parsing          \< 5 s (100 halaman)
  Chunking         \< 3 s
  Embedding        \< 20 s
  Total Indexing   \< 60 s

## Chat

  Metric           Target
  ---------------- ---------
  Retrieval        \< 1 s
  LLM Response     \< 8 s
  Total Response   \< 10 s

------------------------------------------------------------------------

# 9. Cost Evaluation

Pantau:

-   Total API Calls
-   Total Input Tokens
-   Total Output Tokens
-   Estimasi biaya

Target:

-   Hindari pemanggilan ulang jika data sudah tersedia.
-   Gunakan cache untuk ringkasan.

------------------------------------------------------------------------

# 10. Dataset Evaluation

Gunakan minimal:

-   3 buku nonfiksi
-   2 buku fiksi
-   1 dokumen teknis

Masing-masing memiliki:

-   ≥ 20 pertanyaan
-   ≥ 5 evaluasi ringkasan

------------------------------------------------------------------------

# 11. User Acceptance Testing (UAT)

Checklist:

-   [ ] Upload berhasil.
-   [ ] Ringkasan muncul.
-   [ ] Chat berjalan.
-   [ ] Referensi tampil.
-   [ ] Error handling baik.
-   [ ] UI responsif.

Target:

-   Seluruh skenario lulus.

------------------------------------------------------------------------

# 12. Error Analysis

Catat setiap kegagalan:

-   Parsing Error
-   Chunking Error
-   Retrieval Miss
-   Hallucination
-   API Error
-   Timeout

Dokumentasikan:

-   Penyebab
-   Dampak
-   Solusi
-   Status

------------------------------------------------------------------------

# 13. Evaluation Report Template

## Experiment

-   Date:
-   Book:
-   Model:
-   Prompt Version:

## Results

-   Retrieval Score:
-   QA Score:
-   Summary Score:
-   Hallucination Rate:
-   Response Time:
-   Token Usage:

## Observations

-   Strengths
-   Weaknesses
-   Improvements

------------------------------------------------------------------------

# 14. Success Criteria

Project dianggap berhasil apabila:

-   Retrieval mencapai target.
-   Hallucination \< 5%.
-   Ringkasan memperoleh skor ≥ 4/5.
-   QA Faithfulness ≥ 95%.
-   Response time \< 10 detik.
-   Sistem stabil untuk buku \> 300 halaman.

------------------------------------------------------------------------

# 15. Continuous Improvement

Setelah setiap iterasi:

1.  Evaluasi hasil.
2.  Analisis error.
3.  Perbaiki prompt.
4.  Optimalkan retrieval.
5.  Uji ulang.
6.  Dokumentasikan perubahan.

Gunakan pendekatan berbasis data, bukan asumsi.
