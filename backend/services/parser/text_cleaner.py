from collections import Counter
import re

from services.parser.pdf_parser import ParsedPDF, ParsedPage

EDGE_LINE_LIMIT = 2
MIN_REPEATED_PAGES = 3
REPEATED_PAGE_RATIO = 0.6
PAGE_NUMBER_PATTERN = re.compile(r"^(?:page\s*)?-?\s*\d+\s*-?$", re.IGNORECASE)
INLINE_WHITESPACE_PATTERN = re.compile(r"[ \t\f\v]+")
MULTIPLE_BLANK_LINES_PATTERN = re.compile(r"\n{3,}")


def remove_repeated_headers_footers(parsed_pdf: ParsedPDF) -> ParsedPDF:
    repeated_lines = _find_repeated_edge_lines(parsed_pdf.pages)
    if not repeated_lines:
        return parsed_pdf

    cleaned_pages = [
        ParsedPage(
            page_number=page.page_number,
            text=_remove_repeated_edge_lines(page.text, repeated_lines),
        )
        for page in parsed_pdf.pages
    ]
    return ParsedPDF(page_count=parsed_pdf.page_count, pages=cleaned_pages)


def remove_page_numbers(parsed_pdf: ParsedPDF) -> ParsedPDF:
    cleaned_pages = [
        ParsedPage(
            page_number=page.page_number,
            text=_remove_edge_page_number_lines(page.text),
        )
        for page in parsed_pdf.pages
    ]
    return ParsedPDF(page_count=parsed_pdf.page_count, pages=cleaned_pages)


def normalize_whitespace(parsed_pdf: ParsedPDF) -> ParsedPDF:
    cleaned_pages = [
        ParsedPage(
            page_number=page.page_number,
            text=_normalize_whitespace_text(page.text),
        )
        for page in parsed_pdf.pages
    ]
    return ParsedPDF(page_count=parsed_pdf.page_count, pages=cleaned_pages)


def _find_repeated_edge_lines(pages: list[ParsedPage]) -> set[str]:
    candidates: list[str] = []
    for page in pages:
        lines = _non_empty_lines(page.text)
        edge_lines = lines[:EDGE_LINE_LIMIT] + lines[-EDGE_LINE_LIMIT:]
        candidates.extend(_normalize_line(line) for line in edge_lines)

    if not candidates:
        return set()

    min_count = max(MIN_REPEATED_PAGES, int(len(pages) * REPEATED_PAGE_RATIO))
    line_counts = Counter(candidates)
    return {
        line
        for line, count in line_counts.items()
        if line and count >= min_count
    }


def _remove_repeated_edge_lines(text: str, repeated_lines: set[str]) -> str:
    lines = text.splitlines()
    if not lines:
        return text

    start = 0
    end = len(lines)

    for index, line in enumerate(lines[:EDGE_LINE_LIMIT]):
        if _normalize_line(line) in repeated_lines:
            start = index + 1

    trailing_lines = lines[max(0, len(lines) - EDGE_LINE_LIMIT) :]
    for offset, line in enumerate(reversed(trailing_lines), start=1):
        if _normalize_line(line) in repeated_lines:
            end = len(lines) - offset

    return "\n".join(lines[start:end]).strip()


def _remove_edge_page_number_lines(text: str) -> str:
    lines = text.splitlines()
    if not lines:
        return text

    start = 0
    end = len(lines)

    while start < min(EDGE_LINE_LIMIT, len(lines)):
        if not _is_page_number_line(lines[start]):
            break
        start += 1

    trailing_checks = 0
    while end > start and trailing_checks < EDGE_LINE_LIMIT:
        if not _is_page_number_line(lines[end - 1]):
            break
        end -= 1
        trailing_checks += 1

    return "\n".join(lines[start:end]).strip()


def _is_page_number_line(line: str) -> bool:
    return bool(PAGE_NUMBER_PATTERN.fullmatch(line.strip()))


def _normalize_whitespace_text(text: str) -> str:
    normalized_lines = [
        INLINE_WHITESPACE_PATTERN.sub(" ", line).strip()
        for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    ]
    normalized_text = "\n".join(normalized_lines).strip()
    return MULTIPLE_BLANK_LINES_PATTERN.sub("\n\n", normalized_text)


def _non_empty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _normalize_line(line: str) -> str:
    return " ".join(line.casefold().split())
