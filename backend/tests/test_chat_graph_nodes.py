import uuid
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from models import SystemProfile
from services.qa.chat_graph_nodes import (
    ChatGraphBookNotFoundError,
    ChatGraphSummaryNotFoundError,
    ChatGraphSystemProfileNotFoundError,
    detect_identity_node,
    generate_identity_or_summary_answer_node,
    persist_chat_history_node,
    resolve_summary_context_node,
    route_question_node,
    run_retrieval_qa_node,
    validate_book_node,
)
from services.qa.chat_pipeline import ChatAnswer
from services.qa.chat_pipeline import ANSWER_NOT_FOUND
from services.qa.context_builder import SourceReference
from services.qa.question_router import QuestionMode, QuestionRoute


class FakeBookRepository:
    def __init__(self, session, book=None) -> None:
        self.book = book

    async def get_by_id(self, book_id):
        return self.book


class FakeSystemProfileRepository:
    def __init__(self, session, profile=None) -> None:
        self.profile = profile

    async def get_default(self):
        return self.profile


class FakeSummaryRepository:
    def __init__(self, session, summaries=None) -> None:
        self.summaries = summaries or []

    async def list_by_reference(self, reference_id, level=None):
        return self.summaries


class FakeChapterRepository:
    def __init__(self, session, chapters=None) -> None:
        self.chapters = chapters or []

    async def list_by_book_id(self, book_id):
        return self.chapters


class FakeChatHistoryRepository:
    added_items = []

    def __init__(self, session) -> None:
        pass

    async def add(self, item):
        self.added_items.append(item)
        return item


class FakeQwenQAService:
    def __init__(self) -> None:
        pass

    async def answer_question(self, question: str, retrieved_context: str) -> str:
        return f"Generated answer for: {question}"


def fake_profile() -> SystemProfile:
    return SystemProfile(
        profile_key="default",
        assistant_name="AI Book Assistant",
        assistant_description="Assistant description.",
        creator_name="Zakha Aditya Hadiansyah",
        creator_description="Creator description.",
    )


class ChatGraphNodesTest(unittest.IsolatedAsyncioTestCase):
    async def test_validate_book_node_adds_book_to_state(self) -> None:
        book_id = uuid.uuid4()
        book = SimpleNamespace(id=book_id, title="Test Book")

        with patch(
            "services.qa.chat_graph_nodes.BookRepository",
            lambda session: FakeBookRepository(session, book=book),
        ):
            state = await validate_book_node(
                {
                    "book_id": book_id,
                    "question": "Apa isi buku ini?",
                    "normalized_question": "Apa isi buku ini?",
                    "top_k": 5,
                },
                session=object(),
            )

        self.assertEqual(state["book"], book)
        self.assertEqual(state["book_id"], book_id)

    async def test_validate_book_node_raises_when_book_missing(self) -> None:
        with patch(
            "services.qa.chat_graph_nodes.BookRepository",
            lambda session: FakeBookRepository(session, book=None),
        ):
            with self.assertRaises(ChatGraphBookNotFoundError):
                await validate_book_node(
                    {
                        "book_id": uuid.uuid4(),
                        "question": "Apa isi buku ini?",
                        "top_k": 5,
                    },
                    session=object(),
                )

    async def test_detect_identity_node_adds_creator_context(self) -> None:
        with patch(
            "services.qa.chat_graph_nodes.SystemProfileRepository",
            lambda session: FakeSystemProfileRepository(
                session,
                profile=fake_profile(),
            ),
        ):
            state = await detect_identity_node(
                {
                    "book_id": uuid.uuid4(),
                    "question": "siapakah yang menciptakan anda?",
                    "normalized_question": "siapakah yang menciptakan anda?",
                    "top_k": 5,
                },
                session=object(),
            )

        self.assertIn("identity_route", state)
        self.assertIn("Creator description.", state["identity_context"])
        self.assertEqual(state["response_mode"], "app_identity")

    async def test_detect_identity_node_matches_creator_name_from_profile(self) -> None:
        with patch(
            "services.qa.chat_graph_nodes.SystemProfileRepository",
            lambda session: FakeSystemProfileRepository(
                session,
                profile=fake_profile(),
            ),
        ):
            state = await detect_identity_node(
                {
                    "book_id": uuid.uuid4(),
                    "question": "siapakah zakha?",
                    "normalized_question": "siapakah zakha?",
                    "top_k": 5,
                },
                session=object(),
            )

        self.assertIn("identity_route", state)
        self.assertIn("Zakha Aditya Hadiansyah", state["identity_context"])

    async def test_detect_identity_node_leaves_book_question_unchanged(self) -> None:
        initial_state = {
            "book_id": uuid.uuid4(),
            "question": "siapa pak wira?",
            "normalized_question": "siapa pak wira?",
            "top_k": 5,
        }
        with patch(
            "services.qa.chat_graph_nodes.SystemProfileRepository",
            lambda session: FakeSystemProfileRepository(
                session,
                profile=fake_profile(),
            ),
        ):
            state = await detect_identity_node(initial_state, session=object())

        self.assertEqual(state, initial_state)

    async def test_detect_identity_node_raises_when_profile_missing(self) -> None:
        with patch(
            "services.qa.chat_graph_nodes.SystemProfileRepository",
            lambda session: FakeSystemProfileRepository(session, profile=None),
        ):
            with self.assertRaises(ChatGraphSystemProfileNotFoundError):
                await detect_identity_node(
                    {
                        "book_id": uuid.uuid4(),
                        "question": "siapakah yang menciptakan anda?",
                        "normalized_question": "siapakah yang menciptakan anda?",
                        "top_k": 5,
                    },
                    session=object(),
                )

    async def test_resolve_summary_context_node_adds_book_summary_context(self) -> None:
        book_id = uuid.uuid4()
        summary = SimpleNamespace(summary="Book summary text.")

        with patch(
            "services.qa.chat_graph_nodes.SummaryRepository",
            lambda session: FakeSummaryRepository(session, summaries=[summary]),
        ):
            state = await resolve_summary_context_node(
                {
                    "book_id": book_id,
                    "question": "ringkas buku ini",
                    "top_k": 5,
                    "question_route": QuestionRoute(mode=QuestionMode.BOOK_SUMMARY),
                },
                session=object(),
            )

        self.assertIn("[Book Summary]", state["summary_context"])
        self.assertEqual(state["sources"][0].chunk_id, "book-summary")

    async def test_resolve_summary_context_node_adds_chapter_summary_context(self) -> None:
        book_id = uuid.uuid4()
        chapter_id = uuid.uuid4()
        chapter = SimpleNamespace(id=chapter_id, number=1, title="Bab Satu")
        summary = SimpleNamespace(summary="Chapter summary text.")

        with (
            patch(
                "services.qa.chat_graph_nodes.ChapterRepository",
                lambda session: FakeChapterRepository(session, chapters=[chapter]),
            ),
            patch(
                "services.qa.chat_graph_nodes.SummaryRepository",
                lambda session: FakeSummaryRepository(session, summaries=[summary]),
            ),
        ):
            state = await resolve_summary_context_node(
                {
                    "book_id": book_id,
                    "question": "ringkas bab 1",
                    "top_k": 5,
                    "question_route": QuestionRoute(
                        mode=QuestionMode.CHAPTER_SUMMARY,
                        chapter_number=1,
                    ),
                },
                session=object(),
            )

        self.assertIn("Chapter 1: Bab Satu", state["summary_context"])
        self.assertEqual(state["sources"][0].chapter, 1)

    async def test_resolve_summary_context_node_skips_retrieval_route(self) -> None:
        initial_state = {
            "book_id": uuid.uuid4(),
            "question": "siapa pak wira?",
            "top_k": 5,
            "question_route": QuestionRoute(mode=QuestionMode.RETRIEVAL_QA),
        }

        state = await resolve_summary_context_node(initial_state, session=object())

        self.assertEqual(state, initial_state)

    async def test_resolve_summary_context_node_raises_when_summary_missing(self) -> None:
        with patch(
            "services.qa.chat_graph_nodes.SummaryRepository",
            lambda session: FakeSummaryRepository(session, summaries=[]),
        ):
            with self.assertRaises(ChatGraphSummaryNotFoundError):
                await resolve_summary_context_node(
                    {
                        "book_id": uuid.uuid4(),
                        "question": "ringkas buku ini",
                        "top_k": 5,
                        "question_route": QuestionRoute(
                            mode=QuestionMode.BOOK_SUMMARY,
                        ),
                    },
                    session=object(),
                )

    async def test_run_retrieval_qa_node_adds_answer_and_sources(self) -> None:
        source = SourceReference(
            chunk_id="chunk-1",
            chapter=1,
            chapter_title="Bab Satu",
            page_start=1,
            page_end=1,
            distance=0.2,
        )

        async def fake_answer_book_question(book_id, question, top_k):
            return ChatAnswer(
                answer="Jawaban dari retrieval.",
                sources=[source],
            )

        with patch(
            "services.qa.chat_graph_nodes.answer_book_question",
            fake_answer_book_question,
        ):
            state = await run_retrieval_qa_node(
                {
                    "book_id": uuid.uuid4(),
                    "question": "siapa pak wira?",
                    "normalized_question": "siapa pak wira?",
                    "top_k": 5,
                    "question_route": QuestionRoute(mode=QuestionMode.RETRIEVAL_QA),
                }
            )

        self.assertEqual(state["answer"], "Jawaban dari retrieval.")
        self.assertEqual(state["sources"], [source])
        self.assertEqual(state["message"], "Chat answer generated successfully.")
        self.assertEqual(state["response_mode"], QuestionMode.RETRIEVAL_QA.value)

    async def test_run_retrieval_qa_node_skips_summary_context(self) -> None:
        initial_state = {
            "book_id": uuid.uuid4(),
            "question": "ringkas buku ini",
            "top_k": 5,
            "summary_context": "Summary context.",
            "question_route": QuestionRoute(mode=QuestionMode.BOOK_SUMMARY),
        }

        state = await run_retrieval_qa_node(initial_state)

        self.assertEqual(state, initial_state)

    async def test_generate_identity_or_summary_answer_node_handles_identity(self) -> None:
        with patch(
            "services.qa.chat_graph_nodes.QwenQAService",
            FakeQwenQAService,
        ):
            state = await generate_identity_or_summary_answer_node(
                {
                    "book_id": uuid.uuid4(),
                    "question": "siapakah pencipta anda?",
                    "normalized_question": "siapakah pencipta anda?",
                    "top_k": 5,
                    "identity_context": "Creator context.",
                }
            )

        self.assertEqual(
            state["message"],
            "Application identity answer generated successfully.",
        )
        self.assertEqual(state["response_mode"], "app_identity")
        self.assertEqual(state["sources"], [])
        self.assertIn("Generated answer", state["answer"])

    async def test_generate_identity_or_summary_answer_node_handles_summary(self) -> None:
        source = SourceReference(
            chunk_id="book-summary",
            chapter=None,
            chapter_title=None,
            page_start=None,
            page_end=None,
            distance=None,
        )
        with patch(
            "services.qa.chat_graph_nodes.QwenQAService",
            FakeQwenQAService,
        ):
            state = await generate_identity_or_summary_answer_node(
                {
                    "book_id": uuid.uuid4(),
                    "question": "ringkas buku ini",
                    "normalized_question": "ringkas buku ini",
                    "top_k": 5,
                    "summary_context": "Book summary context.",
                    "sources": [source],
                    "response_mode": QuestionMode.BOOK_SUMMARY.value,
                }
            )

        self.assertEqual(state["message"], "Summary answer generated successfully.")
        self.assertEqual(state["response_mode"], QuestionMode.BOOK_SUMMARY.value)
        self.assertEqual(state["sources"], [source])

    async def test_generate_identity_or_summary_answer_node_skips_existing_answer(self) -> None:
        initial_state = {
            "book_id": uuid.uuid4(),
            "question": "siapa pak wira?",
            "top_k": 5,
            "answer": "Existing answer.",
        }

        state = await generate_identity_or_summary_answer_node(initial_state)

        self.assertEqual(state, initial_state)

    async def test_persist_chat_history_node_adds_history_when_answer_exists(self) -> None:
        FakeChatHistoryRepository.added_items = []
        book_id = uuid.uuid4()

        with patch(
            "services.qa.chat_graph_nodes.ChatHistoryRepository",
            FakeChatHistoryRepository,
        ):
            state = await persist_chat_history_node(
                {
                    "book_id": book_id,
                    "question": "Original question?",
                    "normalized_question": "Normalized question?",
                    "top_k": 5,
                    "answer": "Answer text.",
                },
                session=object(),
            )

        self.assertEqual(state["answer"], "Answer text.")
        self.assertEqual(len(FakeChatHistoryRepository.added_items), 1)
        self.assertEqual(FakeChatHistoryRepository.added_items[0].book_id, book_id)
        self.assertEqual(
            FakeChatHistoryRepository.added_items[0].question,
            "Normalized question?",
        )

    async def test_persist_chat_history_node_skips_missing_answer(self) -> None:
        FakeChatHistoryRepository.added_items = []
        initial_state = {
            "book_id": uuid.uuid4(),
            "question": "Original question?",
            "top_k": 5,
        }

        with patch(
            "services.qa.chat_graph_nodes.ChatHistoryRepository",
            FakeChatHistoryRepository,
        ):
            state = await persist_chat_history_node(initial_state, session=object())

        self.assertEqual(state, initial_state)
        self.assertEqual(FakeChatHistoryRepository.added_items, [])

    async def test_route_question_node_adds_question_route(self) -> None:
        state = await route_question_node(
            {
                "book_id": uuid.uuid4(),
                "question": "apa isi keseluruhan buku ini?",
                "normalized_question": "apa isi keseluruhan buku ini?",
                "top_k": 5,
            }
        )

        self.assertEqual(state["question_route"].mode, QuestionMode.BOOK_SUMMARY)
        self.assertEqual(state["response_mode"], QuestionMode.BOOK_SUMMARY.value)

    async def test_route_question_node_skips_identity_context(self) -> None:
        initial_state = {
            "book_id": uuid.uuid4(),
            "question": "apa tugas anda?",
            "normalized_question": "apa tugas anda?",
            "top_k": 5,
            "identity_context": "Assistant context.",
            "response_mode": "app_identity",
        }

        state = await route_question_node(initial_state)

        self.assertEqual(state, initial_state)

    async def test_route_question_node_handles_out_of_scope(self) -> None:
        state = await route_question_node(
            {
                "book_id": uuid.uuid4(),
                "question": "Siapa presiden Amerika Serikat?",
                "normalized_question": "Siapa presiden Amerika Serikat?",
                "top_k": 5,
            }
        )

        self.assertEqual(state["question_route"].mode, QuestionMode.OUT_OF_SCOPE)
        self.assertEqual(state["answer"], ANSWER_NOT_FOUND)
        self.assertEqual(state["sources"], [])


if __name__ == "__main__":
    unittest.main()
