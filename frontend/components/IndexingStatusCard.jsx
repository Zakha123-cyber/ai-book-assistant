const statusCopy = {
  uploaded: {
    label: "Uploaded",
    description: "Book metadata is stored. Waiting for indexing steps.",
  },
  embedding_ready: {
    label: "Embedding Ready",
    description: "Chunks are indexed. Summary generation is starting.",
  },
  summarizing: {
    label: "Summarizing",
    description: "Chunk, chapter, and book summaries are being generated.",
  },
  ready: {
    label: "Ready",
    description: "Indexing and summary generation are complete.",
  },
};

export default function IndexingStatusCard({
  status,
  loading,
  error,
  onRetry,
}) {
  if (error) {
    return (
      <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        Could not load indexing status: {error}
      </div>
    );
  }

  if (!status && loading) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center gap-3">
          <Spinner />
          <div>
            <p className="text-sm font-semibold text-slate-900">
              Checking indexing status
            </p>
            <p className="text-sm text-slate-500">
              Loading background processing state...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!status) {
    return null;
  }

  const copy = statusCopy[status.status] || {
    label: status.status,
    description: "Background processing is in progress.",
  };
  const ready = status.status === "ready";
  const chunkProgress = ratio(
    status.chunk_summary_count,
    status.chunk_count,
    status.chunk_summary_ready,
  );
  const chapterProgress = ratio(
    status.chapter_summary_count,
    status.chapter_count,
    status.chapter_summary_ready,
  );

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-3">
          {ready ? <ReadyIcon /> : <Spinner />}
          <div>
            <p className="text-xs font-semibold tracking-wide text-[#7C9885] uppercase">
              Background Indexing
            </p>
            <h2 className="mt-1 text-lg font-semibold text-slate-900">
              {copy.label}
            </h2>
            <p className="mt-1 text-sm leading-5 text-slate-500">
              {copy.description}
            </p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span
            className={`w-fit rounded-full px-3 py-1 text-xs font-semibold ${
              ready
                ? "bg-emerald-50 text-emerald-700"
                : "bg-amber-50 text-amber-700"
            }`}
          >
            {ready ? "Ready" : "Processing"}
          </span>
          {!ready ? (
            <button
              className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-700 transition hover:border-[#7C9885] hover:text-[#4F6F52] disabled:cursor-not-allowed disabled:opacity-60"
              disabled={loading}
              type="button"
              onClick={onRetry}
            >
              {loading ? "Retrying..." : "Retry indexing"}
            </button>
          ) : null}
        </div>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <ProgressItem
          label="Chunk summaries"
          value={chunkProgress}
          detail={`${status.chunk_summary_count}/${status.chunk_count}`}
        />
        <ProgressItem
          label="Chapter summaries"
          value={chapterProgress}
          detail={`${status.chapter_summary_count}/${status.chapter_count}`}
        />
        <ProgressItem
          label="Book summary"
          value={status.book_summary_ready ? 100 : 0}
          detail={status.book_summary_ready ? "Ready" : "Pending"}
        />
      </div>
    </section>
  );
}

function ProgressItem({ label, value, detail }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-[#F3EDE2] p-3">
      <div className="flex items-center justify-between gap-3 text-sm">
        <p className="font-semibold text-slate-800">{label}</p>
        <p className="text-xs font-medium text-slate-500">{detail}</p>
      </div>
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-white">
        <div
          className="h-full rounded-full bg-[#4F6F52] transition-all duration-500"
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

function Spinner() {
  return (
    <span className="mt-1 h-5 w-5 shrink-0 animate-spin rounded-full border-2 border-[#DDE7DD] border-t-[#4F6F52]" />
  );
}

function ReadyIcon() {
  return (
    <span className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-700">
      OK
    </span>
  );
}

function ratio(done, total, forcedReady = false) {
  if (forcedReady) {
    return 100;
  }
  if (!total) {
    return 0;
  }
  return Math.min(100, Math.round((done / total) * 100));
}
