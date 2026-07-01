const API_BASE_URL =
  process.env.BACKEND_API_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8000";

export async function fetchBooks() {
  const response = await fetch(`${API_BASE_URL}/books`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch books: ${response.status}`);
  }

  const payload = await response.json();
  return payload.books ?? [];
}
