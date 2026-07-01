const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(message, status, payload = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

async function readJsonResponse(response) {
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(
      payload?.message || `Request failed with status ${response.status}.`,
      response.status,
      payload,
    );
  }
  return payload;
}

export async function fetchBooks() {
  const response = await fetch(`${API_BASE_URL}/books`, {
    cache: "no-store",
  });
  return readJsonResponse(response);
}

export async function fetchBookDetail(bookId) {
  const response = await fetch(`${API_BASE_URL}/books/${bookId}`, {
    cache: "no-store",
  });
  return readJsonResponse(response);
}

export async function fetchBookSummary(bookId) {
  const response = await fetch(`${API_BASE_URL}/books/${bookId}/summary`, {
    cache: "no-store",
  });
  return readJsonResponse(response);
}

export async function fetchChapterSummaries(bookId) {
  const response = await fetch(`${API_BASE_URL}/books/${bookId}/chapters`, {
    cache: "no-store",
  });
  return readJsonResponse(response);
}

export async function fetchChatHistory(bookId) {
  const response = await fetch(`${API_BASE_URL}/books/${bookId}/chat-history`, {
    cache: "no-store",
  });
  return readJsonResponse(response);
}

export async function uploadBook(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/books/upload`, {
    method: "POST",
    body: formData,
  });
  return readJsonResponse(response);
}

export async function sendChatMessage({ bookId, question, topK = 5 }) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      book_id: bookId,
      question,
      top_k: topK,
    }),
  });
  return readJsonResponse(response);
}
