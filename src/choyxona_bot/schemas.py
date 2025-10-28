"""Pydantic schemas shared between the bot and the Web App."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Sequence

from pydantic import BaseModel, Field, RootModel, ValidationError, model_validator


class OrderItemRequest(BaseModel):
    """Incoming order line item from the Web App."""

    id: str = Field(..., description="Menu item identifier")
    quantity: int = Field(..., ge=1, description="Number of units requested")


class OrderRequest(BaseModel):
    """Order payload sent by the Web App."""

    customer: str = Field("", description="Customer name or table number")
    items: Sequence[OrderItemRequest]
    discount: int = Field(0, ge=0, description="Discount amount in sums")
    paid: int = Field(0, ge=0, description="Amount paid by customer in sums")

    @model_validator(mode="after")
    def ensure_items_present(self) -> "OrderRequest":
        if not self.items:
            raise ValueError("At least one item is required")
        return self


class StoredOrderItem(BaseModel):
    menu_id: str
    name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class StoredOrder(BaseModel):
    id: int | None = None
    chat_id: int
    username: str | None
    customer: str
    discount: Decimal
    paid: Decimal
    total: Decimal
    change: Decimal
    balance: Decimal
    created_at: datetime
    items: Sequence[StoredOrderItem]


class OrdersSummary(BaseModel):
    total_orders: int
    total_amount: Decimal
    total_paid: Decimal
    total_balance: Decimal
    total_change: Decimal


class StoredOrderList(RootModel[list[StoredOrder]]):
    pass


def parse_order_payload(raw_data: str) -> OrderRequest:
    """Parse a JSON string coming from Telegram Web App data."""

    try:
        return OrderRequest.model_validate_json(raw_data)
    except ValidationError as exc:  # pragma: no cover - logged for operator visibility
        raise ValueError(f"Invalid order payload: {exc}") from exc


__all__ = [
    "OrderItemRequest",
    "OrderRequest",
    "StoredOrderItem",
    "StoredOrder",
    "OrdersSummary",
    "StoredOrderList",
    "parse_order_payload",
]
