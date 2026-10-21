import pytest
from pydantic import ValidationError

from ts_alert.config import Settings, get_settings


def test_default_settings() -> None:
    get_settings.cache_clear()
    settings = Settings()
    assert settings.app_env == "development"
    assert settings.log_level == "info"


def test_invalid_app_env_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "staging")
    get_settings.cache_clear()
    with pytest.raises(ValidationError):
        Settings()


def test_valid_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("LOG_LEVEL", "error")
    get_settings.cache_clear()
    settings = Settings()
    assert settings.app_env == "production"
    assert settings.log_level == "error"
