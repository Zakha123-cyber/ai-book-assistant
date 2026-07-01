import re
from dataclasses import dataclass

from services.parser.pdf_parser import ParsedPDF, ParsedPage

CHAPTER_HEADING_PATTERNS = [
    re.compile(r"^chapter\s+([0-9]+|[ivxlcdm]+)\b[:.\-\s]*(.*)$", re.IGNORECASE),
    re.compile(r"^chap\.\s+([0-9]+|[ivxlcdm]+)\b[:.\-\s]*(.*)$", re.IGNORECASE),
    re.compile(
        r"^bab\s+([0-9]+|[ivxlcdm]+|[a-z]+)\b[:.\-\s]*(.*)$",
        re.IGNORECASE,
    ),
    re.compile(r"^([0-9]+)\.\s+([A-Z][A-Za-z0-9 ,:'\"\-]{2,})$"),
]
MAX_HEADING_LENGTH = 120
DEFAULT_CHAPTER_TITLE = "Untitled Chapter"


@dataclass(frozen=True)
class DetectedChapter:
    number: int
    title: str
    start_page: int
    end_page: int
    text: str


def detect_chapters(parsed_pdf: ParsedPDF) -> list[DetectedChapter]:
    chapter_starts = _find_chapter_starts(parsed_pdf.pages)
    if not chapter_starts:
        return [_build_single_chapter(parsed_pdf)]

    chapters: list[DetectedChapter] = []
    for index, chapter_start in enumerate(chapter_starts):
        next_start = (
            chapter_starts[index + 1]
            if index + 1 < len(chapter_starts)
            else None
        )
        chapter_pages = _slice_chapter_pages(
            parsed_pdf.pages,
            chapter_start.page_number,
            next_start.page_number if next_start else None,
        )
        end_page = chapter_pages[-1].page_number if chapter_pages else chapter_start.page_number
        chapters.append(
            DetectedChapter(
                number=index + 1,
                title=chapter_start.title,
                start_page=chapter_start.page_number,
                end_page=end_page,
                text=_join_pages(chapter_pages),
            )
        )

    return chapters


@dataclass(frozen=True)
class _ChapterStart:
    page_number: int
    title: str


def _find_chapter_starts(pages: list[ParsedPage]) -> list[_ChapterStart]:
    starts: list[_ChapterStart] = []
    seen_titles: set[tuple[int, str]] = set()

    for page in pages:
        candidate_lines = _candidate_heading_lines(page.text)
        for index, line in enumerate(candidate_lines):
            next_line = (
                candidate_lines[index + 1]
                if index + 1 < len(candidate_lines)
                else None
            )
            title = _parse_chapter_title(line, next_line)
            if title is None:
                continue

            key = (page.page_number, title.casefold())
            if key in seen_titles:
                continue

            starts.append(_ChapterStart(page_number=page.page_number, title=title))
            seen_titles.add(key)
            break

    return starts


def _candidate_heading_lines(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return [line for line in lines if len(line) <= MAX_HEADING_LENGTH]


def _parse_chapter_title(line: str, next_line: str | None = None) -> str | None:
    for index, pattern in enumerate(CHAPTER_HEADING_PATTERNS):
        match = pattern.match(line)
        if match is None:
            continue

        trailing_title = match.group(match.lastindex or 0).strip()
        if trailing_title and not trailing_title.isdigit():
            return trailing_title
        if index < 3 and next_line:
            return next_line.strip()
        return line.strip()

    return None


def _slice_chapter_pages(
    pages: list[ParsedPage],
    start_page: int,
    next_start_page: int | None,
) -> list[ParsedPage]:
    if next_start_page is None:
        return [page for page in pages if page.page_number >= start_page]

    return [
        page
        for page in pages
        if start_page <= page.page_number < next_start_page
    ]


def _build_single_chapter(parsed_pdf: ParsedPDF) -> DetectedChapter:
    start_page = parsed_pdf.pages[0].page_number if parsed_pdf.pages else 1
    end_page = parsed_pdf.pages[-1].page_number if parsed_pdf.pages else 1
    return DetectedChapter(
        number=1,
        title=DEFAULT_CHAPTER_TITLE,
        start_page=start_page,
        end_page=end_page,
        text=parsed_pdf.text,
    )


def _join_pages(pages: list[ParsedPage]) -> str:
    return "\n\n".join(page.text for page in pages if page.text)
