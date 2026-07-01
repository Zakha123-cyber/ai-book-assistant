import unittest

from services.prompt.qa_prompts import build_qa_prompt


class QAPromptTest(unittest.TestCase):
    def test_builds_qa_prompt_from_library_template(self) -> None:
        prompt = build_qa_prompt(
            question="Apa yang ditemukan Nara di loteng?",
            retrieved_context=(
                "[Source 1] Chapter 1: Surat dari Loteng; page 1\n"
                "Nara menemukan kotak kayu berisi surat."
            ),
        )

        self.assertIn("Answer the user's question ONLY using the supplied context.", prompt)
        self.assertIn("I could not find that information inside this book.", prompt)
        self.assertIn("Do not use external knowledge.", prompt)
        self.assertIn("Mention chapter and page if available.", prompt)
        self.assertIn("Answer in the same language as the user's question.", prompt)
        self.assertIn("Apa yang ditemukan Nara di loteng?", prompt)
        self.assertIn("Nara menemukan kotak kayu berisi surat.", prompt)

    def test_rejects_empty_question(self) -> None:
        with self.assertRaises(ValueError):
            build_qa_prompt("   ", "Context")

    def test_rejects_empty_context(self) -> None:
        with self.assertRaises(ValueError):
            build_qa_prompt("Question", "   ")


if __name__ == "__main__":
    unittest.main()
