import StatusMessage from "./StatusMessage";

export default function SummaryPanels({ bookSummary, chapters }) {
  return (
    <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
      <div className="rounded-lg border border-neutral-800 bg-neutral-950 p-5">
        <p className="text-xs font-semibold tracking-wide text-cyan-300 uppercase">
          Book Summary
        </p>
        <div className="mt-4">
          {bookSummary ? (
            <pre className="font-sans text-sm leading-6 whitespace-pre-wrap text-neutral-200">
              {bookSummary}
            </pre>
          ) : (
            <StatusMessage tone="warning">
              Book summary is not available yet.
            </StatusMessage>
          )}
        </div>
      </div>

      <div className="rounded-lg border border-neutral-800 bg-neutral-950 p-5">
        <p className="text-xs font-semibold tracking-wide text-cyan-300 uppercase">
          Chapter Summaries
        </p>
        <div className="mt-4 flex max-h-[28rem] flex-col gap-3 overflow-y-auto pr-1">
          {chapters.length === 0 ? (
            <StatusMessage tone="warning">
              No chapters found for this book.
            </StatusMessage>
          ) : null}
          {chapters.map((chapter) => (
            <article
              key={chapter.chapter_id}
              className="rounded-md border border-neutral-800 bg-neutral-900 p-4"
            >
              <h3 className="text-sm font-semibold text-neutral-50">
                Chapter {chapter.number}: {chapter.title}
              </h3>
              {chapter.summary ? (
                <pre className="mt-3 font-sans text-sm leading-6 whitespace-pre-wrap text-neutral-300">
                  {chapter.summary}
                </pre>
              ) : (
                <p className="mt-3 text-sm text-amber-200">
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
