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
    <section className="flex min-h-0 flex-col rounded-lg border border-neutral-800 bg-neutral-950">
      <div className="flex items-center justify-between border-b border-neutral-800 px-4 py-3">
        <div>
          <p className="text-xs font-semibold tracking-wide text-cyan-300 uppercase">
            Library
          </p>
          <h2 className="text-lg font-semibold text-neutral-50">Books</h2>
        </div>
        <button
          className="rounded-md border border-neutral-700 px-3 py-1.5 text-sm text-neutral-200 hover:border-cyan-500 hover:text-cyan-200 disabled:cursor-not-allowed disabled:opacity-60"
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
              className={`rounded-md border p-3 text-left transition ${
                selected
                  ? "border-cyan-500 bg-cyan-950/40"
                  : "border-neutral-800 bg-neutral-900 hover:border-neutral-600"
              }`}
              type="button"
              onClick={() => onSelectBook(book.id)}
            >
              <p className="line-clamp-2 text-sm font-semibold text-neutral-50">
                {book.title}
              </p>
              <p className="mt-1 text-xs text-neutral-400">
                {formatDate(book.uploaded_at)}
              </p>
              <div className="mt-3 flex gap-2 text-xs text-neutral-300">
                <span>{book.chapter_count} chapters</span>
                <span>{book.chunk_count} chunks</span>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
