"""FastAPI application serving the Telegram Web App."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .menu import menu_to_sections

app = FastAPI(title="Choyxona Web App", version="0.1.0")

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "title": "Choyxona buyurtma"},
    )


@app.get("/menu")
async def menu() -> dict[str, object]:
    return {
        "sections": menu_to_sections(),
        "currency": "so'm",
    }


__all__ = ["app"]
