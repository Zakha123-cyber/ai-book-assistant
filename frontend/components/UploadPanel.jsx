"use client";

import { useState } from "react";

import StatusMessage from "./StatusMessage";

export default function UploadPanel({ uploading, uploadError, onUpload }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [localError, setLocalError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setLocalError("");
    setSuccessMessage("");

    if (!selectedFile) {
      setLocalError("Choose a PDF file first.");
      return;
    }
    if (selectedFile.type && selectedFile.type !== "application/pdf") {
      setLocalError("Only PDF files are supported.");
      return;
    }
    if (!selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setLocalError("The selected file must use a .pdf extension.");
      return;
    }

    const result = await onUpload(selectedFile);
    if (result?.success) {
      setSelectedFile(null);
      event.currentTarget.reset();
      setSuccessMessage("Upload indexed successfully.");
    }
  }

  return (
    <section className="rounded-lg border border-neutral-800 bg-neutral-950 p-4">
      <div className="mb-4">
        <p className="text-xs font-semibold tracking-wide text-cyan-300 uppercase">
          Upload
        </p>
        <h2 className="text-lg font-semibold text-neutral-50">
          Add a PDF book
        </h2>
      </div>

      <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
        <input
          className="rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-neutral-100 file:mr-3 file:rounded-md file:border-0 file:bg-cyan-600 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-white"
          type="file"
          accept="application/pdf,.pdf"
          disabled={uploading}
          onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
        />
        <button
          className="rounded-md bg-cyan-600 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-500 disabled:cursor-not-allowed disabled:opacity-60"
          type="submit"
          disabled={uploading}
        >
          {uploading ? "Indexing..." : "Upload and index"}
        </button>
      </form>

      <div className="mt-3 flex flex-col gap-2">
        <StatusMessage tone="error">{localError || uploadError}</StatusMessage>
        <StatusMessage tone="success">{successMessage}</StatusMessage>
      </div>
    </section>
  );
}
