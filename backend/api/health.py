from fastapi import APIRouter

from schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        success=True,
        status="ok",
        service="ai-book-assistant-api",
    )

