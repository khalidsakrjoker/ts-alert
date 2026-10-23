"""Shared cross-cutting utilities and infrastructure."""

from ts_alert.shared.errors import (
    AppError,
    ConfigurationError,
    ConflictError,
    ExternalServiceError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from ts_alert.shared.logging import (
    JsonFormatter,
    StructuredLogger,
    configure_logging,
    get_logger,
)

__all__ = [
    "AppError",
    "ConfigurationError",
    "ConflictError",
    "ExternalServiceError",
    "ForbiddenError",
    "JsonFormatter",
    "NotFoundError",
    "StructuredLogger",
    "UnauthorizedError",
    "ValidationError",
    "configure_logging",
    "get_logger",
]
