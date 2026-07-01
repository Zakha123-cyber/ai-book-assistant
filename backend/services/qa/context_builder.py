from dataclasses import dataclass

from services.retriever import RetrievedChunk

DEFAULT_MAX_CONTEXT_CHARS = 6000


@dataclass(frozen=True)
class SourceReference:
    chunk_id: str
    chapter: int | None
    chapter_title: str | None
    page_start: int | None
    page_end: int | None
    distance: float | None


@dataclass(frozen=True)
class RetrievedContext:
    context: str
    sources: list[SourceReference]


def build_retrieved_context(
    chunks: list[RetrievedChunk],
    max_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
) -> RetrievedContext:
    if max_chars <= 0:
        raise ValueError("max_chars must be greater than zero.")

    context_parts: list[str] = []
    sources: list[SourceReference] = []
    current_length = 0

    for index, chunk in enumerate(chunks, start=1):
        source = _build_source_reference(chunk)
        context_part = _format_context_part(index, chunk, source)
        if current_length + len(context_part) > max_chars:
            remaining_chars = max_chars - current_length
            if remaining_chars <= 0:
                break
            context_part = context_part[:remaining_chars].rstrip()

        if not context_part:
            break

        context_parts.append(context_part)
        sources.append(source)
        current_length += len(context_part)

        if current_length >= max_chars:
            break

    return RetrievedContext(
        context="\n\n".join(context_parts),
        sources=sources,
    )


def _build_source_reference(chunk: RetrievedChunk) -> SourceReference:
    metadata = chunk.metadata
    return SourceReference(
        chunk_id=str(metadata.get("chunk_id", chunk.id)),
        chapter=_int_or_none(metadata.get("chapter")),
        chapter_title=_str_or_none(metadata.get("chapter_title")),
        page_start=_int_or_none(metadata.get("page_start")),
        page_end=_int_or_none(metadata.get("page_end")),
        distance=chunk.distance,
    )


def _format_context_part(
    index: int,
    chunk: RetrievedChunk,
    source: SourceReference,
) -> str:
    source_label = format_source_label(source)
    return f"[Source {index}] {source_label}\n{chunk.document.strip()}"


def format_source_label(source: SourceReference) -> str:
    label_parts: list[str] = []
    if source.chapter is not None:
        chapter_label = f"Chapter {source.chapter}"
        if source.chapter_title:
            chapter_label = f"{chapter_label}: {source.chapter_title}"
        label_parts.append(chapter_label)
    page_range = format_page_range(source)
    if page_range is not None:
        label_parts.append(page_range)
    return "; ".join(label_parts) if label_parts else "source unavailable"


def format_page_range(source: SourceReference) -> str | None:
    if source.page_start is None or source.page_end is None:
        return None
    if source.page_start == source.page_end:
        return f"page {source.page_start}"
    return f"pages {source.page_start}-{source.page_end}"


def _int_or_none(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _str_or_none(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
