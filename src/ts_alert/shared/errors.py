"""Typed application error hierarchy carrying codes and safe messages."""

from __future__ import annotations

from typing import Any


class AppError(Exception):
    """Base application exception carrying error code, message, and safe message."""

    default_code: str = "INTERNAL_ERROR"
    default_safe_message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        safe_message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code or self.default_code
        self.safe_message = safe_message or self.default_safe_message
        self.message = message or self.safe_message
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to a safe dictionary suitable for structured logging or responses."""
        payload: dict[str, Any] = {
            "code": self.code,
            "message": self.safe_message,
        }
        if self.details:
            payload["details"] = self.details
        return payload

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"code={self.code!r}, message={self.message!r}, safe_message={self.safe_message!r})"
        )


class ValidationError(AppError):
    """Raised when user or client input fails validation rules."""

    default_code: str = "VALIDATION_ERROR"
    default_safe_message: str = "Invalid request parameters or payload."


class NotFoundError(AppError):
    """Raised when an entity or resource could not be found."""

    default_code: str = "NOT_FOUND"
    default_safe_message: str = "The requested resource was not found."


class ConflictError(AppError):
    """Raised when an operation conflicts with current state or duplicates a resource."""

    default_code: str = "CONFLICT"
    default_safe_message: str = "The resource already exists or is in a conflicting state."


class UnauthorizedError(AppError):
    """Raised when authentication credentials are required, invalid, or expired."""

    default_code: str = "UNAUTHORIZED"
    default_safe_message: str = "Authentication credentials are required or invalid."


class ForbiddenError(AppError):
    """Raised when authenticated subject lacks sufficient permissions."""

    default_code: str = "FORBIDDEN"
    default_safe_message: str = "You do not have permission to perform this action."


class ConfigurationError(AppError):
    """Raised when application configuration or environment is invalid."""

    default_code: str = "CONFIGURATION_ERROR"
    default_safe_message: str = "A server configuration error occurred."


class ExternalServiceError(AppError):
    """Raised when an upstream dependency or external API call fails."""

    default_code: str = "EXTERNAL_SERVICE_ERROR"
    default_safe_message: str = "An upstream service encountered an error."
