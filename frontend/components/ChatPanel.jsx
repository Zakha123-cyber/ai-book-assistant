"use client";

import { useState } from "react";

import StatusMessage from "./StatusMessage";

function formatDate(value) {
  if (!value) {
    return "";
  }
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function ChatPanel({
  selectedBookId,
  history,
  sending,
  error,
  onSendMessage,
}) {
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);

  async function handleSubmit(event) {
    event.preventDefault();
    const normalizedQuestion = question.trim();
    if (!normalizedQuestion || sending) {
      return;
    }

    const result = await onSendMessage(normalizedQuestion, Number(topK));
    if (result?.success) {
      setQuestion("");
    }
  }

  return (
    <section className="rounded-lg border border-neutral-800 bg-neutral-950 p-5">
      <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold tracking-wide text-cyan-300 uppercase">
            Chat
          </p>
          <h2 className="text-lg font-semibold text-neutral-50">
            Ask this book
          </h2>
        </div>
        <label className="flex items-center gap-2 text-sm text-neutral-300">
          Top K
          <select
            className="rounded-md border border-neutral-700 bg-neutral-900 px-2 py-1 text-neutral-100"
            value={topK}
            onChange={(event) => setTopK(event.target.value)}
          >
            {[3, 5, 8, 10, 15, 20].map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
      </div>

      <form className="mt-4 flex flex-col gap-3" onSubmit={handleSubmit}>
        <textarea
          className="min-h-24 rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm leading-6 text-neutral-100 outline-none focus:border-cyan-500 disabled:cursor-not-allowed disabled:opacity-60"
          placeholder="Ask a question based on the selected book..."
          value={question}
          disabled={!selectedBookId || sending}
          onChange={(event) => setQuestion(event.target.value)}
        />
        <button
          className="self-start rounded-md bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-60"
          type="submit"
          disabled={!selectedBookId || sending || !question.trim()}
        >
          {sending ? "Asking..." : "Send question"}
        </button>
      </form>

      <div className="mt-3">
        <StatusMessage tone="error">{error}</StatusMessage>
      </div>

      <div className="mt-5 flex max-h-[34rem] flex-col gap-4 overflow-y-auto pr-1">
        {history.length === 0 ? (
          <StatusMessage tone="warning">
            No chat history yet for this book.
          </StatusMessage>
        ) : null}
        {history.map((item) => (
          <article
            key={item.id}
            className="rounded-md border border-neutral-800 bg-neutral-900 p-4"
          >
            <div className="flex flex-col gap-1 border-b border-neutral-800 pb-3">
              <p className="text-xs text-neutral-500">
                {formatDate(item.created_at)}
              </p>
              <h3 className="text-sm font-semibold text-neutral-50">
                {item.question}
              </h3>
            </div>
            <pre className="mt-3 font-sans text-sm leading-6 whitespace-pre-wrap text-neutral-300">
              {item.answer}
            </pre>
            {item.sources?.length ? (
              <div className="mt-4 rounded-md border border-neutral-800 bg-neutral-950 p-3">
                <p className="text-xs font-semibold tracking-wide text-neutral-400 uppercase">
                  Sources
                </p>
                <ul className="mt-2 flex flex-col gap-2 text-sm text-neutral-300">
                  {item.sources.map((source) => (
                    <li key={`${item.id}-${source.source_index}`}>
                      {source.source_index}. {source.label}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
