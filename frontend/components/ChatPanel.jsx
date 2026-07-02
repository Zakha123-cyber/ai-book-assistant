"use client";

import { useState } from "react";

import MarkdownText from "./MarkdownText";
import StatusMessage from "./StatusMessage";
import TypewriterMarkdownText from "./TypewriterMarkdownText";

const suggestedQuestions = [
  "Ringkas buku ini.",
  "Apa tema utama buku ini?",
  "Siapa tokoh utama?",
  "Ringkas Bab 1.",
];

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
  const [animatedMessageIds, setAnimatedMessageIds] = useState(() => new Set());

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
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold tracking-wide text-[#7C9885] uppercase">
            Chat with Book
          </p>
          <h2 className="text-lg font-semibold text-slate-900">
            Ask grounded questions
          </h2>
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-600">
          Top K
          <select
            className="rounded-xl border border-slate-200 bg-white px-2 py-1 text-slate-900 outline-none focus:border-[#7C9885]"
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

      <div className="mt-4 flex flex-wrap gap-2">
        {suggestedQuestions.map((item) => (
          <button
            className="rounded-full border border-slate-200 bg-[#F3EDE2] px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:border-[#7C9885] hover:text-[#4F6F52] disabled:cursor-not-allowed disabled:opacity-60"
            disabled={!selectedBookId || sending}
            key={item}
            type="button"
            onClick={() => setQuestion(item)}
          >
            {item}
          </button>
        ))}
      </div>

      <form className="mt-4 flex flex-col gap-3" onSubmit={handleSubmit}>
        <label className="sr-only" htmlFor="book-question">
          Ask something about this book
        </label>
        <textarea
          className="min-h-24 rounded-2xl border border-slate-200 bg-[#FAF7F0] px-4 py-3 text-sm leading-6 text-slate-900 outline-none focus:border-[#7C9885] disabled:cursor-not-allowed disabled:opacity-60"
          id="book-question"
          placeholder="Ask something about this book..."
          value={question}
          disabled={!selectedBookId || sending}
          onChange={(event) => setQuestion(event.target.value)}
        />
        <button
          className="self-start rounded-xl bg-[#4F6F52] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#405b43] disabled:cursor-not-allowed disabled:opacity-60"
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
        {sending ? <ChatLoadingMessage /> : null}
        {history.length === 0 ? (
          <StatusMessage tone="warning">
            No chat history yet for this book.
          </StatusMessage>
        ) : null}
        {history.map((item) => (
          <ChatMessage
            animated={item.id?.startsWith("local-")}
            animationDone={animatedMessageIds.has(item.id)}
            item={item}
            key={item.id}
            onAnimationDone={() =>
              setAnimatedMessageIds((current) => {
                const next = new Set(current);
                next.add(item.id);
                return next;
              })
            }
          />
        ))}
      </div>
    </section>
  );
}

function ChatMessage({ item, animated, animationDone, onAnimationDone }) {
  const shouldAnimate = animated && !animationDone;

  return (
    <article className="rounded-2xl border border-slate-200 bg-[#FAF7F0] p-4">
      <div className="flex flex-col gap-1 border-b border-slate-200 pb-3">
        <p className="text-xs text-slate-500">{formatDate(item.created_at)}</p>
        <h3 className="text-sm font-semibold text-slate-900">
          {item.question}
        </h3>
      </div>
      {shouldAnimate ? (
        <TypewriterMarkdownText
          className="mt-3"
          enabled
          text={item.answer}
          onDone={onAnimationDone}
        />
      ) : (
        <MarkdownText className="mt-3" text={item.answer} />
      )}
      {item.sources?.length ? (
        <div
          className={`mt-4 rounded-2xl border border-slate-200 bg-white p-4 transition-opacity duration-300 ${
            shouldAnimate ? "opacity-40" : "opacity-100"
          }`}
        >
          <p className="text-xs font-semibold tracking-wide text-[#7C9885] uppercase">
            Sources
          </p>
          <ul className="mt-3 flex flex-col gap-3 text-sm text-slate-700">
            {item.sources.map((source) => (
              <li
                className="rounded-xl border border-slate-200 bg-[#F3EDE2] p-3"
                key={`${item.id}-${source.source_index}`}
              >
                <p className="font-semibold text-slate-900">
                  Source {source.source_index}
                </p>
                <p className="mt-1">{source.label}</p>
                {typeof source.distance === "number" ? (
                  <p className="mt-1 text-xs text-slate-500">
                    Distance {source.distance.toFixed(3)}
                  </p>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </article>
  );
}

function ChatLoadingMessage() {
  return (
    <article className="rounded-2xl border border-slate-200 bg-[#FAF7F0] p-4">
      <div className="flex items-start gap-3">
        <span className="mt-1 h-5 w-5 shrink-0 animate-spin rounded-full border-2 border-[#DDE7DD] border-t-[#4F6F52]" />
        <div>
          <p className="text-sm font-semibold text-slate-900">
            AI is reading the book context
          </p>
          <div className="mt-2 flex gap-1">
            <span className="h-2 w-2 animate-bounce rounded-full bg-[#7C9885]" />
            <span className="h-2 w-2 animate-bounce rounded-full bg-[#7C9885] [animation-delay:120ms]" />
            <span className="h-2 w-2 animate-bounce rounded-full bg-[#7C9885] [animation-delay:240ms]" />
          </div>
        </div>
      </div>
    </article>
  );
}
