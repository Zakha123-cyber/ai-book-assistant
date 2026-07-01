import json
from pathlib import Path

from services.parser.pdf_parser import ParsedPDF


def save_extracted_text(parsed_pdf: ParsedPDF, source_pdf_path: Path) -> Path:
    extracted_path = source_pdf_path.with_suffix(".extracted.json")
    payload = {
        "source_pdf": str(source_pdf_path),
        "page_count": parsed_pdf.page_count,
        "text": parsed_pdf.text,
        "pages": [
            {
                "page_number": page.page_number,
                "text": page.text,
            }
            for page in parsed_pdf.pages
        ],
    }

    extracted_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return extracted_path

