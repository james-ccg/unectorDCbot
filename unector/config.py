from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True, slots=True)
class Settings:
    discord_token: str
    discord_guild_id: int | None
    game_news_channel_id: int | None
    game_news_role_id: int | None
    steam_app_ids: tuple[int, ...]
    media_poll_minutes: int
    database_path: Path

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.getenv("DISCORD_TOKEN", "").strip()
        if not token:
            raise RuntimeError("DISCORD_TOKEN is missing. Copy .env.example to .env and fill it in.")

        def optional_int(name: str) -> int | None:
            value = os.getenv(name, "").strip()
            if not value:
                return None
            try:
                number = int(value)
            except ValueError as exc:
                raise RuntimeError(f"{name} must be a numeric Discord ID.") from exc
            if number <= 0:
                raise RuntimeError(f"{name} must be a positive integer.")
            return number

        raw_app_ids = os.getenv("STEAM_APP_IDS", "730").strip()
        try:
            app_ids = tuple(dict.fromkeys(int(item.strip()) for item in raw_app_ids.split(",") if item.strip()))
        except ValueError as exc:
            raise RuntimeError("STEAM_APP_IDS must be comma-separated numeric app IDs.") from exc

        poll_minutes = int(os.getenv("MEDIA_POLL_MINUTES", "30"))
        if not 10 <= poll_minutes <= 1440:
            raise RuntimeError("MEDIA_POLL_MINUTES must be between 10 and 1440.")

        db_path = Path(os.getenv("DATABASE_PATH", "data/unector.sqlite3"))
        return cls(
            discord_token=token,
            discord_guild_id=optional_int("DISCORD_GUILD_ID"),
            game_news_channel_id=optional_int("GAME_NEWS_CHANNEL_ID"),
            game_news_role_id=optional_int("GAME_NEWS_ROLE_ID"),
            steam_app_ids=app_ids,
            media_poll_minutes=poll_minutes,
            database_path=db_path,
        )
