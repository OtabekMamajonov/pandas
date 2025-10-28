"""Choyxona Telegram Web App bot package."""

from importlib.metadata import version

__all__ = ["__version__"]

try:
    __version__ = version("choyxona-telegram-webapp")
except Exception:  # pragma: no cover - fallback when package metadata is missing
    __version__ = "0.1.0"
