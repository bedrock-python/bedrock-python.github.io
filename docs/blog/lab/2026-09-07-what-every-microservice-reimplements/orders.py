"""Application decisions; no HTTP framework or infrastructure library imports."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Order:
    id: int
    sku: str
    quantity: int


class OrderMissing(Exception):
    pass


class StockUnavailable(Exception):
    pass


class OrderStore(Protocol):
    async def find(self, order_id: int) -> Order | None: ...


class StockReader(Protocol):
    async def available(self, sku: str) -> int: ...


class OrderView:
    def __init__(self, store: OrderStore, stock: StockReader):
        self.store, self.stock = store, stock

    async def get(self, order_id: int) -> dict:
        order = await self.store.find(order_id)
        if order is None:
            raise OrderMissing(order_id)
        available = await self.stock.available(order.sku)
        return {
            "order_id": order.id,
            "available": available,
            "can_fulfill": available >= order.quantity,
        }
