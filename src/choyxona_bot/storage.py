"""SQLite-backed storage for orders."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
import sqlite3
from pathlib import Path
from typing import Iterator

from .schemas import OrdersSummary, StoredOrder, StoredOrderItem


CREATE_ORDERS_TABLE = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    username TEXT,
    customer TEXT,
    discount NUMERIC NOT NULL,
    paid NUMERIC NOT NULL,
    total NUMERIC NOT NULL,
    change NUMERIC NOT NULL,
    balance NUMERIC NOT NULL,
    created_at TEXT NOT NULL
)
"""

CREATE_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    menu_id TEXT NOT NULL,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC NOT NULL,
    subtotal NUMERIC NOT NULL,
    FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
)
"""


@dataclass(slots=True)
class OrderStorage:
    """Persistence layer for orders."""

    path: Path

    def __post_init__(self) -> None:
        self.path = self.path.expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute(CREATE_ORDERS_TABLE)
            conn.execute(CREATE_ITEMS_TABLE)
            conn.commit()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        try:
            yield conn
        finally:
            conn.close()

    def record_order(self, order: StoredOrder) -> StoredOrder:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO orders (chat_id, username, customer, discount, paid, total, change, balance, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order.chat_id,
                    order.username,
                    order.customer,
                    float(order.discount),
                    float(order.paid),
                    float(order.total),
                    float(order.change),
                    float(order.balance),
                    order.created_at.isoformat(),
                ),
            )
            order_id = cursor.lastrowid
            for item in order.items:
                cursor.execute(
                    """
                    INSERT INTO order_items (order_id, menu_id, name, quantity, unit_price, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        order_id,
                        item.menu_id,
                        item.name,
                        item.quantity,
                        float(item.unit_price),
                        float(item.subtotal),
                    ),
                )
            conn.commit()
        return order.model_copy(update={"id": order_id})

    def list_orders(self, day: date | None = None) -> list[StoredOrder]:
        query = "SELECT * FROM orders"
        params: list[object] = []
        if day is not None:
            start = datetime.combine(day, datetime.min.time())
            end = datetime.combine(day, datetime.max.time())
            query += " WHERE created_at BETWEEN ? AND ?"
            params.extend([start.isoformat(), end.isoformat()])
        query += " ORDER BY created_at ASC"

        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            orders = []
            for row in cursor.fetchall():
                items = self._fetch_order_items(conn, row["id"])
                orders.append(
                    StoredOrder(
                        id=row["id"],
                        chat_id=row["chat_id"],
                        username=row["username"],
                        customer=row["customer"],
                        discount=Decimal(str(row["discount"])),
                        paid=Decimal(str(row["paid"])),
                        total=Decimal(str(row["total"])),
                        change=Decimal(str(row["change"])),
                        balance=Decimal(str(row["balance"])),
                        created_at=datetime.fromisoformat(row["created_at"]),
                        items=items,
                    )
                )
        return orders

    def _fetch_order_items(self, conn: sqlite3.Connection, order_id: int) -> list[StoredOrderItem]:
        cursor = conn.execute(
            "SELECT menu_id, name, quantity, unit_price, subtotal FROM order_items WHERE order_id = ?",
            (order_id,),
        )
        return [
            StoredOrderItem(
                menu_id=row[0],
                name=row[1],
                quantity=row[2],
                unit_price=Decimal(str(row[3])),
                subtotal=Decimal(str(row[4])),
            )
            for row in cursor.fetchall()
        ]

    def summarize(self, day: date | None = None) -> OrdersSummary:
        orders = self.list_orders(day)
        total_amount = sum((order.total for order in orders), Decimal(0))
        total_paid = sum((order.paid for order in orders), Decimal(0))
        total_balance = sum((order.balance for order in orders), Decimal(0))
        total_change = sum((order.change for order in orders), Decimal(0))
        return OrdersSummary(
            total_orders=len(orders),
            total_amount=total_amount,
            total_paid=total_paid,
            total_balance=total_balance,
            total_change=total_change,
        )


__all__ = ["OrderStorage"]
