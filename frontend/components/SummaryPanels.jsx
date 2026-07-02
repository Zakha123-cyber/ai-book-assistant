import StatusMessage from "./StatusMessage";
import MarkdownText from "./MarkdownText";

export default function SummaryPanels({
  bookSummary,
  chapters,
  indexingStatus,
}) {
  const processing = indexingStatus && indexingStatus.status !== "ready";
  const waitingForBookSummary =
    processing && !indexingStatus.book_summary_ready;

  return (
    <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <p className="text-xs font-semibold tracking-wide text-[#7C9885] uppercase">
          Book Summary
        </p>
        <div className="mt-4">
          {bookSummary ? (
            <div className="max-h-[28rem] overflow-y-auto rounded-2xl bg-[#F3EDE2] p-4">
              <MarkdownText text={bookSummary} />
            </div>
          ) : waitingForBookSummary ? (
            <ProcessingState
              title="Book summary is being generated"
              description="The backend is still summarizing chunks and chapters. This panel will update automatically when the book summary is ready."
            />
          ) : (
            <StatusMessage tone="warning">
              Book summary is not available yet. Check indexing status or try
              again shortly.
            </StatusMessage>
          )}
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <p className="text-xs font-semibold tracking-wide text-[#7C9885] uppercase">
          Chapter Summaries
        </p>
        <div className="mt-4 flex max-h-[28rem] flex-col gap-3 overflow-y-auto pr-1">
          {chapters.length === 0 ? (
            processing ? (
              <ProcessingState
                title="Chapter summaries are being prepared"
                description="Chapter summary cards will appear as soon as the background indexing process has enough generated summaries."
              />
            ) : (
              <StatusMessage tone="warning">
                No chapters found for this book.
              </StatusMessage>
            )
          ) : null}
          {chapters.map((chapter) => (
            <article
              key={chapter.chapter_id}
              className="rounded-2xl border border-slate-200 bg-[#F3EDE2] p-4"
            >
              <h3 className="text-sm font-semibold text-slate-900">
                Chapter {chapter.number}: {chapter.title}
              </h3>
              {chapter.summary ? (
                <MarkdownText className="mt-3" text={chapter.summary} />
              ) : processing ? (
                <div className="mt-3 flex items-center gap-2 text-sm text-amber-700">
                  <Spinner />
                  Summary is still being generated.
                </div>
              ) : (
                <p className="mt-3 text-sm text-amber-700">
                  Summary is not available yet.
                </p>
              )}
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function ProcessingState({ title, description }) {
  return (
    <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4">
      <div className="flex items-start gap-3">
        <Spinner />
        <div>
          <p className="text-sm font-semibold text-amber-800">{title}</p>
          <p className="mt-1 text-sm leading-5 text-amber-700">{description}</p>
        </div>
      </div>
    </div>
  );
}

function Spinner() {
  return (
    <span className="mt-0.5 h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-amber-200 border-t-amber-700" />
  );
}
