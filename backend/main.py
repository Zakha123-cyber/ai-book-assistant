from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.router import api_router
from core.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(
        title="AI Book Assistant API",
        version="0.1.0",
    )
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(
        RequestValidationError,
        request_validation_exception_handler,
    )
    app.include_router(api_router)
    return app


app = create_app()
