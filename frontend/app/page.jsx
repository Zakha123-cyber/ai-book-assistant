import Link from "next/link";

const features = [
  {
    title: "Layered summaries",
    description:
      "Generate book, chapter, and chunk summaries so long PDFs become easier to inspect.",
  },
  {
    title: "Chat with context",
    description:
      "Ask questions about an uploaded book and keep the answer grounded in retrieved passages.",
  },
  {
    title: "Traceable sources",
    description:
      "Review chapter, page, and source references behind every retrieval-backed answer.",
  },
];

const steps = [
  "Upload a text-based PDF",
  "Wait for indexing and summaries",
  "Ask questions with source references",
];

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#FAF7F0] text-slate-900">
      <nav className="border-b border-slate-200/80 bg-[#FAF7F0]/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <Link className="text-lg font-semibold tracking-tight" href="/">
            AI Book Assistant
          </Link>
          <div className="flex items-center gap-3">
            <a
              className="hidden text-sm font-medium text-slate-600 hover:text-slate-900 sm:inline"
              href="#features"
            >
              Features
            </a>
            <a
              className="hidden text-sm font-medium text-slate-600 hover:text-slate-900 sm:inline"
              href="#workflow"
            >
              Workflow
            </a>
            <Link
              className="rounded-xl bg-[#4F6F52] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#405b43]"
              href="/dashboard"
            >
              Start Reading
            </Link>
          </div>
        </div>
      </nav>

      <section className="mx-auto grid max-w-7xl gap-10 px-4 py-16 sm:px-6 lg:grid-cols-[1fr_0.9fr] lg:px-8 lg:py-20">
        <div className="flex flex-col justify-center">
          <p className="mb-4 w-fit rounded-full border border-[#D6A85A]/40 bg-white/70 px-4 py-2 text-sm font-semibold text-[#4F6F52]">
            Modern Literary Intelligence
          </p>
          <h1 className="max-w-4xl text-5xl leading-tight font-bold tracking-normal text-slate-900 md:text-6xl">
            Understand books faster with AI-powered reading assistance.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
            Upload a book, generate chapter summaries, ask questions, and trace
            every answer back to its source.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link
              className="rounded-xl bg-[#4F6F52] px-5 py-3 text-center text-sm font-semibold text-white shadow-md transition hover:bg-[#405b43]"
              href="/dashboard"
            >
              Start Reading
            </Link>
            <a
              className="rounded-xl border border-slate-300 bg-white/70 px-5 py-3 text-center text-sm font-semibold text-slate-800 transition hover:border-[#7C9885] hover:text-[#4F6F52]"
              href="#demo"
            >
              View Demo
            </a>
          </div>
        </div>

        <div id="demo" className="relative min-h-[34rem]">
          <div className="absolute inset-x-0 top-8 rounded-2xl border border-slate-200 bg-white p-5 shadow-md">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div>
                <p className="text-xs font-semibold tracking-wide text-[#7C9885] uppercase">
                  Book Workspace
                </p>
                <h2 className="mt-1 text-xl font-semibold">
                  Jejak Cahaya di Desa Arunika
                </h2>
              </div>
              <span className="rounded-full bg-[#DDE7DD] px-3 py-1 text-xs font-semibold text-[#4F6F52]">
                Ready
              </span>
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              {["8 chapters", "8 chunks", "12 sources"].map((item) => (
                <div
                  className="rounded-xl border border-slate-200 bg-[#F3EDE2] p-4 text-sm font-semibold text-slate-700"
                  key={item}
                >
                  {item}
                </div>
              ))}
            </div>
            <div className="mt-5 rounded-2xl border border-slate-200 p-4">
              <p className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
                AI Summary
              </p>
              <p className="mt-3 text-sm leading-6 text-slate-700">
                Nara discovers an old compass, a weathered map, and a letter
                that leads her friends toward the forgotten lighthouse.
              </p>
            </div>
          </div>

          <div className="absolute bottom-20 left-0 max-w-xs rounded-2xl border border-slate-200 bg-white p-4 shadow-md">
            <p className="text-xs font-semibold tracking-wide text-[#A67C52] uppercase">
              Source Reference
            </p>
            <p className="mt-2 text-sm font-semibold text-slate-800">
              Chapter 4 - Bertemu Pak Wira
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Page 5 · relevance 91%
            </p>
          </div>

          <div className="absolute right-0 bottom-0 max-w-sm rounded-2xl border border-slate-200 bg-[#1E293B] p-5 text-white shadow-md">
            <p className="text-xs font-semibold tracking-wide text-[#D6A85A] uppercase">
              Ask the book
            </p>
            <p className="mt-3 text-sm leading-6 text-slate-200">
              “Apa pesan utama dari perjalanan Nara?”
            </p>
          </div>
        </div>
      </section>

      <section
        id="features"
        className="border-y border-slate-200 bg-white/70 py-14"
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold tracking-wide text-[#7C9885] uppercase">
              Features
            </p>
            <h2 className="mt-2 text-3xl font-semibold text-slate-900">
              Built for reading, understanding, and verifying.
            </h2>
          </div>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {features.map((feature) => (
              <article
                className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
                key={feature.title}
              >
                <h3 className="text-lg font-semibold text-slate-900">
                  {feature.title}
                </h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">
                  {feature.description}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section
        id="workflow"
        className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8"
      >
        <div className="grid gap-8 lg:grid-cols-[0.8fr_1fr] lg:items-center">
          <div>
            <p className="text-sm font-semibold tracking-wide text-[#7C9885] uppercase">
              How it works
            </p>
            <h2 className="mt-2 text-3xl font-semibold text-slate-900">
              From PDF to cited answers.
            </h2>
            <p className="mt-4 text-sm leading-6 text-slate-600">
              The app indexes your uploaded book, prepares summaries in the
              background, then keeps every answer connected to the book context.
            </p>
          </div>
          <div className="grid gap-3">
            {steps.map((step, index) => (
              <div
                className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
                key={step}
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-[#DDE7DD] text-sm font-bold text-[#4F6F52]">
                  {index + 1}
                </span>
                <p className="font-medium text-slate-800">{step}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-[#1E293B] px-4 py-14 text-white sm:px-6 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-6 lg:flex-row lg:items-center">
          <div>
            <p className="text-sm font-semibold tracking-wide text-[#D6A85A] uppercase">
              Ready to explore a book?
            </p>
            <h2 className="mt-2 text-3xl font-semibold">
              Open the reading workspace and upload your first PDF.
            </h2>
          </div>
          <Link
            className="w-fit rounded-xl bg-white px-5 py-3 text-sm font-semibold text-slate-900 transition hover:bg-[#F3EDE2]"
            href="/dashboard"
          >
            Go to Dashboard
          </Link>
        </div>
      </section>

      <footer className="bg-[#FAF7F0] px-4 py-6 text-sm text-slate-500 sm:px-6 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-2 sm:flex-row">
          <p>AI Book Assistant</p>
          <p>Read. Understand. Ask. Verify.</p>
        </div>
      </footer>
    </main>
  );
}
