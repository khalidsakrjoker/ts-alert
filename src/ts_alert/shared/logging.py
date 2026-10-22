"""Structured JSON logging with level configured from application settings."""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, TextIO

from ts_alert.config import get_settings

LEVEL_MAP: dict[str, int] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}

_STANDARD_RECORD_ATTRS: frozenset[str] = frozenset(
    {
        "args",
        "context",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "message",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "taskName",
        "thread",
        "threadName",
    }
)


class JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON with standard fields."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=UTC).isoformat()
        context: dict[str, Any] = {}

        record_context = getattr(record, "context", None)
        if isinstance(record_context, Mapping):
            context.update(record_context)

        for key, val in record.__dict__.items():
            if key not in _STANDARD_RECORD_ATTRS and not key.startswith("_"):
                context[key] = val

        payload: dict[str, Any] = {
            "level": record.levelname,
            "timestamp": timestamp,
            "message": record.getMessage(),
            "context": context,
            "logger": record.name,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


class StructuredLogger:
    """Wrapper around standard logging.Logger providing structured logging."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self.name = logger.name

    def _log(
        self,
        level: int,
        message: str,
        context: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        ctx: dict[str, Any] = {}
        if context:
            ctx.update(context)
        if kwargs:
            ctx.update(kwargs)
        self._logger.log(level, message, extra={"context": ctx})

    def debug(
        self,
        message: str,
        context: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._log(logging.DEBUG, message, context, **kwargs)

    def info(
        self,
        message: str,
        context: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._log(logging.INFO, message, context, **kwargs)

    def warning(
        self,
        message: str,
        context: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._log(logging.WARNING, message, context, **kwargs)

    def warn(
        self,
        message: str,
        context: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._log(logging.WARNING, message, context, **kwargs)

    def error(
        self,
        message: str,
        context: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._log(logging.ERROR, message, context, **kwargs)

    def is_enabled_for(self, level: int) -> bool:
        return self._logger.isEnabledFor(level)


def configure_logging(
    level: str | None = None,
    stream: TextIO | None = None,
) -> None:
    """Configure the root logger with a JSON formatter and log level from config."""
    if level is None:
        level = get_settings().log_level

    log_level = LEVEL_MAP.get(level.lower(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(log_level)

    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(JsonFormatter())

    root.handlers.clear()
    root.addHandler(handler)


def get_logger(name: str = "ts_alert") -> StructuredLogger:
    """Get a structured logger configured with the application log level."""
    settings = get_settings()
    log_level = LEVEL_MAP.get(settings.log_level.lower(), logging.INFO)
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    return StructuredLogger(logger)
