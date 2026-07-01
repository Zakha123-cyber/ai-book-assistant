import unittest

from services.prompt.summary_prompts import build_chapter_summary_prompt
from services.summarizer import summarize_chapter_from_chunk_summaries


class FakeChapterSummaryClient:
    def __init__(self) -> None:
        self.requests: list[list[str]] = []

    async def summarize_chapter(self, chunk_summaries: list[str]) -> str:
        self.requests.append(chunk_summaries)
        return "1. Overview\nAlice follows the White Rabbit."


class ChapterSummaryTest(unittest.IsolatedAsyncioTestCase):
    def test_builds_chapter_summary_prompt_from_library_template(self) -> None:
        prompt = build_chapter_summary_prompt([
            "- Alice sees the White Rabbit.",
            "- Alice falls down the rabbit-hole.",
        ])

        self.assertIn("Generate a coherent chapter summary", prompt)
        self.assertIn("Remove duplicated information", prompt)
        self.assertIn("1. Overview", prompt)
        self.assertIn("Chunk 1:", prompt)
        self.assertIn("- Alice sees the White Rabbit.", prompt)

    async def test_summarizes_chapter_from_chunk_summaries(self) -> None:
        client = FakeChapterSummaryClient()
        chunk_summaries = [
            "- Alice sees the White Rabbit.",
            "- Alice falls down the rabbit-hole.",
        ]

        summary = await summarize_chapter_from_chunk_summaries(
            chunk_summaries,
            client=client,
        )

        self.assertEqual(client.requests, [chunk_summaries])
        self.assertIn("Alice follows the White Rabbit", summary)


if __name__ == "__main__":
    unittest.main()
