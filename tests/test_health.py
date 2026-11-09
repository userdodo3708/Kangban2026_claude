"""Acceptance tests for the health endpoint and trace_id plumbing."""

from __future__ import annotations

import json
import logging

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.logging import (
    JsonFormatter,
    TraceIdFilter,
    get_trace_id,
    reset_trace_id,
    set_trace_id,
)
from app.main import app


def test_health_returns_200_and_valid_body() -> None:
    settings = get_settings()
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }
    assert response.headers["X-Trace-ID"]


def test_health_preserves_incoming_trace_id() -> None:
    with TestClient(app) as client:
        response = client.get("/health", headers={"X-Trace-ID": "test-trace-123"})

    assert response.headers["X-Trace-ID"] == "test-trace-123"


def test_health_replaces_invalid_trace_id() -> None:
    with TestClient(app) as client:
        response = client.get("/health", headers={"X-Trace-ID": "bad trace id"})

    assert response.headers["X-Trace-ID"] != "bad trace id"
    assert 0 < len(response.headers["X-Trace-ID"]) <= 128


def test_trace_filter_uses_context() -> None:
    token = set_trace_id("trace-from-test")
    try:
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname=__file__, lineno=1,
            msg="hello", args=(), exc_info=None,
        )
        assert TraceIdFilter().filter(record) is True
        assert record.trace_id == "trace-from-test"
    finally:
        reset_trace_id(token)
    assert get_trace_id() == "-"


def test_json_formatter_always_emits_trace_id() -> None:
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname=__file__, lineno=1,
        msg="hello %s", args=("world",), exc_info=None,
    )
    payload = json.loads(JsonFormatter().format(record))
    assert payload["trace_id"] == "-"
    assert payload["message"] == "hello world"
    assert payload["level"] == "INFO"
