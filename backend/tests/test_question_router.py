import unittest

from services.qa.question_router import QuestionMode, route_question


class QuestionRouterTest(unittest.TestCase):
    def test_routes_book_summary_questions_in_indonesian(self) -> None:
        route = route_question("Apa isi keseluruhan buku ini?")

        self.assertEqual(route.mode, QuestionMode.BOOK_SUMMARY)
        self.assertIsNone(route.chapter_number)

    def test_routes_book_summary_questions_in_english(self) -> None:
        route = route_question("What is this book about?")

        self.assertEqual(route.mode, QuestionMode.BOOK_SUMMARY)

    def test_routes_chapter_summary_questions_in_indonesian(self) -> None:
        route = route_question("Ceritakan bab pertama")

        self.assertEqual(route.mode, QuestionMode.CHAPTER_SUMMARY)
        self.assertEqual(route.chapter_number, 1)

    def test_routes_chapter_summary_questions_in_english(self) -> None:
        route = route_question("What is chapter 1 about?")

        self.assertEqual(route.mode, QuestionMode.CHAPTER_SUMMARY)
        self.assertEqual(route.chapter_number, 1)

    def test_routes_english_word_chapter_numbers(self) -> None:
        route = route_question("Summarize chapter one")

        self.assertEqual(route.mode, QuestionMode.CHAPTER_SUMMARY)
        self.assertEqual(route.chapter_number, 1)

    def test_routes_obvious_out_of_scope_questions(self) -> None:
        route = route_question("Siapa presiden Amerika Serikat?")

        self.assertEqual(route.mode, QuestionMode.OUT_OF_SCOPE)

    def test_routes_obvious_english_out_of_scope_questions(self) -> None:
        route = route_question("Who is the president of the United States?")

        self.assertEqual(route.mode, QuestionMode.OUT_OF_SCOPE)

    def test_routes_regular_book_question_to_retrieval(self) -> None:
        route = route_question("Apa yang ditemukan Nara di loteng?")

        self.assertEqual(route.mode, QuestionMode.RETRIEVAL_QA)


if __name__ == "__main__":
    unittest.main()
