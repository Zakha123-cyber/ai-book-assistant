# 04_TASKLIST.md

> **Purpose:** Daftar implementasi bertahap untuk AI Agent.\
> **Rule:** Kerjakan secara berurutan. Jangan melompati task yang belum
> selesai.

---

# Phase 1 --- Project Initialization

- [DONE] T001 Membuat struktur repository.
- [DONE] T002 Inisialisasi backend FastAPI.
- [DONE] T003 Inisialisasi frontend Next.js.
- [DONE] T004 Konfigurasi environment (.env.example).
- [DONE] T005 Konfigurasi PostgreSQL.
- [DONE] T006 Konfigurasi ChromaDB.
- [DONE] T007 Konfigurasi logging.
- [SKIP] T008 Menambahkan Docker Compose (opsional).
- [DONE] T009 Menambahkan konfigurasi linting dan formatting.
- [DONE] T010 Menjalankan health check endpoint.

---

# Phase 2 --- Database

- [DONE] T011 Membuat model `books`.
- [DONE] T012 Membuat model `chapters`.
- [DONE] T013 Membuat model `chunks`.
- [DONE] T014 Membuat model `summaries`.
- [DONE] T015 Membuat model `chat_history`.
- [DONE] T016 Membuat migrasi database.
- [DONE] T017 Menambahkan repository layer.
- [DONE] T018 Menguji CRUD dasar.

---

# Phase 3 --- Upload & Parsing

- [DONE] T019 Endpoint upload PDF.
- [DONE] T020 Validasi ukuran dan tipe file.
- [DONE] T021 Simpan file upload.
- [DONE] T022 Ekstraksi teks menggunakan PyMuPDF.
- [DONE] T023 Membersihkan header/footer.
- [DONE] T024 Menghapus nomor halaman.
- [DONE] T025 Normalisasi whitespace.
- [DONE] T026 Menyimpan hasil ekstraksi.

---

# Phase 4 --- Chunking

- [DONE] T027 Deteksi chapter.
- [DONE] T028 Deteksi section.
- [DONE] T029 Semantic chunking.
- [DONE] T030 Overlap chunk.
- [DONE] T031 Metadata generation.
- [DONE] T032 Unit test chunking.

---

# Phase 5 --- Embedding

- [DONE] T033 Integrasi embedding model.
- [DONE] T034 Generate embedding setiap chunk.
- [DONE] T035 Simpan embedding ke ChromaDB.
- [DONE TAPI MASIH TIDAK MAKSIMAL HASILNYA] T036 Verifikasi retrieval dasar.

---

# Phase 6 --- Hierarchical Summarization

- [DONE] T037 Ringkasan setiap chunk.
- [DONE] T038 Ringkasan setiap chapter.
- [DONE] T039 Ringkasan keseluruhan buku.
- [DONE] T040 Simpan seluruh ringkasan ke PostgreSQL.
- [DONE] T041 Endpoint summary.

---

# Phase 7 --- Retrieval & QA

- [ ] T042 Embedding pertanyaan.
- [ ] T043 Similarity search (Top-K).
- [ ] T044 Context builder.
- [ ] T045 Prompt builder.
- [ ] T046 Integrasi Qwen 3.5 API.
- [ ] T047 Endpoint Chat with Book.
- [ ] T048 Menampilkan source reference.

---

# Phase 8 --- Frontend

- [ ] T049 Halaman daftar buku.
- [ ] T050 Halaman upload.
- [ ] T051 Halaman detail buku.
- [ ] T052 Ringkasan per chapter.
- [ ] T053 Ringkasan buku.
- [ ] T054 Halaman chat.
- [ ] T055 Riwayat chat.
- [ ] T056 Loading & error state.

---

# Phase 9 --- Evaluation

- [ ] T057 Uji kualitas retrieval.
- [ ] T058 Uji kualitas ringkasan.
- [ ] T059 Uji hallucination.
- [ ] T060 Optimasi prompt.
- [ ] T061 Logging evaluasi.

---

# Phase 10 --- Finalization

- [ ] T062 API documentation.
- [ ] T063 README.
- [ ] T064 Deployment configuration.
- [ ] T065 Final testing.
- [ ] T066 Performance profiling.
- [ ] T067 Code cleanup.
- [ ] T068 Release v1.0.

---

# Milestones

## Milestone 1

- Project dapat dijalankan.
- Database aktif.

## Milestone 2

- Buku berhasil diunggah dan diparsing.

## Milestone 3

- Embedding tersimpan di ChromaDB.

## Milestone 4

- Ringkasan bertingkat selesai.

## Milestone 5

- Chat with Book berjalan.

## Milestone 6

- Sistem siap dipresentasikan.

---

# Definition of Done

Sebuah task dinyatakan selesai apabila:

- Implementasi selesai.
- Tidak ada error.
- Mengikuti AI Agent Rules.
- Memiliki logging.
- Memiliki validasi.
- Tidak merusak fitur lain.
- Lulus pengujian yang relevan.
