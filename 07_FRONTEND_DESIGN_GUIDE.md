
# 07_FRONTEND_DESIGN_GUIDE.md

> **Project:** AI Book Assistant  
> **Purpose:** Panduan desain frontend untuk AI Agent agar UI platform literasi terlihat modern, konsisten, dan nyaman digunakan.  
> **Frontend Stack:** Next.js + TypeScript + Tailwind CSS

---

# 1. Design Vision

AI Book Assistant adalah platform literasi berbasis AI yang membantu pengguna memahami buku melalui:

- Upload buku
- Ringkasan bertingkat
- Chat with Book
- Source Reference
- Riwayat percakapan
- Insight buku

Desain harus terasa:

- Modern
- Bersih
- Tenang
- Akademik
- Premium tetapi tetap sederhana
- Nyaman untuk membaca teks panjang

Inspirasi visual:

- Medium
- Notion
- Readwise
- NotebookLM
- Perplexity
- Apple Books
- Linear

---

# 2. Design Theme

## Theme Name

**Modern Literary Intelligence**

Konsep utama:

> Perpaduan antara platform membaca buku modern dan AI assistant yang profesional.

Desain tidak boleh terlalu ramai. Fokus utama adalah **konten buku**, **ringkasan**, dan **jawaban AI**.

---

# 3. Color Palette

Gunakan warna yang lembut, literatif, dan modern.

## Primary Colors

| Name | Hex | Usage |
|------|-----|-------|
| Ink Navy | `#1E293B` | Main text, heading |
| Warm Ivory | `#FAF7F0` | Main background |
| Soft Sand | `#F3EDE2` | Card background |
| Sage Green | `#7C9885` | Primary accent |
| Deep Sage | `#4F6F52` | Button primary |
| Clay Brown | `#A67C52` | Secondary accent |
| Muted Gold | `#D6A85A` | Highlight, badge |

## Neutral Colors

| Name | Hex |
|------|-----|
| White | `#FFFFFF` |
| Slate 50 | `#F8FAFC` |
| Slate 100 | `#F1F5F9` |
| Slate 300 | `#CBD5E1` |
| Slate 500 | `#64748B` |
| Slate 700 | `#334155` |
| Slate 900 | `#0F172A` |

## Semantic Colors

| State | Hex |
|-------|-----|
| Success | `#16A34A` |
| Warning | `#F59E0B` |
| Error | `#DC2626` |
| Info | `#2563EB` |

---

# 4. Tailwind Theme Recommendation

Tambahkan warna custom berikut ke `tailwind.config.ts`.

```ts
theme: {
  extend: {
    colors: {
      ink: {
        DEFAULT: "#1E293B",
        dark: "#0F172A",
        muted: "#64748B",
      },
      ivory: {
        DEFAULT: "#FAF7F0",
        soft: "#F3EDE2",
      },
      sage: {
        DEFAULT: "#7C9885",
        dark: "#4F6F52",
        light: "#DDE7DD",
      },
      clay: {
        DEFAULT: "#A67C52",
      },
      gold: {
        DEFAULT: "#D6A85A",
      },
    },
  },
}
```

---

# 5. Typography

## Font Recommendation

Gunakan kombinasi:

- Heading: `Inter` atau `Plus Jakarta Sans`
- Body text: `Inter`
- Reading content: optional `Merriweather`

Rekomendasi final:

```text
Primary Font: Inter
Reading Font: Merriweather
```

## Typography Scale

| Element | Size | Weight |
|---------|------|--------|
| Hero Title | 48-64px | 700 |
| Page Title | 32-40px | 700 |
| Section Title | 24-28px | 600 |
| Card Title | 18-20px | 600 |
| Body | 16px | 400 |
| Small Text | 14px | 400 |
| Caption | 12px | 400 |

---

# 6. Layout Principles

## General Layout

- Gunakan whitespace yang lega.
- Jangan membuat UI terlalu padat.
- Lebar konten membaca maksimal `760px`.
- Lebar dashboard maksimal `1200px`.
- Gunakan card-based layout.
- Gunakan rounded corner modern.
- Gunakan shadow halus, bukan shadow tebal.

## Recommended Container

```tsx
<div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
  ...
</div>
```

## Reading Container

```tsx
<div className="mx-auto max-w-3xl">
  ...
</div>
```

---

# 7. Global UI Style

## Border Radius

| Component | Radius |
|-----------|--------|
| Button | `rounded-xl` |
| Card | `rounded-2xl` |
| Modal | `rounded-2xl` |
| Input | `rounded-xl` |
| Badge | `rounded-full` |

## Shadow

Gunakan shadow lembut:

```tsx
shadow-sm
shadow-md
```

Hindari:

```tsx
shadow-2xl
```

kecuali untuk modal utama.

## Border

Gunakan border halus:

```tsx
border border-slate-200
```

---

# 8. Main Pages

## 1. Landing Page

### Purpose
Menjelaskan fungsi platform dan mengarahkan user untuk upload buku.

### Sections

1. Navbar
2. Hero Section
3. Feature Highlights
4. How It Works
5. Demo Preview
6. Call to Action
7. Footer

### Hero Copy

```text
Understand books faster with AI-powered reading assistance.
```

Subtitle:

```text
Upload a book, generate chapter summaries, ask questions, and trace every answer back to its source.
```

### Hero Layout

```text
Left:
- Title
- Subtitle
- CTA Button
- Secondary Button

Right:
- UI mockup card
- Floating summary card
- Floating source reference card
```

### CTA Buttons

Primary:

```text
Start Reading
```

Secondary:

```text
View Demo
```

---

## 2. Dashboard Page

### Purpose
Menampilkan daftar buku pengguna.

### Components

- Page header
- Upload button
- Search book input
- Book cards
- Empty state

### Book Card Content

- Cover placeholder
- Book title
- Author
- Upload date
- Processing status
- Number of chapters
- Last opened
- Action button: Open Book

### Status Badge

| Status | Label |
|--------|-------|
| uploaded | Uploaded |
| processing | Processing |
| indexed | Ready |
| failed | Failed |

---

## 3. Upload Page

### Purpose
Mengunggah PDF buku.

### UI Requirements

- Drag and drop area
- File validation message
- Upload progress
- Processing status
- Error state
- Success state

### Drag Area Style

```text
Large rounded card
Dashed border
Soft ivory background
Book/upload icon
```

### Upload States

```text
Idle -> Uploading -> Processing -> Ready
```

---

## 4. Book Detail Page

### Purpose
Menampilkan informasi buku, ringkasan, chapter, dan akses chat.

### Layout

```text
Book Header
  ├── Title
  ├── Author
  ├── Metadata
  └── Action Buttons

Tabs
  ├── Overview
  ├── Chapters
  ├── Chat
  └── Sources
```

### Overview Tab

- Book summary
- Key takeaways
- Important terms
- Main themes

### Chapters Tab

- Chapter list
- Chapter summary cards
- Expand/collapse chapter details

### Chat Tab

- Chat with Book interface

### Sources Tab

- Retrieved chunks
- Page references
- Chapter references
- Excerpts

---

## 5. Chat with Book Page

### Purpose
User dapat bertanya tentang isi buku.

### Layout

```text
Left Sidebar:
- Book info
- Chapter list
- Suggested questions

Main Area:
- Chat messages
- Source references
- Input box
```

### Chat Bubble

User message:

```text
Right aligned
Light sage background
```

AI message:

```text
Left aligned
White card
Source reference below answer
```

### Input Box

- Sticky bottom
- Rounded-xl
- Placeholder:

```text
Ask something about this book...
```

### Suggested Questions

Contoh:

- Ringkas buku ini.
- Apa tema utama buku ini?
- Siapa tokoh utama?
- Ringkas Bab 1.
- Apa pesan moral dari cerita ini?

---

# 9. Source Reference UI

Source reference adalah fitur penting.

## Source Card

Tampilkan setelah jawaban AI.

### Content

- Chapter title
- Page number
- Similarity score
- Excerpt preview
- Button: View Source

### Example

```text
Source 1
Bab 4 - Bertemu Pak Wira
Page 18 · Relevance 91%

"Pak Wira memberikan peta yang lebih lengkap dan menceritakan sejarah mercusuar..."
```

### Style

```tsx
<div className="rounded-xl border border-slate-200 bg-ivory-soft p-4">
  ...
</div>
```

---

# 10. Components List

Agent wajib membuat komponen reusable.

## Layout Components

- `Navbar`
- `Sidebar`
- `PageHeader`
- `Container`
- `Footer`

## Book Components

- `BookCard`
- `BookUploadDropzone`
- `BookStatusBadge`
- `BookMetadata`
- `ChapterCard`
- `SummaryCard`

## Chat Components

- `ChatWindow`
- `ChatMessage`
- `ChatInput`
- `SourceReferenceCard`
- `SuggestedQuestionList`

## Common Components

- `Button`
- `Input`
- `Textarea`
- `Badge`
- `Card`
- `Tabs`
- `Skeleton`
- `EmptyState`
- `ErrorState`
- `LoadingSpinner`

---

# 11. UX Rules

## Loading State

Jangan biarkan halaman kosong saat loading.

Gunakan:

- Skeleton card
- Spinner kecil
- Progress indicator untuk upload/indexing

## Empty State

Setiap halaman kosong harus memiliki pesan yang ramah.

Contoh:

```text
No books yet.
Upload your first book to start exploring it with AI.
```

## Error State

Error harus jelas.

Contoh:

```text
We could not process this PDF.
Please upload a valid text-based PDF file.
```

## Confirmation

Untuk aksi destructive seperti hapus buku, gunakan confirmation modal.

---

# 12. Responsive Design

## Desktop

- Sidebar boleh tampil.
- Layout 2 kolom untuk chat dan book detail.
- Card grid 3 kolom.

## Tablet

- Card grid 2 kolom.
- Sidebar menjadi collapsible.

## Mobile

- Card grid 1 kolom.
- Chat full screen.
- Source reference tampil di bawah jawaban.
- Navbar ringkas.

---

# 13. Accessibility Rules

- Gunakan semantic HTML.
- Button harus dapat diakses keyboard.
- Gunakan `aria-label` untuk icon-only button.
- Contrast teks harus jelas.
- Jangan hanya mengandalkan warna untuk status.
- Input harus memiliki label.

---

# 14. Animation Guidelines

Gunakan animasi ringan.

Allowed:

- Fade in
- Slide up
- Hover scale kecil
- Smooth transition

Avoid:

- Animasi berlebihan
- Parallax berat
- Motion yang mengganggu membaca

Recommended class:

```tsx
transition-all duration-200 ease-in-out
```

---

# 15. Icon Style

Gunakan icon style yang clean.

Recommended library:

```text
lucide-react
```

Recommended icons:

- BookOpen
- Upload
- Search
- MessageCircle
- Sparkles
- FileText
- Layers
- Bookmark
- Quote
- Library
- ArrowRight

---

# 16. Page Implementation Priority

AI Agent wajib mengerjakan frontend dengan urutan berikut:

1. Global layout
2. Theme colors
3. Reusable UI components
4. Landing page
5. Dashboard page
6. Upload page
7. Book detail page
8. Chat page
9. Source reference UI
10. Loading, empty, and error states
11. Responsive polish

---

# 17. Frontend Folder Structure

```text
frontend/
├── app/
│   ├── page.tsx
│   ├── dashboard/
│   │   └── page.tsx
│   ├── upload/
│   │   └── page.tsx
│   ├── books/
│   │   └── [bookId]/
│   │       ├── page.tsx
│   │       └── chat/
│   │           └── page.tsx
│   └── layout.tsx
│
├── components/
│   ├── layout/
│   ├── book/
│   ├── chat/
│   ├── source/
│   └── ui/
│
├── lib/
│   ├── api.ts
│   ├── constants.ts
│   └── utils.ts
│
├── types/
│   ├── book.ts
│   ├── chat.ts
│   └── source.ts
│
└── styles/
    └── globals.css
```

---

# 18. Sample Data for Frontend Mocking

Gunakan mock data sebelum backend siap.

## Book

```ts
export const mockBook = {
  id: "book-001",
  title: "Jejak Cahaya di Desa Arunika",
  author: "AI Generated",
  status: "ready",
  chapters: 8,
  uploadedAt: "2026-07-02",
};
```

## Source Reference

```ts
export const mockSources = [
  {
    id: "source-001",
    chapter: "Bab 4 - Bertemu Pak Wira",
    page: 18,
    score: 0.91,
    excerpt:
      "Pak Wira memberikan peta yang lebih lengkap dan menceritakan sejarah mercusuar.",
  },
];
```

---

# 19. Visual Do and Don't

## Do

- Gunakan background warm ivory.
- Gunakan card putih atau soft sand.
- Gunakan typography yang nyaman dibaca.
- Prioritaskan konten.
- Tampilkan source reference dengan jelas.
- Gunakan spacing yang lega.

## Don't

- Jangan memakai warna terlalu neon.
- Jangan membuat UI terlalu gelap.
- Jangan menaruh terlalu banyak elemen dalam satu card.
- Jangan menyembunyikan source reference.
- Jangan membuat chat terlihat seperti chatbot umum tanpa konteks buku.

---

# 20. Final Design Goal

Frontend harus membuat user merasa bahwa mereka sedang menggunakan:

> Platform membaca buku modern yang dibantu AI, bukan sekadar chatbot biasa.

Fokus utama:

1. Membaca
2. Memahami
3. Bertanya
4. Memverifikasi sumber

Desain harus mendukung empat aktivitas tersebut secara jelas.
