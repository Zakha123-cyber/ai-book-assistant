import uuid
import unittest
from unittest.mock import patch

import services.qa.chat_graph as chat_graph
from services.qa import ANSWER_NOT_FOUND
from services.qa.chat_graph import run_chat_graph
from services.qa.question_router import QuestionMode, QuestionRoute


def make_node(name, calls, updates=None):
    async def node(state):
        calls.append(name)
        return {
            **state,
            **(updates or {}),
        }

    return node


class ChatGraphWorkflowTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        chat_graph._build_chat_graph.cache_clear()

    def tearDown(self) -> None:
        chat_graph._build_chat_graph.cache_clear()

    async def test_chat_graph_runs_retrieval_workflow_in_order(self) -> None:
        calls = []
        book_id = uuid.uuid4()

        with (
            patch(
                "services.qa.chat_graph._validate_book",
                make_node("validate_book", calls, {"book": object()}),
            ),
            patch(
                "services.qa.chat_graph._detect_identity",
                make_node("detect_identity", calls),
            ),
            patch(
                "services.qa.chat_graph._route_question",
                make_node(
                    "route_question",
                    calls,
                    {
                        "question_route": QuestionRoute(
                            mode=QuestionMode.RETRIEVAL_QA,
                        ),
                        "response_mode": "retrieval_qa",
                    },
                ),
            ),
            patch(
                "services.qa.chat_graph._resolve_summary_context",
                make_node("resolve_summary_context", calls),
            ),
            patch(
                "services.qa.chat_graph._run_retrieval_qa",
                make_node(
                    "run_retrieval_qa",
                    calls,
                    {
                        "answer": "Retrieval answer.",
                        "sources": [],
                        "message": "Chat answer generated successfully.",
                    },
                ),
            ),
            patch(
                "services.qa.chat_graph._generate_identity_or_summary_answer",
                make_node("generate_identity_or_summary_answer", calls),
            ),
            patch(
                "services.qa.chat_graph._persist_chat_history",
                make_node("persist_chat_history", calls),
            ),
        ):
            state = await run_chat_graph(
                book_id=book_id,
                question="  siapa pak wira?  ",
                top_k=5,
            )

        self.assertEqual(
            calls,
            [
                "validate_book",
                "detect_identity",
                "route_question",
                "run_retrieval_qa",
                "persist_chat_history",
            ],
        )
        self.assertEqual(state["book_id"], book_id)
        self.assertEqual(state["question"], "  siapa pak wira?  ")
        self.assertEqual(state["normalized_question"], "siapa pak wira?")
        self.assertEqual(state["answer"], "Retrieval answer.")
        self.assertIn("persist_chat_history", calls)

    async def test_chat_graph_preserves_identity_answer_state(self) -> None:
        calls = []
        book_id = uuid.uuid4()

        with (
            patch(
                "services.qa.chat_graph._validate_book",
                make_node("validate_book", calls, {"book": object()}),
            ),
            patch(
                "services.qa.chat_graph._detect_identity",
                make_node(
                    "detect_identity",
                    calls,
                    {
                        "identity_context": "Creator context.",
                        "response_mode": "app_identity",
                    },
                ),
            ),
            patch(
                "services.qa.chat_graph._route_question",
                make_node("route_question", calls),
            ),
            patch(
                "services.qa.chat_graph._resolve_summary_context",
                make_node("resolve_summary_context", calls),
            ),
            patch(
                "services.qa.chat_graph._run_retrieval_qa",
                make_node("run_retrieval_qa", calls),
            ),
            patch(
                "services.qa.chat_graph._generate_identity_or_summary_answer",
                make_node(
                    "generate_identity_or_summary_answer",
                    calls,
                    {
                        "answer": "Identity answer.",
                        "sources": [],
                        "message": "Application identity answer generated successfully.",
                    },
                ),
            ),
            patch(
                "services.qa.chat_graph._persist_chat_history",
                make_node("persist_chat_history", calls),
            ),
        ):
            state = await run_chat_graph(
                book_id=book_id,
                question="siapakah pencipta anda?",
                top_k=5,
            )

        self.assertEqual(state["response_mode"], "app_identity")
        self.assertEqual(state["answer"], "Identity answer.")
        self.assertEqual(state["sources"], [])
        self.assertEqual(
            calls,
            [
                "validate_book",
                "detect_identity",
                "generate_identity_or_summary_answer",
                "persist_chat_history",
            ],
        )

    async def test_chat_graph_preserves_out_of_scope_answer_state(self) -> None:
        calls = []

        with (
            patch(
                "services.qa.chat_graph._validate_book",
                make_node("validate_book", calls, {"book": object()}),
            ),
            patch(
                "services.qa.chat_graph._detect_identity",
                make_node("detect_identity", calls),
            ),
            patch(
                "services.qa.chat_graph._route_question",
                make_node(
                    "route_question",
                    calls,
                    {
                        "answer": ANSWER_NOT_FOUND,
                        "sources": [],
                        "message": "Question is outside the scope of this book.",
                        "response_mode": "out_of_scope",
                    },
                ),
            ),
            patch(
                "services.qa.chat_graph._resolve_summary_context",
                make_node("resolve_summary_context", calls),
            ),
            patch(
                "services.qa.chat_graph._run_retrieval_qa",
                make_node("run_retrieval_qa", calls),
            ),
            patch(
                "services.qa.chat_graph._generate_identity_or_summary_answer",
                make_node("generate_identity_or_summary_answer", calls),
            ),
            patch(
                "services.qa.chat_graph._persist_chat_history",
                make_node("persist_chat_history", calls),
            ),
        ):
            state = await run_chat_graph(
                book_id=uuid.uuid4(),
                question="Siapa presiden Amerika Serikat?",
                top_k=5,
            )

        self.assertEqual(state["answer"], ANSWER_NOT_FOUND)
        self.assertEqual(state["response_mode"], "out_of_scope")
        self.assertEqual(state["sources"], [])
        self.assertEqual(
            calls,
            [
                "validate_book",
                "detect_identity",
                "route_question",
                "persist_chat_history",
            ],
        )


if __name__ == "__main__":
    unittest.main()
