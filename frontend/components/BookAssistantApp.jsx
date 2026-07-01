"use client";

import BookDetail from "./BookDetail";
import BookList from "./BookList";
import ChatPanel from "./ChatPanel";
import SummaryPanels from "./SummaryPanels";
import UploadPanel from "./UploadPanel";
import { useBookDashboard } from "../hooks/useBookDashboard";

export default function BookAssistantApp() {
  const dashboard = useBookDashboard();

  return (
    <main className="min-h-screen bg-neutral-950 px-4 py-6 text-neutral-50 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-6">
        <header className="flex flex-col gap-3 border-b border-neutral-800 pb-5">
          <p className="text-sm font-semibold tracking-wide text-cyan-300 uppercase">
            AI Book Assistant
          </p>
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight text-neutral-50">
                Read, summarize, and question indexed books.
              </h1>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-neutral-300">
                Upload PDFs, inspect summaries, ask retrieval-backed questions,
                and review chat history from one workspace.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-3">
              <div className="rounded-md border border-neutral-800 bg-neutral-900 px-4 py-3">
                <p className="text-neutral-500">Books</p>
                <p className="mt-1 text-xl font-semibold">
                  {dashboard.books.length}
                </p>
              </div>
              <div className="rounded-md border border-neutral-800 bg-neutral-900 px-4 py-3">
                <p className="text-neutral-500">Selected</p>
                <p className="mt-1 text-xl font-semibold">
                  {dashboard.bookDetail ? "1" : "0"}
                </p>
              </div>
              <div className="rounded-md border border-neutral-800 bg-neutral-900 px-4 py-3">
                <p className="text-neutral-500">Messages</p>
                <p className="mt-1 text-xl font-semibold">
                  {dashboard.chatHistory.length}
                </p>
              </div>
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
            />
            <SummaryPanels
              bookSummary={dashboard.bookSummary}
              chapters={dashboard.chapters}
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
