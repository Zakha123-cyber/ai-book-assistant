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

export default function BookDetail({ book, loading, error }) {
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

  return (
    <section className="rounded-lg border border-neutral-800 bg-neutral-950 p-5">
      <p className="text-xs font-semibold tracking-wide text-cyan-300 uppercase">
        Book Detail
      </p>
      <h1 className="mt-2 text-2xl font-semibold text-neutral-50">
        {book.title}
      </h1>
      <dl className="mt-5 grid gap-3 text-sm text-neutral-300 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-md border border-neutral-800 bg-neutral-900 p-3">
          <dt className="text-neutral-500">Chapters</dt>
          <dd className="mt-1 text-lg font-semibold text-neutral-50">
            {book.chapter_count}
          </dd>
        </div>
        <div className="rounded-md border border-neutral-800 bg-neutral-900 p-3">
          <dt className="text-neutral-500">Chunks</dt>
          <dd className="mt-1 text-lg font-semibold text-neutral-50">
            {book.chunk_count}
          </dd>
        </div>
        <div className="rounded-md border border-neutral-800 bg-neutral-900 p-3 sm:col-span-2">
          <dt className="text-neutral-500">Uploaded</dt>
          <dd className="mt-1 text-neutral-100">
            {formatDate(book.uploaded_at)}
          </dd>
        </div>
      </dl>
    </section>
  );
}
