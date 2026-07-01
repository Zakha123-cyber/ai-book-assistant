QA_PROMPT_TEMPLATE = """Answer the user's question ONLY using the supplied context.

If the answer cannot be found in the context, reply:

"I could not find that information inside this book."

Requirements:
- Do not use external knowledge.
- Quote relevant concepts when appropriate.
- Mention chapter and page if available.
- Answer in the same language as the user's question.

Question:
{question}

Context:
{retrieved_context}
"""


def build_qa_prompt(question: str, retrieved_context: str) -> str:
    normalized_question = question.strip()
    normalized_context = retrieved_context.strip()
    if not normalized_question:
        raise ValueError("question cannot be empty.")
    if not normalized_context:
        raise ValueError("retrieved_context cannot be empty.")

    return QA_PROMPT_TEMPLATE.format(
        question=normalized_question,
        retrieved_context=normalized_context,
    )
