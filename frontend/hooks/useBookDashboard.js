"use client";

import { useCallback, useEffect, useState } from "react";

import {
  ApiError,
  fetchBookDetail,
  fetchBookSummary,
  fetchBookStatus,
  fetchBooks,
  fetchChapterSummaries,
  fetchChatHistory,
  retryBookSummaryIndexing,
  sendChatMessage,
  uploadBook,
} from "../services/api";

function errorMessage(error) {
  if (error instanceof ApiError) {
    return error.message;
  }
  return "Something went wrong. Please try again.";
}

export function useBookDashboard() {
  const [books, setBooks] = useState([]);
  const [selectedBookId, setSelectedBookId] = useState(null);
  const [bookDetail, setBookDetail] = useState(null);
  const [bookSummary, setBookSummary] = useState(null);
  const [chapters, setChapters] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [indexingStatus, setIndexingStatus] = useState(null);
  const [loadingBooks, setLoadingBooks] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [booksError, setBooksError] = useState("");
  const [detailError, setDetailError] = useState("");
  const [statusError, setStatusError] = useState("");
  const [uploadError, setUploadError] = useState("");
  const [chatError, setChatError] = useState("");

  const loadBooks = useCallback(async () => {
    setLoadingBooks(true);
    setBooksError("");
    try {
      const payload = await fetchBooks();
      setBooks(payload.books || []);
      if (!selectedBookId && payload.books?.length) {
        setSelectedBookId(payload.books[0].id);
      }
    } catch (error) {
      setBooksError(errorMessage(error));
    } finally {
      setLoadingBooks(false);
    }
  }, [selectedBookId]);

  const loadBookDetail = useCallback(async (bookId) => {
    if (!bookId) {
      setBookDetail(null);
      setBookSummary(null);
      setChapters([]);
      setChatHistory([]);
      setIndexingStatus(null);
      return;
    }

    setLoadingDetail(true);
    setDetailError("");
    setStatusError("");
    try {
      const [
        detailPayload,
        statusPayload,
        summaryPayload,
        chaptersPayload,
        historyPayload,
      ] = await Promise.allSettled([
        fetchBookDetail(bookId),
        fetchBookStatus(bookId),
        fetchBookSummary(bookId),
        fetchChapterSummaries(bookId),
        fetchChatHistory(bookId),
      ]);

      if (detailPayload.status === "fulfilled") {
        setBookDetail(detailPayload.value.book);
      } else {
        throw detailPayload.reason;
      }

      if (statusPayload.status === "fulfilled") {
        setIndexingStatus(statusPayload.value);
      } else {
        setIndexingStatus(null);
        setStatusError(errorMessage(statusPayload.reason));
      }

      setBookSummary(
        summaryPayload.status === "fulfilled"
          ? summaryPayload.value.summary
          : null,
      );
      setChapters(
        chaptersPayload.status === "fulfilled"
          ? chaptersPayload.value.chapters || []
          : [],
      );
      setChatHistory(
        historyPayload.status === "fulfilled"
          ? sortNewestFirst(historyPayload.value.history || [])
          : [],
      );
    } catch (error) {
      setDetailError(errorMessage(error));
      setBookDetail(null);
      setBookSummary(null);
      setChapters([]);
      setChatHistory([]);
      setIndexingStatus(null);
    } finally {
      setLoadingDetail(false);
    }
  }, []);

  const refreshIndexingStatus = useCallback(async (bookId) => {
    if (!bookId) {
      return null;
    }

    setLoadingStatus(true);
    setStatusError("");
    try {
      const payload = await fetchBookStatus(bookId);
      setIndexingStatus(payload);
      return payload;
    } catch (error) {
      setStatusError(errorMessage(error));
      return null;
    } finally {
      setLoadingStatus(false);
    }
  }, []);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      loadBooks();
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, [loadBooks]);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      loadBookDetail(selectedBookId);
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, [loadBookDetail, selectedBookId]);

  useEffect(() => {
    if (!selectedBookId || indexingStatus?.status === "ready") {
      return undefined;
    }

    const intervalId = window.setInterval(async () => {
      const payload = await refreshIndexingStatus(selectedBookId);
      if (payload?.status === "ready") {
        await loadBookDetail(selectedBookId);
        await loadBooks();
      }
    }, 4000);

    return () => window.clearInterval(intervalId);
  }, [
    indexingStatus?.status,
    loadBookDetail,
    loadBooks,
    refreshIndexingStatus,
    selectedBookId,
  ]);

  async function handleUpload(file) {
    setUploading(true);
    setUploadError("");
    try {
      const payload = await uploadBook(file);
      await loadBooks();
      if (payload.book_id) {
        setSelectedBookId(payload.book_id);
        await refreshIndexingStatus(payload.book_id);
      }
      return payload;
    } catch (error) {
      setUploadError(errorMessage(error));
      return null;
    } finally {
      setUploading(false);
    }
  }

  async function handleRetryIndexing() {
    if (!selectedBookId) {
      setStatusError("Choose a book before retrying indexing.");
      return null;
    }

    setLoadingStatus(true);
    setStatusError("");
    try {
      const payload = await retryBookSummaryIndexing(selectedBookId);
      setIndexingStatus(payload);
      return payload;
    } catch (error) {
      setStatusError(errorMessage(error));
      return null;
    } finally {
      setLoadingStatus(false);
    }
  }

  async function handleSendMessage(question, topK) {
    if (!selectedBookId) {
      setChatError("Choose a book before asking a question.");
      return null;
    }

    setSendingMessage(true);
    setChatError("");
    try {
      const payload = await sendChatMessage({
        bookId: selectedBookId,
        question,
        topK,
      });
      const localMessage = {
        id: `local-${Date.now()}`,
        book_id: selectedBookId,
        question: payload.question,
        answer: payload.answer,
        created_at: new Date().toISOString(),
        sources: payload.sources || [],
      };
      setChatHistory((items) => [localMessage, ...items]);
      return payload;
    } catch (error) {
      setChatError(errorMessage(error));
      return null;
    } finally {
      setSendingMessage(false);
    }
  }

  return {
    books,
    selectedBookId,
    bookDetail,
    bookSummary,
    chapters,
    chatHistory,
    indexingStatus,
    loadingBooks,
    loadingDetail,
    loadingStatus,
    uploading,
    sendingMessage,
    booksError,
    detailError,
    statusError,
    uploadError,
    chatError,
    loadBooks,
    selectBook: setSelectedBookId,
    handleUpload,
    handleRetryIndexing,
    handleSendMessage,
  };
}

function sortNewestFirst(items) {
  return [...items].sort(
    (left, right) => new Date(right.created_at) - new Date(left.created_at),
  );
}
