"use client";

import { useCallback, useEffect, useState } from "react";

import {
  ApiError,
  fetchBookDetail,
  fetchBookSummary,
  fetchBooks,
  fetchChapterSummaries,
  fetchChatHistory,
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
  const [loadingBooks, setLoadingBooks] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [booksError, setBooksError] = useState("");
  const [detailError, setDetailError] = useState("");
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
      return;
    }

    setLoadingDetail(true);
    setDetailError("");
    try {
      const [detailPayload, summaryPayload, chaptersPayload, historyPayload] =
        await Promise.allSettled([
          fetchBookDetail(bookId),
          fetchBookSummary(bookId),
          fetchChapterSummaries(bookId),
          fetchChatHistory(bookId),
        ]);

      if (detailPayload.status === "fulfilled") {
        setBookDetail(detailPayload.value.book);
      } else {
        throw detailPayload.reason;
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
          ? historyPayload.value.history || []
          : [],
      );
    } catch (error) {
      setDetailError(errorMessage(error));
      setBookDetail(null);
      setBookSummary(null);
      setChapters([]);
      setChatHistory([]);
    } finally {
      setLoadingDetail(false);
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

  async function handleUpload(file) {
    setUploading(true);
    setUploadError("");
    try {
      const payload = await uploadBook(file);
      await loadBooks();
      if (payload.book_id) {
        setSelectedBookId(payload.book_id);
      }
      return payload;
    } catch (error) {
      setUploadError(errorMessage(error));
      return null;
    } finally {
      setUploading(false);
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
      setChatHistory((items) => [...items, localMessage]);
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
    loadingBooks,
    loadingDetail,
    uploading,
    sendingMessage,
    booksError,
    detailError,
    uploadError,
    chatError,
    loadBooks,
    selectBook: setSelectedBookId,
    handleUpload,
    handleSendMessage,
  };
}
