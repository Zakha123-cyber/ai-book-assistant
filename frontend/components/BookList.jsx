import StatusMessage from "./StatusMessage";

function formatDate(value) {
  if (!value) {
    return "Unknown date";
  }
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function BookList({
  books,
  selectedBookId,
  loading,
  error,
  onSelectBook,
  onRefresh,
}) {
  return (
    <section className="flex min-h-0 flex-col rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
        <div>
          <p className="text-xs font-semibold tracking-wide text-[#7C9885] uppercase">
            Library
          </p>
          <h2 className="text-lg font-semibold text-slate-900">Books</h2>
        </div>
        <button
          className="rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-sm font-semibold text-slate-700 transition hover:border-[#7C9885] hover:text-[#4F6F52] disabled:cursor-not-allowed disabled:opacity-60"
          type="button"
          onClick={onRefresh}
          disabled={loading}
        >
          Refresh
        </button>
      </div>

      <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto p-3">
        {error ? <StatusMessage tone="error">{error}</StatusMessage> : null}
        {loading ? <StatusMessage>Loading books...</StatusMessage> : null}
        {!loading && books.length === 0 ? (
          <StatusMessage tone="warning">
            No books indexed yet. Upload a PDF to start.
          </StatusMessage>
        ) : null}

        {books.map((book) => {
          const selected = book.id === selectedBookId;
          return (
            <button
              key={book.id}
              className={`rounded-2xl border p-4 text-left shadow-sm transition ${
                selected
                  ? "border-[#7C9885] bg-[#DDE7DD]"
                  : "border-slate-200 bg-white hover:border-[#7C9885]"
              }`}
              type="button"
              onClick={() => onSelectBook(book.id)}
            >
              <div className="flex gap-3">
                <div className="flex h-14 w-11 shrink-0 items-center justify-center rounded-lg bg-[#1E293B] text-xs font-semibold text-white">
                  PDF
                </div>
                <div className="min-w-0">
                  <p className="line-clamp-2 text-sm font-semibold text-slate-900">
                    {book.title}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    {book.author || "Unknown author"}
                  </p>
                </div>
              </div>
              <p className="mt-3 text-xs text-slate-500">
                Indexed {formatDate(book.uploaded_at)}
              </p>
              <div className="mt-3 flex flex-wrap gap-2 text-xs font-medium text-slate-600">
                <span className="rounded-full bg-[#F3EDE2] px-2.5 py-1">
                  {book.chapter_count} chapters
                </span>
                <span className="rounded-full bg-[#F3EDE2] px-2.5 py-1">
                  {book.chunk_count} chunks
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
