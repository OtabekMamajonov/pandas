"""Configuration helpers for the choyxona bot."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(slots=True)
class Settings:
    """Runtime configuration loaded from environment variables."""

    bot_token: str
    webapp_url: str
    webapp_host: str = "0.0.0.0"
    webapp_port: int = 8000
    database_path: Path = Path("./data/orders.db")

    @classmethod
    def from_env(cls) -> "Settings":
        bot_token = os.environ.get("BOT_TOKEN")
        if not bot_token:
            raise RuntimeError("BOT_TOKEN environment variable is required")

        webapp_url = os.environ.get("WEBAPP_URL")
        if not webapp_url:
            raise RuntimeError("WEBAPP_URL environment variable is required")

        webapp_host = os.environ.get("WEBAPP_HOST", "0.0.0.0")
        webapp_port = int(os.environ.get("WEBAPP_PORT", "8000"))
        database_path = Path(os.environ.get("DATABASE_PATH", "./data/orders.db")).expanduser()

        database_path.parent.mkdir(parents=True, exist_ok=True)

        return cls(
            bot_token=bot_token,
            webapp_url=webapp_url,
            webapp_host=webapp_host,
            webapp_port=webapp_port,
            database_path=database_path,
        )


__all__ = ["Settings"]
