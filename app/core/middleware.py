"""ASGI middleware that establishes a trace_id for each HTTP request."""

from __future__ import annotations

import logging
import time
import uuid

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import reset_trace_id, set_trace_id

TRACE_ID_HEADER = "X-Trace-ID"
_ALLOWED_TRACE_ID_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._"
)
logger = logging.getLogger("app.http")


def _normalize_trace_id(value: str | None) -> str:
    if value:
        candidate = value.strip()
        if 0 < len(candidate) <= 128 and set(candidate) <= _ALLOWED_TRACE_ID_CHARS:
            return candidate
    return uuid.uuid4().hex


class TraceIdMiddleware:
    """Pure ASGI middleware so contextvars remain visible downstream."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        trace_id = _normalize_trace_id(Headers(scope=scope).get(TRACE_ID_HEADER))
        token = set_trace_id(trace_id)
        scope.setdefault("state", {})["trace_id"] = trace_id
        started = time.perf_counter()
        status_code = 500
        method = scope.get("method", "")
        path = scope.get("path", "")

        async def send_with_trace_id(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = MutableHeaders(scope=message)
                response_headers[TRACE_ID_HEADER] = trace_id
            await send(message)

        try:
            logger.info("request_started method=%s path=%s", method, path)
            await self.app(scope, receive, send_with_trace_id)
        except Exception:
            logger.exception("request_failed method=%s path=%s", method, path)
            raise
        finally:
            duration_ms = (time.perf_counter() - started) * 1000
            logger.info(
                "request_finished method=%s path=%s status=%s duration_ms=%.2f",
                method,
                path,
                status_code,
                duration_ms,
            )
            reset_trace_id(token)
