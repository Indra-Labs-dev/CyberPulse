from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppError, app_error_handler, unhandled_error_handler, validation_error_handler
from app.core.logging import configure_logging, get_logger
from app.tasks.scheduler import shutdown_scheduler, start_scheduler
from app.websocket.server import create_socket_app

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s (%s)", settings.app_name, settings.environment)
    start_scheduler()
    yield
    shutdown_scheduler()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)

    app.include_router(api_router)

    return app


app = create_app()
socket_app = create_socket_app(app)
