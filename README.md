# Choyxona Telegram Web App Bot

This project provides a Telegram bot with an accompanying Web App tailored for a choyxona (teahouse).
It helps staff record sold dishes and products, calculates totals, and keeps a persistent sales history.

## Features

- FastAPI-powered Web App designed for Telegram Web App integration.
- Telegram bot built on `python-telegram-bot` v20 for receiving orders sent from the Web App.
- SQLite-backed storage that records every order with its line items, totals, payments, and change.
- Built-in menu catalogue with pricing so that totals are re-calculated server-side for accuracy.
- Daily summary command (`/summary`) to view revenue, total receipts, and outstanding balances.

## Project structure

```
.
├── README.md
├── pyproject.toml
└── src/
    └── choyxona_bot/
        ├── __init__.py
        ├── bot.py
        ├── config.py
        ├── menu.py
        ├── schemas.py
        ├── storage.py
        └── webapp.py
```

The Web App's HTML template lives in `src/choyxona_bot/templates/index.html`.

## Getting started

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Configure environment variables

Create a `.env` file or export the variables in your shell:

```
BOT_TOKEN="your-telegram-bot-token"
WEBAPP_URL="https://example.com"  # Public HTTPS URL that Telegram users will open
WEBAPP_HOST="0.0.0.0"
WEBAPP_PORT="8000"
DATABASE_PATH="./data/orders.db"
```

### 3. Run the Web App

```bash
uvicorn choyxona_bot.webapp:app --host "$WEBAPP_HOST" --port "$WEBAPP_PORT"
```

Host the Web App at a public HTTPS URL (for example using a reverse proxy, render.com, fly.io, etc.).
Update `WEBAPP_URL` to point to this deployed address.

### 4. Run the bot

```bash
python -m choyxona_bot.bot
```

The bot listens for Web App data and records orders into the SQLite database specified by `DATABASE_PATH`.

## Using the system

1. A staff member starts the bot conversation and taps the "🧾 Buyurtma yaratish" button to open the Web App inside Telegram.
2. They fill out the order: select dishes, adjust quantities, optionally add a discount, and note how much the customer paid.
3. When they tap "Buyurtmani yuborish", the Web App sends the structured order data back to the bot.
4. The bot re-computes totals based on the authoritative menu, stores the order, and replies with a receipt summary, including change due.
5. The `/summary` command aggregates all orders for the current day, listing revenue, payments, and outstanding amounts.

## Development tips

- Adjust menu items in `menu.py`. Each item has an `id`, `name`, `category`, and price in UZS.
- `storage.py` uses SQLite with automatic migrations; delete the database file to reset data in development.
- Extend `bot.py` to add commands for exporting reports or editing menu data if needed.
- The front-end template (`templates/index.html`) is a vanilla JavaScript single-page experience; customise styling or behaviour there.

## License

This project is provided as-is to serve as a starting point for choyxona order management automation.
