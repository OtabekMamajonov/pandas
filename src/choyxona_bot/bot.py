"""Telegram bot entrypoint for the choyxona Web App."""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
import logging

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .config import Settings
from .menu import MENU_BY_ID
from .schemas import OrderRequest, StoredOrder, StoredOrderItem, parse_order_payload
from .storage import OrderStorage

LOGGER = logging.getLogger(__name__)


def format_currency(amount: Decimal) -> str:
    return f"{amount:,.0f} so'm".replace(",", " ")


def build_items(order: OrderRequest) -> tuple[list[StoredOrderItem], Decimal]:
    items: list[StoredOrderItem] = []
    total = Decimal(0)
    for item_req in order.items:
        menu_item = MENU_BY_ID.get(item_req.id)
        if menu_item is None:
            raise ValueError(f"Menu item '{item_req.id}' mavjud emas")
        subtotal = menu_item.price * item_req.quantity
        items.append(
            StoredOrderItem(
                menu_id=menu_item.id,
                name=menu_item.name,
                quantity=item_req.quantity,
                unit_price=menu_item.price,
                subtotal=subtotal,
            )
        )
        total += subtotal
    return items, total


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config: Settings = context.bot_data["config"]
    button = KeyboardButton(
        text="🧾 Buyurtma yaratish",
        web_app=WebAppInfo(url=config.webapp_url),
    )
    reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
    await update.message.reply_text(
        "Assalomu alaykum! Web App orqali buyurtmalarni qabul qilish uchun tugmani bosing.",
        reply_markup=reply_markup,
    )


async def handle_web_app(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    storage: OrderStorage = context.bot_data["storage"]
    web_app_data = update.effective_message.web_app_data
    if web_app_data is None:
        return

    try:
        order_payload = parse_order_payload(web_app_data.data)
    except ValueError as exc:
        LOGGER.warning("Invalid payload received: %s", exc)
        await update.message.reply_text("Buyurtma ma'lumotida xatolik. Iltimos, qaytadan urinib ko'ring.")
        return

    try:
        items, total = build_items(order_payload)
    except ValueError as exc:
        LOGGER.warning("Invalid item: %s", exc)
        await update.message.reply_text(str(exc))
        return

    discount = Decimal(order_payload.discount)
    if discount > total:
        discount = total
    net_total = total - discount
    paid = Decimal(order_payload.paid)
    change = max(paid - net_total, Decimal(0))
    balance = max(net_total - paid, Decimal(0))

    stored_order = StoredOrder(
        chat_id=update.effective_chat.id,
        username=update.effective_user.username if update.effective_user else None,
        customer=order_payload.customer.strip(),
        discount=discount,
        paid=paid,
        total=net_total,
        change=change,
        balance=balance,
        created_at=datetime.utcnow(),
        items=items,
    )
    stored_order = storage.record_order(stored_order)

    lines = ["<b>Buyurtma qabul qilindi</b>"]
    if stored_order.customer:
        lines.append(f"Mijoz: {stored_order.customer}")
    for item in stored_order.items:
        lines.append(
            f"• {item.name} × {item.quantity} = {format_currency(item.subtotal)}"
        )
    lines.append(f"Jami: {format_currency(total)}")
    if discount:
        lines.append(f"Chegirma: −{format_currency(discount)}")
    lines.append(f"To'lanishi kerak: {format_currency(stored_order.total)}")
    lines.append(f"Olingan to'lov: {format_currency(stored_order.paid)}")
    if stored_order.change:
        lines.append(f"Qaytim: {format_currency(stored_order.change)}")
    if stored_order.balance:
        lines.append(f"Qarz: {format_currency(stored_order.balance)}")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
    )


async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    storage: OrderStorage = context.bot_data["storage"]
    today = date.today()
    summary = storage.summarize(today)
    lines = ["<b>Kunlik hisobot</b>"]
    lines.append(f"Buyurtmalar soni: {summary.total_orders}")
    lines.append(f"Jami tushum: {format_currency(summary.total_amount)}")
    lines.append(f"Olingan to'lovlar: {format_currency(summary.total_paid)}")
    lines.append(f"Qaytim berilgan: {format_currency(summary.total_change)}")
    lines.append(f"Qarzdorlik: {format_currency(summary.total_balance)}")
    await update.message.reply_text(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
    )


def create_application(config: Settings) -> Application:
    application = ApplicationBuilder().token(config.bot_token).build()
    storage = OrderStorage(config.database_path)
    application.bot_data["config"] = config
    application.bot_data["storage"] = storage

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("summary", summary))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app))

    return application


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    config = Settings.from_env()
    application = create_application(config)
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
