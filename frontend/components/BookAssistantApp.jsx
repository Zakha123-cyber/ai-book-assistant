"use client";

import Link from "next/link";

import BookDetail from "./BookDetail";
import BookList from "./BookList";
import ChatPanel from "./ChatPanel";
import IndexingStatusCard from "./IndexingStatusCard";
import SummaryPanels from "./SummaryPanels";
import UploadPanel from "./UploadPanel";
import { useBookDashboard } from "../hooks/useBookDashboard";

export default function BookAssistantApp() {
  const dashboard = useBookDashboard();

  return (
    <main className="min-h-screen bg-[#FAF7F0] px-4 py-6 text-slate-900 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <header className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <Link
                  className="text-sm font-semibold text-[#4F6F52] hover:text-[#1E293B]"
                  href="/"
                >
                  AI Book Assistant
                </Link>
                <span className="rounded-full bg-[#DDE7DD] px-3 py-1 text-xs font-semibold text-[#4F6F52]">
                  Reading Workspace
                </span>
              </div>
              <h1 className="mt-3 max-w-3xl text-3xl font-semibold tracking-normal text-slate-900">
                Read, summarize, and question indexed books.
              </h1>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
                Upload PDFs, inspect generated summaries, ask grounded
                questions, and review chat history from one focused workspace.
              </p>
            </div>
            <div className="grid grid-cols-3 gap-3 text-sm">
              <Metric label="Books" value={dashboard.books.length} />
              <Metric label="Selected" value={dashboard.bookDetail ? 1 : 0} />
              <Metric label="Messages" value={dashboard.chatHistory.length} />
            </div>
          </div>
        </header>

        <div className="grid min-h-[calc(100vh-12rem)] gap-6 lg:grid-cols-[22rem_minmax(0,1fr)]">
          <aside className="flex min-h-0 flex-col gap-4">
            <UploadPanel
              uploading={dashboard.uploading}
              uploadError={dashboard.uploadError}
              onUpload={dashboard.handleUpload}
            />
            <BookList
              books={dashboard.books}
              selectedBookId={dashboard.selectedBookId}
              loading={dashboard.loadingBooks}
              error={dashboard.booksError}
              onSelectBook={dashboard.selectBook}
              onRefresh={dashboard.loadBooks}
            />
          </aside>

          <div className="flex min-w-0 flex-col gap-4">
            <BookDetail
              book={dashboard.bookDetail}
              loading={dashboard.loadingDetail}
              error={dashboard.detailError}
              indexingStatus={dashboard.indexingStatus}
            />
            <IndexingStatusCard
              status={dashboard.indexingStatus}
              loading={dashboard.loadingStatus}
              error={dashboard.statusError}
              onRetry={dashboard.handleRetryIndexing}
            />
            <SummaryPanels
              bookSummary={dashboard.bookSummary}
              chapters={dashboard.chapters}
              indexingStatus={dashboard.indexingStatus}
            />
            <ChatPanel
              selectedBookId={dashboard.selectedBookId}
              history={dashboard.chatHistory}
              sending={dashboard.sendingMessage}
              error={dashboard.chatError}
              onSendMessage={dashboard.handleSendMessage}
            />
          </div>
        </div>
      </div>
    </main>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-[#F3EDE2] px-4 py-3">
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <p className="mt-1 text-xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}
