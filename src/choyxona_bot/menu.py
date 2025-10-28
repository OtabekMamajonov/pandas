"""Menu catalogue for the choyxona."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True, slots=True)
class MenuItem:
    id: str
    name: str
    category: str
    price: Decimal

    def as_dict(self) -> dict[str, str | float]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": float(self.price),
        }


MENU: tuple[MenuItem, ...] = (
    MenuItem(id="tea_green", name="Ko'k choy", category="Ichimliklar", price=Decimal("5000")),
    MenuItem(id="tea_black", name="Qora choy", category="Ichimliklar", price=Decimal("4000")),
    MenuItem(id="lepyoshka", name="Non", category="Qo'shimchalar", price=Decimal("3000")),
    MenuItem(id="somsa_lamb", name="Qo'y go'shtli somsa", category="Somsa", price=Decimal("12000")),
    MenuItem(id="somsa_beef", name="Mol go'shtli somsa", category="Somsa", price=Decimal("11000")),
    MenuItem(id="plov", name="Palov", category="Asosiy taomlar", price=Decimal("28000")),
    MenuItem(id="lagman", name="Lag'mon", category="Asosiy taomlar", price=Decimal("26000")),
    MenuItem(id="shashlik", name="Kabob", category="Asosiy taomlar", price=Decimal("18000")),
    MenuItem(id="salad", name="Achchiq-chuchuk", category="Salatlar", price=Decimal("9000")),
    MenuItem(id="ayran", name="Ayran", category="Ichimliklar", price=Decimal("7000")),
)

MENU_BY_ID = {item.id: item for item in MENU}
MENU_BY_CATEGORY: dict[str, tuple[MenuItem, ...]] = {}
for item in MENU:
    MENU_BY_CATEGORY.setdefault(item.category, tuple())
# Since tuples are immutable, rebuild category mapping explicitly
MENU_BY_CATEGORY = {
    category: tuple(item for item in MENU if item.category == category)
    for category in {item.category for item in MENU}
}


def menu_to_sections(items: Iterable[MenuItem] = MENU) -> list[dict[str, object]]:
    """Return menu items grouped by category for front-end consumption."""

    sections: dict[str, list[dict[str, object]]] = {}
    for item in items:
        sections.setdefault(item.category, []).append(item.as_dict())
    return [
        {
            "category": category,
            "items": sections[category],
        }
        for category in sorted(sections.keys())
    ]


__all__ = ["MenuItem", "MENU", "MENU_BY_ID", "menu_to_sections"]
