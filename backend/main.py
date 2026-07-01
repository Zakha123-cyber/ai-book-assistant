from fastapi import FastAPI

from api.router import api_router
from core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(
        title="AI Book Assistant API",
        version="0.1.0",
    )
    app.include_router(api_router)
    return app


app = create_app()
