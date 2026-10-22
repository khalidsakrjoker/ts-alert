import io
import json
import logging
import sys
from typing import Any

import pytest

from ts_alert.config import get_settings
from ts_alert.shared.logging import (
    JsonFormatter,
    configure_logging,
    get_logger,
)


def test_json_formatter_outputs_required_fields() -> None:
    formatter = JsonFormatter()
    logger = logging.getLogger("test.formatter")
    record = logger.makeRecord(
        name="test.formatter",
        level=logging.INFO,
        fn="test_logging.py",
        lno=20,
        msg="payment processed for %s",
        args=("user_42",),
        exc_info=None,
        extra={"context": {"amount": 100, "currency": "USD"}},
    )

    formatted = formatter.format(record)
    parsed: dict[str, Any] = json.loads(formatted)

    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "test.formatter"
    assert parsed["message"] == "payment processed for user_42"
    assert parsed["context"] == {"amount": 100, "currency": "USD"}
    assert "timestamp" in parsed


def test_json_formatter_includes_exception() -> None:
    formatter = JsonFormatter()
    logger = logging.getLogger("test.exception")
    try:
        raise ValueError("boom")
    except ValueError:
        record = logger.makeRecord(
            name="test.exception",
            level=logging.ERROR,
            fn="test_logging.py",
            lno=45,
            msg="operation failed",
            args=(),
            exc_info=sys.exc_info(),
        )

    formatted = formatter.format(record)
    parsed: dict[str, Any] = json.loads(formatted)

    assert parsed["level"] == "ERROR"
    assert parsed["message"] == "operation failed"
    assert "ValueError: boom" in parsed["exception"]


def test_structured_logger_emits_json_lines() -> None:
    buffer = io.StringIO()
    configure_logging(level="info", stream=buffer)

    logger = get_logger("test.structured")
    logger.info("service started", context={"port": 8080})
    logger.debug("this should be filtered at info level")
    logger.warning("disk usage high", path="/var/log")
    logger.error("upstream timeout", service="billing")

    lines = [line.strip() for line in buffer.getvalue().splitlines() if line.strip()]
    assert len(lines) == 3

    info_log = json.loads(lines[0])
    assert info_log["level"] == "INFO"
    assert info_log["message"] == "service started"
    assert info_log["context"] == {"port": 8080}

    warn_log = json.loads(lines[1])
    assert warn_log["level"] == "WARNING"
    assert warn_log["message"] == "disk usage high"
    assert warn_log["context"] == {"path": "/var/log"}

    error_log = json.loads(lines[2])
    assert error_log["level"] == "ERROR"
    assert error_log["message"] == "upstream timeout"
    assert error_log["context"] == {"service": "billing"}


def test_log_level_comes_from_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "debug")
    get_settings.cache_clear()

    buffer = io.StringIO()
    configure_logging(stream=buffer)

    logger = get_logger("test.config_level")
    assert logger.is_enabled_for(logging.DEBUG)

    logger.debug("debug event visible", step="init")
    lines = [line.strip() for line in buffer.getvalue().splitlines() if line.strip()]
    assert len(lines) == 1

    entry = json.loads(lines[0])
    assert entry["level"] == "DEBUG"
    assert entry["message"] == "debug event visible"
    assert entry["context"] == {"step": "init"}

    get_settings.cache_clear()


def test_structured_logger_warn_alias() -> None:
    buffer = io.StringIO()
    configure_logging(level="warn", stream=buffer)

    logger = get_logger("test.alias")
    logger.warn("legacy warn call")

    lines = [line.strip() for line in buffer.getvalue().splitlines() if line.strip()]
    assert len(lines) == 1
    assert json.loads(lines[0])["level"] == "WARNING"
