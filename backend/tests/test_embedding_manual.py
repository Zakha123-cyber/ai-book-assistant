import asyncio

from services.embedding import DashScopeEmbeddingService


async def main() -> None:
    service = DashScopeEmbeddingService()
    vectors = await service.embed_texts(["Alice follows the white rabbit."])

    print("Embedding request succeeded.")
    print(f"vector_count: {len(vectors)}")
    print(f"dimension: {len(vectors[0]) if vectors else 0}")
    print(f"sample: {vectors[0][:5] if vectors else []}")


if __name__ == "__main__":
    asyncio.run(main())

