from dataclasses import dataclass
from pathlib import Path

import fitz


class PDFParsingError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class ParsedPDF:
    page_count: int
    pages: list[ParsedPage]

    @property
    def text(self) -> str:
        return "\n\n".join(page.text for page in self.pages if page.text)


def extract_text_from_pdf(file_path: Path) -> ParsedPDF:
    try:
        with fitz.open(file_path) as document:
            pages = [
                ParsedPage(
                    page_number=page.number + 1,
                    text=page.get_text("text").strip(),
                )
                for page in document
            ]
            return ParsedPDF(page_count=document.page_count, pages=pages)
    except Exception as error:
        raise PDFParsingError("Failed to extract text from PDF.") from error

