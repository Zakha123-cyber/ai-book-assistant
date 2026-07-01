import re
from dataclasses import dataclass

from services.chunker.chapter_detector import DetectedChapter

SECTION_HEADING_PATTERNS = [
    re.compile(r"^([0-9]+\.[0-9]+(?:\.[0-9]+)*)\s+(.+)$"),
    re.compile(r"^section\s+([0-9]+|[ivxlcdm]+)\b[:.\-\s]*(.*)$", re.IGNORECASE),
]
MAX_SECTION_HEADING_LENGTH = 120
DEFAULT_SECTION_TITLE = "Main Section"


@dataclass(frozen=True)
class DetectedSection:
    chapter_number: int
    chapter_title: str
    number: int
    title: str
    start_page: int
    end_page: int
    text: str


def detect_sections(chapters: list[DetectedChapter]) -> list[DetectedSection]:
    sections: list[DetectedSection] = []
    for chapter in chapters:
        sections.extend(_detect_chapter_sections(chapter))
    return sections


def _detect_chapter_sections(chapter: DetectedChapter) -> list[DetectedSection]:
    section_starts = _find_section_starts(chapter.text)
    if not section_starts:
        return [
            DetectedSection(
                chapter_number=chapter.number,
                chapter_title=chapter.title,
                number=1,
                title=DEFAULT_SECTION_TITLE,
                start_page=chapter.start_page,
                end_page=chapter.end_page,
                text=chapter.text,
            )
        ]

    sections: list[DetectedSection] = []
    lines = chapter.text.splitlines()
    for index, start in enumerate(section_starts):
        next_start = (
            section_starts[index + 1]
            if index + 1 < len(section_starts)
            else None
        )
        end_index = next_start.line_index if next_start else len(lines)
        section_text = "\n".join(lines[start.line_index:end_index]).strip()
        sections.append(
            DetectedSection(
                chapter_number=chapter.number,
                chapter_title=chapter.title,
                number=index + 1,
                title=start.title,
                start_page=chapter.start_page,
                end_page=chapter.end_page,
                text=section_text,
            )
        )

    return sections


@dataclass(frozen=True)
class _SectionStart:
    line_index: int
    title: str


def _find_section_starts(text: str) -> list[_SectionStart]:
    starts: list[_SectionStart] = []
    for index, line in enumerate(text.splitlines()):
        normalized_line = line.strip()
        if len(normalized_line) > MAX_SECTION_HEADING_LENGTH:
            continue

        title = _parse_section_title(normalized_line)
        if title is None:
            continue

        starts.append(_SectionStart(line_index=index, title=title))

    return starts


def _parse_section_title(line: str) -> str | None:
    for pattern in SECTION_HEADING_PATTERNS:
        match = pattern.match(line)
        if match is None:
            continue

        trailing_title = match.group(match.lastindex or 0).strip()
        if trailing_title and not trailing_title.isdigit():
            return trailing_title
        return line

    return None
