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
      setSuccessMessage(
        "Upload accepted. Indexing and summaries will continue.",
      );
    }
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-4">
        <p className="text-xs font-semibold tracking-wide text-[#7C9885] uppercase">
          Upload
        </p>
        <h2 className="text-lg font-semibold text-slate-900">Add a PDF book</h2>
        <p className="mt-1 text-sm leading-5 text-slate-500">
          Text-based PDF files work best for extraction and retrieval.
        </p>
      </div>

      <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
        <label className="cursor-pointer rounded-2xl border border-dashed border-[#7C9885]/70 bg-[#F3EDE2] p-4 text-center transition hover:border-[#4F6F52]">
          <input
            className="sr-only"
            type="file"
            accept="application/pdf,.pdf"
            disabled={uploading}
            onChange={(event) =>
              setSelectedFile(event.target.files?.[0] || null)
            }
          />
          <span className="block text-sm font-semibold text-slate-800">
            {selectedFile ? selectedFile.name : "Choose or drop a PDF"}
          </span>
          <span className="mt-1 block text-xs text-slate-500">
            Maximum size follows backend upload settings.
          </span>
        </label>
        <button
          className="rounded-xl bg-[#4F6F52] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-[#405b43] disabled:cursor-not-allowed disabled:opacity-60"
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
