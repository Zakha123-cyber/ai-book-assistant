<<<<<<< Updated upstream
import { fetchBooks } from "../services/books";

function formatDate(value) {
  return new Intl.DateTimeFormat("id-ID", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function filenameLabel(filename) {
  const parts = filename.split(/[\\/]/);
  return parts[parts.length - 1] || filename;
}

export default async function HomePage() {
  let books = [];
  let error = null;

  try {
    books = await fetchBooks();
  } catch (fetchError) {
    error = fetchError;
  }

  return (
    <main className="min-h-screen bg-zinc-100 px-5 py-6 text-zinc-950">
      <section className="mx-auto flex max-w-6xl flex-col gap-5">
        <header className="flex flex-col justify-between gap-3 border-b border-zinc-300 pb-4 sm:flex-row sm:items-end">
          <div>
            <p className="text-xs font-semibold tracking-[0.18em] text-teal-700 uppercase">
              AI Book Assistant
            </p>
            <h1 className="mt-2 text-2xl font-semibold tracking-normal text-zinc-950">
              Books
            </h1>
          </div>
          <div className="text-sm text-zinc-600">
            {books.length} indexed {books.length === 1 ? "book" : "books"}
          </div>
        </header>

        {error ? (
          <div className="border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-900">
            Backend unavailable. Start the API server and refresh this page.
          </div>
        ) : null}

        {!error && books.length === 0 ? (
          <div className="border border-zinc-300 bg-white px-4 py-8 text-center text-sm text-zinc-600">
            No books indexed yet.
          </div>
        ) : null}

        {!error && books.length > 0 ? (
          <div className="overflow-x-auto border border-zinc-300 bg-white">
            <table className="min-w-full border-collapse text-left text-sm">
              <thead className="bg-zinc-200 text-xs font-semibold tracking-[0.08em] text-zinc-600 uppercase">
                <tr>
                  <th className="w-[38%] px-4 py-3">Title</th>
                  <th className="w-[22%] px-4 py-3">Author</th>
                  <th className="w-[26%] px-4 py-3">File</th>
                  <th className="w-[14%] px-4 py-3">Indexed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-200">
                {books.map((book) => (
                  <tr key={book.id} className="hover:bg-zinc-50">
                    <td className="px-4 py-3 align-top">
                      <div className="font-medium text-zinc-950">
                        {book.title}
                      </div>
                      <div className="mt-1 font-mono text-xs text-zinc-500">
                        {book.id}
                      </div>
                    </td>
                    <td className="px-4 py-3 align-top text-zinc-700">
                      {book.author || "-"}
                    </td>
                    <td className="px-4 py-3 align-top text-zinc-700">
                      {filenameLabel(book.filename)}
                    </td>
                    <td className="px-4 py-3 align-top text-zinc-700">
                      {formatDate(book.uploaded_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>
    </main>
  );
=======
import BookAssistantApp from "../components/BookAssistantApp";

export default function HomePage() {
  return <BookAssistantApp />;
>>>>>>> Stashed changes
}
