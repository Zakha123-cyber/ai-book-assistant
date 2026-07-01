CHUNK_SUMMARY_TEMPLATE = """Summarize the following passage.

Requirements:
- Maximum 5 bullet points.
- Preserve important terminology.
- Do not introduce new information.
- Keep factual accuracy.
- Write the summary in the same language as the passage.
- Output in Markdown.

Context:
{chunk}
"""

CHAPTER_SUMMARY_TEMPLATE = """You are given summaries from multiple chunks within the same chapter.

Generate a coherent chapter summary.

Requirements:
- Explain the main ideas.
- Remove duplicated information.
- Preserve key concepts.
- Write the summary in the same language as the chunk summaries.
- Output:
  1. Overview
  2. Key Points
  3. Important Terms
  4. Chapter Conclusion

Chunk Summaries:
{chunk_summaries}
"""

BOOK_SUMMARY_TEMPLATE = """Create a complete summary of the book using the provided chapter summaries.

Output format:

# Overview

# Main Concepts

# Key Takeaways

# Important Terms

# Final Conclusion

Language:
Write the summary in the same language as the chapter summaries.

Chapter Summaries:
{chapter_summaries}
"""


def build_chunk_summary_prompt(chunk: str) -> str:
    return CHUNK_SUMMARY_TEMPLATE.format(chunk=chunk.strip())


def build_chapter_summary_prompt(chunk_summaries: list[str]) -> str:
    formatted_summaries = "\n\n".join(
        f"Chunk {index}:\n{summary.strip()}"
        for index, summary in enumerate(chunk_summaries, start=1)
    )
    return CHAPTER_SUMMARY_TEMPLATE.format(chunk_summaries=formatted_summaries)


def build_book_summary_prompt(chapter_summaries: list[str]) -> str:
    formatted_summaries = "\n\n".join(
        f"Chapter {index}:\n{summary.strip()}"
        for index, summary in enumerate(chapter_summaries, start=1)
    )
    return BOOK_SUMMARY_TEMPLATE.format(chapter_summaries=formatted_summaries)
