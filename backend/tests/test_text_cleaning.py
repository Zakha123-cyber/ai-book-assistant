import unittest

from services.parser.pdf_parser import ParsedPage, ParsedPDF
from services.parser.text_cleaner import remove_boilerplate_lines


class TextCleanerTest(unittest.TestCase):
    def test_removes_book_viewer_boilerplate_lines(self) -> None:
        parsed_pdf = ParsedPDF(
            page_count=1,
            pages=[
                ParsedPage(
                    page_number=1,
                    text=(
                        "Fit Page\n"
                        "Full Screen On/Off\n"
                        "Close Book\n"
                        "Navigate\n"
                        "Control\n"
                        "Internet\n"
                        "Digital Interface by BookVirtual Corp.\n"
                        "U.S. Patent Pending.\n"
                        "Copyright 2000 All Rights Reserved.\n"
                        "Alice was beginning to get very tired."
                    ),
                )
            ],
        )

        cleaned_pdf = remove_boilerplate_lines(parsed_pdf)

        self.assertEqual(
            cleaned_pdf.pages[0].text,
            "Alice was beginning to get very tired.",
        )

    def test_preserves_content_after_inline_boilerplate(self) -> None:
        parsed_pdf = ParsedPDF(
            page_count=1,
            pages=[
                ParsedPage(
                    page_number=1,
                    text=(
                        "Fit Page Full Screen On/Off Close Book Navigate Control "
                        "Internet Digital Interface by BookVirtual Corp. "
                        "U.S. Patent Pending. Copyright 2000 All Rights Reserved. "
                        "CHAPTER IV.\n"
                        "THE RABBIT SENDS IN A LITTLE BILL."
                    ),
                )
            ],
        )

        cleaned_pdf = remove_boilerplate_lines(parsed_pdf)

        self.assertEqual(
            cleaned_pdf.pages[0].text,
            "CHAPTER IV.\nTHE RABBIT SENDS IN A LITTLE BILL.",
        )

    def test_removes_extraction_artifact_before_copyright_notice(self) -> None:
        parsed_pdf = ParsedPDF(
            page_count=1,
            pages=[
                ParsedPage(
                    page_number=1,
                    text="' 2000 All Rights Reserved. CHAPTER I.\nDOWN THE RABBIT-HOLE.",
                )
            ],
        )

        cleaned_pdf = remove_boilerplate_lines(parsed_pdf)

        self.assertEqual(
            cleaned_pdf.pages[0].text,
            "CHAPTER I.\nDOWN THE RABBIT-HOLE.",
        )

    def test_preserves_normal_content_with_similar_words(self) -> None:
        parsed_pdf = ParsedPDF(
            page_count=1,
            pages=[
                ParsedPage(
                    page_number=1,
                    text=(
                        "Alice tried to control her temper.\n"
                        "The internet was not part of this story."
                    ),
                )
            ],
        )

        cleaned_pdf = remove_boilerplate_lines(parsed_pdf)

        self.assertEqual(
            cleaned_pdf.pages[0].text,
            "Alice tried to control her temper.\n"
            "The internet was not part of this story.",
        )


if __name__ == "__main__":
    unittest.main()
