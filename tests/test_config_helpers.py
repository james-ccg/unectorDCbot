from pathlib import Path

import pytest

from unector.config import Settings

def test_settings_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("unector.config.load_dotenv", lambda: None)
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="DISCORD_TOKEN"):
        Settings.from_env()

def test_settings_parses_app_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("unector.config.load_dotenv", lambda: None)
    monkeypatch.setenv("DISCORD_TOKEN", "test-token")
    monkeypatch.setenv("STEAM_APP_IDS", "730,570,730")
    monkeypatch.setenv("DATABASE_PATH", "test.sqlite3")
    settings = Settings.from_env()
    assert settings.steam_app_ids == (730, 570)
    assert settings.database_path == Path("test.sqlite3")

def test_poll_interval_is_validated(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("unector.config.load_dotenv", lambda: None)
    monkeypatch.setenv("DISCORD_TOKEN", "test-token")
    monkeypatch.setenv("MEDIA_POLL_MINUTES", "2")
    with pytest.raises(RuntimeError, match="MEDIA_POLL_MINUTES"):
        Settings.from_env()
