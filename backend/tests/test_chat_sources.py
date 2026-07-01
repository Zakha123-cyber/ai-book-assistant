import unittest

from api.chat import _sources_to_response
from services.qa import SourceReference


class ChatSourcesTest(unittest.TestCase):
    def test_formats_chat_sources_for_response(self) -> None:
        sources = [
            SourceReference(
                chunk_id="chunk-0",
                chapter=1,
                chapter_title="Surat dari Loteng",
                page_start=2,
                page_end=2,
                distance=0.77,
            ),
            SourceReference(
                chunk_id="chunk-1",
                chapter=2,
                chapter_title="Persiapan Perjalanan",
                page_start=3,
                page_end=4,
                distance=0.88,
            ),
        ]

        response_sources = _sources_to_response(sources)

        self.assertEqual(response_sources[0].source_index, 1)
        self.assertEqual(
            response_sources[0].label,
            "Chapter 1: Surat dari Loteng; page 2",
        )
        self.assertEqual(response_sources[0].page_range, "page 2")
        self.assertEqual(response_sources[1].source_index, 2)
        self.assertEqual(response_sources[1].page_range, "pages 3-4")


if __name__ == "__main__":
    unittest.main()
