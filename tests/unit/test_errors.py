import pytest

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


def test_base_app_error_defaults() -> None:
    err = AppError()
    assert err.code == "INTERNAL_ERROR"
    assert err.safe_message == "An unexpected error occurred."
    assert err.message == "An unexpected error occurred."
    assert err.details == {}
    assert str(err) == "[INTERNAL_ERROR] An unexpected error occurred."
    assert err.to_dict() == {
        "code": "INTERNAL_ERROR",
        "message": "An unexpected error occurred.",
    }


def test_base_app_error_custom_values() -> None:
    err = AppError(
        "Database pool exhausted",
        code="DB_POOL_EXHAUSTED",
        safe_message="Temporary service degradation.",
        details={"pool_size": 20, "active": 20},
    )
    assert err.code == "DB_POOL_EXHAUSTED"
    assert err.message == "Database pool exhausted"
    assert err.safe_message == "Temporary service degradation."
    assert err.details == {"pool_size": 20, "active": 20}
    assert str(err) == "[DB_POOL_EXHAUSTED] Database pool exhausted"
    assert err.to_dict() == {
        "code": "DB_POOL_EXHAUSTED",
        "message": "Temporary service degradation.",
        "details": {"pool_size": 20, "active": 20},
    }
    assert "AppError" in repr(err)


def test_typed_error_subclasses() -> None:
    cases = [
        (ValidationError, "VALIDATION_ERROR", "Invalid request parameters or payload."),
        (NotFoundError, "NOT_FOUND", "The requested resource was not found."),
        (ConflictError, "CONFLICT", "The resource already exists or is in a conflicting state."),
        (UnauthorizedError, "UNAUTHORIZED", "Authentication credentials are required or invalid."),
        (ForbiddenError, "FORBIDDEN", "You do not have permission to perform this action."),
        (ConfigurationError, "CONFIGURATION_ERROR", "A server configuration error occurred."),
        (
            ExternalServiceError,
            "EXTERNAL_SERVICE_ERROR",
            "An upstream service encountered an error.",
        ),
    ]
    for cls, expected_code, expected_safe_msg in cases:
        err = cls()
        assert isinstance(err, AppError)
        assert isinstance(err, Exception)
        assert err.code == expected_code
        assert err.safe_message == expected_safe_msg
        assert str(err) == f"[{expected_code}] {expected_safe_msg}"


def test_custom_message_preserves_safe_message() -> None:
    err = ValidationError("Email field is missing @ character", details={"field": "email"})
    assert err.code == "VALIDATION_ERROR"
    assert err.message == "Email field is missing @ character"
    assert err.safe_message == "Invalid request parameters or payload."
    assert err.to_dict() == {
        "code": "VALIDATION_ERROR",
        "message": "Invalid request parameters or payload.",
        "details": {"field": "email"},
    }


def test_app_error_catchable_as_base() -> None:
    with pytest.raises(AppError) as exc_info:
        raise NotFoundError("User 42 does not exist")

    assert isinstance(exc_info.value, NotFoundError)
    assert exc_info.value.code == "NOT_FOUND"
