import re
from dataclasses import dataclass

from services.chunker.section_detector import DetectedSection

TARGET_CHUNK_TOKENS = 500
OVERLAP_TOKENS = 100
PARAGRAPH_SPLIT_PATTERN = re.compile(r"\n\s*\n+")
SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")
TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]")


@dataclass(frozen=True)
class SemanticChunk:
    chunk_id: str
    chapter_number: int
    chapter_title: str
    section_number: int
    section_title: str
    chunk_index: int
    text: str
    token_count: int
    metadata: dict[str, int | str]


def create_semantic_chunks(
    sections: list[DetectedSection],
    target_tokens: int = TARGET_CHUNK_TOKENS,
    overlap_tokens: int = OVERLAP_TOKENS,
    base_metadata: dict[str, int | str] | None = None,
) -> list[SemanticChunk]:
    chunks: list[SemanticChunk] = []
    chunk_index = 0
    base_metadata = base_metadata or {}

    for section in sections:
        section_chunks = _chunk_section(section, target_tokens, overlap_tokens)
        for section_chunk in section_chunks:
            chunks.append(
                SemanticChunk(
                    chunk_id=f"chunk-{chunk_index}",
                    chapter_number=section.chapter_number,
                    chapter_title=section.chapter_title,
                    section_number=section.number,
                    section_title=section.title,
                    chunk_index=chunk_index,
                    text=section_chunk,
                    token_count=count_tokens(section_chunk),
                    metadata={
                        **base_metadata,
                        "chunk_id": f"chunk-{chunk_index}",
                        "chapter": section.chapter_number,
                        "chapter_title": section.chapter_title,
                        "section": section.number,
                        "section_title": section.title,
                        "page_start": section.start_page,
                        "page_end": section.end_page,
                    },
                )
            )
            chunk_index += 1

    return chunks


def count_tokens(text: str) -> int:
    return len(TOKEN_PATTERN.findall(text))


def _chunk_section(
    section: DetectedSection,
    target_tokens: int,
    overlap_tokens: int,
) -> list[str]:
    units = _semantic_units(section.text, target_tokens)
    base_chunks: list[str] = []
    current_units: list[str] = []
    current_tokens = 0

    for unit in units:
        unit_tokens = count_tokens(unit)
        if current_units and current_tokens + unit_tokens > target_tokens:
            base_chunks.append("\n\n".join(current_units).strip())
            current_units = []
            current_tokens = 0

        current_units.append(unit)
        current_tokens += unit_tokens

    if current_units:
        base_chunks.append("\n\n".join(current_units).strip())

    return _apply_chunk_overlap(
        [chunk for chunk in base_chunks if chunk],
        overlap_tokens,
    )


def _semantic_units(text: str, target_tokens: int) -> list[str]:
    paragraphs = [
        paragraph.strip()
        for paragraph in PARAGRAPH_SPLIT_PATTERN.split(text)
        if paragraph.strip()
    ]

    units: list[str] = []
    for paragraph in paragraphs:
        if count_tokens(paragraph) <= target_tokens:
            units.append(paragraph)
            continue

        units.extend(_split_long_paragraph(paragraph, target_tokens))

    return units


def _split_long_paragraph(paragraph: str, target_tokens: int) -> list[str]:
    sentences = [
        sentence.strip()
        for sentence in SENTENCE_SPLIT_PATTERN.split(paragraph)
        if sentence.strip()
    ]
    if not sentences:
        return [paragraph]

    units: list[str] = []
    current_sentences: list[str] = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)
        if current_sentences and current_tokens + sentence_tokens > target_tokens:
            units.append(" ".join(current_sentences).strip())
            current_sentences = []
            current_tokens = 0

        current_sentences.append(sentence)
        current_tokens += sentence_tokens

    if current_sentences:
        units.append(" ".join(current_sentences).strip())

    return units


def _apply_chunk_overlap(chunks: list[str], overlap_tokens: int) -> list[str]:
    if overlap_tokens <= 0 or len(chunks) <= 1:
        return chunks

    overlapped_chunks = [chunks[0]]
    for previous_chunk, current_chunk in zip(chunks, chunks[1:]):
        overlap_text = _tail_tokens(previous_chunk, overlap_tokens)
        if overlap_text:
            overlapped_chunks.append(f"{overlap_text}\n\n{current_chunk}")
            continue

        overlapped_chunks.append(current_chunk)

    return overlapped_chunks


def _tail_tokens(text: str, token_count: int) -> str:
    tokens = TOKEN_PATTERN.findall(text)
    return _join_tokens(tokens[-token_count:])


def _join_tokens(tokens: list[str]) -> str:
    text = " ".join(tokens)
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)
    text = re.sub(r"([(\"'])\s+", r"\1", text)
    text = re.sub(r"\s+([)\"'])", r"\1", text)
    return text
