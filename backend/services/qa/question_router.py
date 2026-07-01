import re
from dataclasses import dataclass
from enum import StrEnum


class QuestionMode(StrEnum):
    OUT_OF_SCOPE = "out_of_scope"
    BOOK_SUMMARY = "book_summary"
    CHAPTER_SUMMARY = "chapter_summary"
    RETRIEVAL_QA = "retrieval_qa"


BOOK_SUMMARY_KEYWORDS = (
    "isi keseluruhan buku",
    "isi buku",
    "keseluruhan buku",
    "ringkasan buku",
    "tentang apa buku",
    "buku ini tentang apa",
    "summary of the book",
    "summarize the book",
    "what is this book about",
    "what is the book about",
    "whole book",
    "overall book",
)
CHAPTER_PATTERN = re.compile(
    r"\b(?:bab|chapter)\s+([0-9]+|[ivxlcdm]+|[a-z]+)\b",
    re.IGNORECASE,
)
SUMMARY_REQUEST_KEYWORDS = (
    "apa isi",
    "isi",
    "ringkas",
    "ringkasan",
    "summary",
    "summarize",
    "ceritakan",
    "tentang apa",
    "what is",
    "what's",
    "about",
)
OUT_OF_SCOPE_PATTERNS = (
    re.compile(r"\bsiapa\s+presiden\b", re.IGNORECASE),
    re.compile(r"\bwho\s+is\s+(?:the\s+)?president\b", re.IGNORECASE),
    re.compile(r"\bpresiden\s+(?:amerika|indonesia|china|rusia)\b", re.IGNORECASE),
    re.compile(r"\b(?:united states|us|american)\s+president\b", re.IGNORECASE),
    re.compile(r"\b(?:cuaca|weather)\b", re.IGNORECASE),
    re.compile(r"\b(?:harga saham|stock price|exchange rate|kurs)\b", re.IGNORECASE),
    re.compile(r"\b(?:resep|recipe)\b", re.IGNORECASE),
    re.compile(r"\bcara membuat\s+(?:rendang|nasi goreng|kue)\b", re.IGNORECASE),
)
INDONESIAN_ORDINALS = {
    "pertama": 1,
    "kedua": 2,
    "ketiga": 3,
    "keempat": 4,
    "kelima": 5,
    "keenam": 6,
    "ketujuh": 7,
    "kedelapan": 8,
    "kesembilan": 9,
    "kesepuluh": 10,
}
ENGLISH_NUMBERS = {
    "one": 1,
    "first": 1,
    "two": 2,
    "second": 2,
    "three": 3,
    "third": 3,
    "four": 4,
    "fourth": 4,
    "five": 5,
    "fifth": 5,
    "six": 6,
    "sixth": 6,
    "seven": 7,
    "seventh": 7,
    "eight": 8,
    "eighth": 8,
    "nine": 9,
    "ninth": 9,
    "ten": 10,
    "tenth": 10,
}
ROMAN_VALUES = {
    "i": 1,
    "ii": 2,
    "iii": 3,
    "iv": 4,
    "v": 5,
    "vi": 6,
    "vii": 7,
    "viii": 8,
    "ix": 9,
    "x": 10,
    "xi": 11,
    "xii": 12,
}


@dataclass(frozen=True)
class QuestionRoute:
    mode: QuestionMode
    chapter_number: int | None = None


def route_question(question: str) -> QuestionRoute:
    normalized_question = " ".join(question.casefold().split())
    if not normalized_question:
        return QuestionRoute(mode=QuestionMode.RETRIEVAL_QA)

    if _is_obviously_out_of_scope(normalized_question):
        return QuestionRoute(mode=QuestionMode.OUT_OF_SCOPE)

    chapter_match = CHAPTER_PATTERN.search(normalized_question)
    if chapter_match is not None and _looks_like_summary_request(normalized_question):
        chapter_number = _parse_chapter_number(chapter_match.group(1))
        if chapter_number is not None:
            return QuestionRoute(
                mode=QuestionMode.CHAPTER_SUMMARY,
                chapter_number=chapter_number,
            )

    if any(keyword in normalized_question for keyword in BOOK_SUMMARY_KEYWORDS):
        return QuestionRoute(mode=QuestionMode.BOOK_SUMMARY)

    return QuestionRoute(mode=QuestionMode.RETRIEVAL_QA)


def _is_obviously_out_of_scope(question: str) -> bool:
    return any(pattern.search(question) for pattern in OUT_OF_SCOPE_PATTERNS)


def _looks_like_summary_request(question: str) -> bool:
    return any(keyword in question for keyword in SUMMARY_REQUEST_KEYWORDS)


def _parse_chapter_number(raw_value: str) -> int | None:
    value = raw_value.casefold().strip()
    if value.isdigit():
        return int(value)
    if value in ROMAN_VALUES:
        return ROMAN_VALUES[value]
    return INDONESIAN_ORDINALS.get(value) or ENGLISH_NUMBERS.get(value)
