import unittest
import uuid

from models import Chunk
from services.prompt.summary_prompts import build_chunk_summary_prompt
from services.summarizer import summarize_chunks


class FakeChunkSummaryClient:
    def __init__(self) -> None:
        self.requests: list[str] = []

    async def summarize_chunk(self, chunk_text: str) -> str:
        self.requests.append(chunk_text)
        return f"- Summary for: {chunk_text[:12]}"


class ChunkSummaryTest(unittest.IsolatedAsyncioTestCase):
    def test_builds_chunk_summary_prompt_from_library_template(self) -> None:
        prompt = build_chunk_summary_prompt("Alice follows the White Rabbit.")

        self.assertIn("Maximum 5 bullet points", prompt)
        self.assertIn("Do not introduce new information", prompt)
        self.assertIn("Alice follows the White Rabbit.", prompt)

    async def test_summarizes_each_chunk(self) -> None:
        chunk_1 = Chunk(
            id=uuid.uuid4(),
            chapter_id=uuid.uuid4(),
            chunk_index=0,
            content="Alice follows the White Rabbit.",
        )
        chunk_2 = Chunk(
            id=uuid.uuid4(),
            chapter_id=uuid.uuid4(),
            chunk_index=1,
            content="Alice falls down a deep rabbit-hole.",
        )
        client = FakeChunkSummaryClient()

        results = await summarize_chunks([chunk_1, chunk_2], client=client)

        self.assertEqual(client.requests, [chunk_1.content, chunk_2.content])
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].chunk_id, chunk_1.id)
        self.assertFalse(results[0].cached)
        self.assertTrue(results[0].summary.startswith("- Summary for:"))


if __name__ == "__main__":
    unittest.main()
