import unittest
from types import SimpleNamespace

from services.qa.qwen_qa import QAServiceError, QwenQAService


class FakeCompletions:
    def __init__(self) -> None:
        self.request: dict[str, object] | None = None

    async def create(self, **kwargs: object) -> object:
        self.request = kwargs
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="  Nara menemukan surat.  ")
                )
            ]
        )


class FakeChat:
    def __init__(self) -> None:
        self.completions = FakeCompletions()


class FakeClient:
    def __init__(self) -> None:
        self.chat = FakeChat()


class QwenQAServiceTest(unittest.IsolatedAsyncioTestCase):
    async def test_answers_question_with_qa_prompt(self) -> None:
        service = QwenQAService.__new__(QwenQAService)
        service.model = "qwen-test"
        service.client = FakeClient()

        answer = await service.answer_question(
            question="Apa yang ditemukan Nara?",
            retrieved_context="[Source 1] Nara menemukan surat.",
        )

        request = service.client.chat.completions.request
        self.assertEqual(answer, "Nara menemukan surat.")
        self.assertEqual(request["model"], "qwen-test")
        self.assertEqual(request["temperature"], 0.1)
        self.assertIn("Apa yang ditemukan Nara?", request["messages"][1]["content"])
        self.assertIn("[Source 1] Nara menemukan surat.", request["messages"][1]["content"])

    async def test_rejects_empty_answer(self) -> None:
        class EmptyCompletions:
            async def create(self, **kwargs: object) -> object:
                return SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content=""))]
                )

        service = QwenQAService.__new__(QwenQAService)
        service.model = "qwen-test"
        service.client = SimpleNamespace(
            chat=SimpleNamespace(completions=EmptyCompletions())
        )

        with self.assertRaises(QAServiceError):
            await service.answer_question("Question", "Context")


if __name__ == "__main__":
    unittest.main()
