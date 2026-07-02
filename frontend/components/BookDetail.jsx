import StatusMessage from "./StatusMessage";

function formatDate(value) {
  if (!value) {
    return "Unknown";
  }
  return new Intl.DateTimeFormat("en", {
    dateStyle: "full",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function BookDetail({ book, loading, error, indexingStatus }) {
  if (loading) {
    return <StatusMessage>Loading selected book...</StatusMessage>;
  }

  if (error) {
    return <StatusMessage tone="error">{error}</StatusMessage>;
  }

  if (!book) {
    return (
      <StatusMessage tone="warning">
        Select a book from the library or upload a new PDF.
      </StatusMessage>
    );
  }

  const ready = indexingStatus?.status === "ready";

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-xs font-semibold tracking-wide text-[#7C9885] uppercase">
            Book Detail
          </p>
          <h1 className="mt-2 text-2xl font-semibold text-slate-900">
            {book.title}
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            {book.author || "Unknown author"} - {book.filename}
          </p>
        </div>
        <span
          className={`w-fit rounded-full px-3 py-1 text-xs font-semibold ${
            ready ? "bg-[#DDE7DD] text-[#4F6F52]" : "bg-amber-50 text-amber-700"
          }`}
        >
          {ready ? "Ready for Q&A" : "Indexing in progress"}
        </span>
      </div>

      <dl className="mt-5 grid gap-3 text-sm text-slate-600 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Chapters" value={book.chapter_count} />
        <Metric label="Chunks" value={book.chunk_count} />
        <div className="rounded-xl border border-slate-200 bg-[#F3EDE2] p-3 sm:col-span-2">
          <dt className="text-slate-500">Uploaded</dt>
          <dd className="mt-1 text-slate-900">
            {formatDate(book.uploaded_at)}
          </dd>
        </div>
      </dl>
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-[#F3EDE2] p-3">
      <dt className="text-slate-500">{label}</dt>
      <dd className="mt-1 text-lg font-semibold text-slate-900">{value}</dd>
    </div>
  );
}
