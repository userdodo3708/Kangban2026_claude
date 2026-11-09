"""Structured JSON logging with a request-scoped trace_id."""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar, Token
from datetime import datetime, timezone
from typing import Any

_trace_id: ContextVar[str] = ContextVar("trace_id", default="-")


def get_trace_id() -> str:
    return _trace_id.get()


def set_trace_id(trace_id: str) -> Token[str]:
    return _trace_id.set(trace_id or "-")


def reset_trace_id(token: Token[str]) -> None:
    _trace_id.reset(token)


class TraceIdFilter(logging.Filter):
    """Attach the current context trace_id to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id()
        return True


class JsonFormatter(logging.Formatter):
    """One JSON object per line, always including trace_id."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "trace_id": getattr(record, "trace_id", "-"),
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def configure_logging(level: str = "INFO") -> None:
    """Route application and uvicorn logs through the same JSON handler."""

    log_level = getattr(logging, level.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.set_name("konban-json")
    handler.setFormatter(JsonFormatter())
    handler.addFilter(TraceIdFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(log_level)
    root.addHandler(handler)

    # Uvicorn installs its own handlers before importing the app; replace them
    # so startup, error, and access lines also carry trace_id.
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(log_level)
        logger.propagate = False

    logging.captureWarnings(True)
