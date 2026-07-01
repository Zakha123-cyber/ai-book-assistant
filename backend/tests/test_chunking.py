import unittest

from services.chunker.chapter_detector import DetectedChapter, detect_chapters
from services.chunker.section_detector import DetectedSection, detect_sections
from services.chunker.semantic_chunker import create_semantic_chunks
from services.parser.pdf_parser import ParsedPage, ParsedPDF


class ChapterDetectorTest(unittest.TestCase):
    def test_detects_roman_chapters_with_next_line_titles(self) -> None:
        parsed_pdf = ParsedPDF(
            page_count=3,
            pages=[
                ParsedPage(1, "CHAPTER I.\nDOWN THE RABBIT-HOLE.\nBody one"),
                ParsedPage(2, "More body"),
                ParsedPage(3, "CHAPTER II.\nTHE POOL OF TEARS.\nBody two"),
            ],
        )

        chapters = detect_chapters(parsed_pdf)

        self.assertEqual(len(chapters), 2)
        self.assertEqual(chapters[0].title, "DOWN THE RABBIT-HOLE.")
        self.assertEqual(chapters[0].start_page, 1)
        self.assertEqual(chapters[0].end_page, 2)
        self.assertEqual(chapters[1].title, "THE POOL OF TEARS.")
        self.assertEqual(chapters[1].start_page, 3)

    def test_falls_back_to_single_chapter(self) -> None:
        parsed_pdf = ParsedPDF(
            page_count=1,
            pages=[ParsedPage(1, "No explicit chapter heading.")],
        )

        chapters = detect_chapters(parsed_pdf)

        self.assertEqual(len(chapters), 1)
        self.assertEqual(chapters[0].title, "Untitled Chapter")
        self.assertEqual(chapters[0].text, "No explicit chapter heading.")


class SectionDetectorTest(unittest.TestCase):
    def test_detects_numbered_sections(self) -> None:
        chapter = DetectedChapter(
            number=1,
            title="Introduction",
            start_page=3,
            end_page=5,
            text="1.1 Background\nBody A\n1.2 Method\nBody B",
        )

        sections = detect_sections([chapter])

        self.assertEqual(len(sections), 2)
        self.assertEqual(sections[0].title, "Background")
        self.assertEqual(sections[0].start_page, 3)
        self.assertEqual(sections[0].end_page, 5)
        self.assertEqual(sections[1].title, "Method")

    def test_falls_back_to_main_section(self) -> None:
        chapter = DetectedChapter(
            number=1,
            title="Fiction Chapter",
            start_page=1,
            end_page=2,
            text="Once upon a time.",
        )

        sections = detect_sections([chapter])

        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0].title, "Main Section")
        self.assertEqual(sections[0].chapter_title, "Fiction Chapter")


class SemanticChunkerTest(unittest.TestCase):
    def test_creates_semantic_chunks_with_metadata(self) -> None:
        section = DetectedSection(
            chapter_number=1,
            chapter_title="Introduction",
            number=1,
            title="Background",
            start_page=3,
            end_page=5,
            text="Alpha beta gamma.\n\nDelta epsilon zeta.",
        )

        chunks = create_semantic_chunks(
            [section],
            target_tokens=5,
            overlap_tokens=0,
            base_metadata={"book_id": "book-1"},
        )

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].chunk_id, "chunk-0")
        self.assertEqual(chunks[0].metadata["book_id"], "book-1")
        self.assertEqual(chunks[0].metadata["chapter"], 1)
        self.assertEqual(chunks[0].metadata["section_title"], "Background")
        self.assertEqual(chunks[0].metadata["page_start"], 3)
        self.assertEqual(chunks[0].metadata["page_end"], 5)

    def test_adds_overlap_between_chunks(self) -> None:
        section = DetectedSection(
            chapter_number=1,
            chapter_title="Introduction",
            number=1,
            title="Background",
            start_page=1,
            end_page=1,
            text="Alpha beta gamma.\n\nDelta epsilon zeta.",
        )

        chunks = create_semantic_chunks(
            [section],
            target_tokens=5,
            overlap_tokens=2,
        )

        self.assertEqual(chunks[1].text, "gamma.\n\nDelta epsilon zeta.")

    def test_splits_long_paragraph_by_sentence(self) -> None:
        section = DetectedSection(
            chapter_number=1,
            chapter_title="Introduction",
            number=1,
            title="Background",
            start_page=1,
            end_page=1,
            text="First sentence. Second sentence. Third sentence.",
        )

        chunks = create_semantic_chunks(
            [section],
            target_tokens=4,
            overlap_tokens=0,
        )

        self.assertEqual([chunk.text for chunk in chunks], [
            "First sentence.",
            "Second sentence.",
            "Third sentence.",
        ])


if __name__ == "__main__":
    unittest.main()

