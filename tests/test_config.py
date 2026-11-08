from __future__ import annotations

import os

import pytest

from config import ConfigError, Settings


def test_load_requires_telegram_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    with pytest.raises(ConfigError, match="TELEGRAM_TOKEN"):
        Settings.load()


def test_load_applies_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_TOKEN", "tg-token")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    settings = Settings.load()
    assert settings.gemini_model == "models/gemini-2.5-flash"
    assert settings.chat_db_path == "chat_history.db"
    assert settings.log_level == "INFO"
