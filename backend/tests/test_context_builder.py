import unittest

from services.qa import (
    SourceReference,
    build_retrieved_context,
    format_page_range,
    format_source_label,
)
from services.retriever import RetrievedChunk


class ContextBuilderTest(unittest.TestCase):
    def test_builds_context_with_source_references(self) -> None:
        chunks = [
            RetrievedChunk(
                id="book-1:chunk-0",
                document="Nara menemukan surat di loteng.",
                metadata={
                    "chunk_id": "chunk-0",
                    "chapter": 1,
                    "chapter_title": "Surat dari Loteng",
                    "page_start": 1,
                    "page_end": 2,
                },
                distance=0.12,
            )
        ]

        result = build_retrieved_context(chunks)

        self.assertIn("[Source 1] Chapter 1: Surat dari Loteng; pages 1-2", result.context)
        self.assertIn("Nara menemukan surat di loteng.", result.context)
        self.assertEqual(len(result.sources), 1)
        self.assertEqual(result.sources[0].chunk_id, "chunk-0")
        self.assertEqual(result.sources[0].chapter, 1)
        self.assertEqual(result.sources[0].page_start, 1)
        self.assertEqual(result.sources[0].distance, 0.12)

    def test_truncates_context_to_max_chars(self) -> None:
        chunks = [
            RetrievedChunk(
                id="book-1:chunk-0",
                document="A" * 200,
                metadata={"chunk_id": "chunk-0"},
                distance=None,
            )
        ]

        result = build_retrieved_context(chunks, max_chars=80)

        self.assertLessEqual(len(result.context), 80)
        self.assertEqual(len(result.sources), 1)

    def test_rejects_invalid_max_chars(self) -> None:
        with self.assertRaises(ValueError):
            build_retrieved_context([], max_chars=0)

    def test_handles_missing_metadata(self) -> None:
        result = build_retrieved_context([
            RetrievedChunk(
                id="book-1:chunk-0",
                document="Plain text.",
                metadata={},
                distance=None,
            )
        ])

        self.assertIn("source unavailable", result.context)
        self.assertIsNone(result.sources[0].chapter)
        self.assertEqual(result.sources[0].chunk_id, "book-1:chunk-0")

    def test_formats_source_label_and_page_range(self) -> None:
        source = SourceReference(
            chunk_id="chunk-0",
            chapter=2,
            chapter_title="Persiapan Perjalanan",
            page_start=3,
            page_end=4,
            distance=0.42,
        )

        self.assertEqual(
            format_source_label(source),
            "Chapter 2: Persiapan Perjalanan; pages 3-4",
        )
        self.assertEqual(format_page_range(source), "pages 3-4")


if __name__ == "__main__":
    unittest.main()
