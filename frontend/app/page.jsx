export default function HomePage() {
  return (
    <main className="min-h-screen bg-neutral-950 px-6 py-10 text-neutral-50">
      <section className="mx-auto flex max-w-5xl flex-col gap-6">
        <p className="text-sm font-medium tracking-wide text-cyan-300 uppercase">
          AI Book Assistant
        </p>
        <h1 className="max-w-3xl text-4xl leading-tight font-semibold">
          Upload, summarize, and ask questions about long books.
        </h1>
        <p className="max-w-2xl text-base leading-7 text-neutral-300">
          The frontend shell is ready. Book upload, summaries, and chat views
          will be added in their scheduled tasks.
        </p>
      </section>
    </main>
  );
}
