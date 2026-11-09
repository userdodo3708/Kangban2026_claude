"""FastAPI entrypoint for the Konban backend."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.middleware import TraceIdMiddleware

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info(
        "app_startup name=%s version=%s env=%s",
        settings.app_name,
        settings.app_version,
        settings.app_env,
    )
    yield
    logger.info("app_shutdown name=%s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)
app.add_middleware(TraceIdMiddleware)
app.include_router(health_router)
