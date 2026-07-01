import unittest

from services.prompt.summary_prompts import build_book_summary_prompt
from services.summarizer import summarize_book_from_chapter_summaries


class FakeBookSummaryClient:
    def __init__(self) -> None:
        self.requests: list[list[str]] = []

    async def summarize_book(self, chapter_summaries: list[str]) -> str:
        self.requests.append(chapter_summaries)
        return "# Overview\nAlice explores Wonderland."


class BookSummaryTest(unittest.IsolatedAsyncioTestCase):
    def test_builds_book_summary_prompt_from_library_template(self) -> None:
        prompt = build_book_summary_prompt([
            "Chapter 1 summary.",
            "Chapter 2 summary.",
        ])

        self.assertIn("Create a complete summary of the book", prompt)
        self.assertIn("# Overview", prompt)
        self.assertIn("# Key Takeaways", prompt)
        self.assertIn("Chapter 1:", prompt)
        self.assertIn("Chapter 1 summary.", prompt)

    async def test_summarizes_book_from_chapter_summaries(self) -> None:
        client = FakeBookSummaryClient()
        chapter_summaries = [
            "Alice follows the White Rabbit.",
            "Alice enters a pool of tears.",
        ]

        summary = await summarize_book_from_chapter_summaries(
            chapter_summaries,
            client=client,
        )

        self.assertEqual(client.requests, [chapter_summaries])
        self.assertIn("Alice explores Wonderland", summary)


if __name__ == "__main__":
    unittest.main()
