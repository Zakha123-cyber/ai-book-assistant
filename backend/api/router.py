from fastapi import APIRouter

from api.books import router as books_router
from api.health import router as health_router

api_router = APIRouter()
api_router.include_router(books_router)
api_router.include_router(health_router)
