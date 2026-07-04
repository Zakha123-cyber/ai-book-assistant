import asyncio
import sys

from httpx import ASGITransport, AsyncClient

from database.session import engine
from main import app


SCENARIOS = [
    ("identity", "apa tugas anda, dan siapakah yang menciptakan anda"),
    ("book_summary", "ringkas keseluruhan buku ini"),
    ("retrieval_qa", "siapa pak wira?"),
    ("out_of_scope", "siapa presiden Amerika Serikat?"),
]


async def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: uv run python -m tests.test_chat_graph_manual <book_id>"
        )

    book_id = sys.argv[1]
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
            timeout=120,
        ) as client:
            for name, question in SCENARIOS:
                response = await client.post(
                    "/chat",
                    json={
                        "book_id": book_id,
                        "question": question,
                        "top_k": 5,
                    },
                )
                print(f"\n[{name}]")
                print(f"status_code: {response.status_code}")
                payload = response.json()
                if response.status_code != 200:
                    print(f"error: {payload}")
                    continue

                answer = payload.get("answer") or ""
                print(f"message: {payload.get('message')}")
                print(f"source_count: {len(payload.get('sources') or [])}")
                print(f"answer_preview: {answer.replace(chr(10), ' ')[:500]}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
