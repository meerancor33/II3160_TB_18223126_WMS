from typing import Dict, List, Optional
from uuid import uuid4

from src.domain.inventory import (
    InventoryItem,
    SKU,
    Quantity,
    Threshold,
    Batch,
)


class InventoryRepositoryInMemory:
    def __init__(self):
        self._items: Dict[str, InventoryItem] = {}
        self._by_sku: Dict[str, str] = {}

    def list_all(self) -> List[InventoryItem]:
        return list(self._items.values())

    def get_by_id(self, item_id: str) -> Optional[InventoryItem]:
        return self._items.get(item_id)

    def get_by_sku(self, sku: str) -> Optional[InventoryItem]:
        item_id = self._by_sku.get(sku)
        if not item_id:
            return None
        return self._items[item_id]

    def save(self, item: InventoryItem) -> InventoryItem:
        self._items[item.id] = item
        self._by_sku[item.sku.value] = item.id
        return item


class InventoryService:
    def __init__(self, repo: InventoryRepositoryInMemory):
        self.repo = repo

    # ------ Use cases untuk admin gudang ------

    def create_item(self, sku: str, initial_qty: int = 0, uom: str = "pcs",
                    min_qty: int = 0) -> InventoryItem:
        if self.repo.get_by_sku(sku):
            raise ValueError("Item with this SKU already exists")

        item = InventoryItem(
            id=str(uuid4()),
            sku=SKU(sku),
            on_hand=Quantity(initial_qty, uom),
            reserved=Quantity(0, uom),
            threshold=Threshold(min_qty),
            batch=None,
        )
        self.repo.save(item)
        return item

    def list_items(self) -> List[InventoryItem]:
        return self.repo.list_all()

    def get_item(self, sku: str) -> InventoryItem:
        item = self.repo.get_by_sku(sku)
        if not item:
            raise ValueError("Item not found")
        return item

    def set_threshold(self, sku: str, min_qty: int) -> InventoryItem:
        item = self.get_item(sku)
        item.threshold = Threshold(min_qty)
        self.repo.save(item)
        return item

    # ------ Use cases inbound / outbound / order ------

    def increase_stock(self, sku: str, qty: int, reason: str = "INBOUND") -> InventoryItem:
        item = self.get_item(sku)
        item.increase(Quantity(qty, item.on_hand.uom), reason)
        self.repo.save(item)
        return item

    def decrease_stock(self, sku: str, qty: int, reason: str = "CONSUME") -> InventoryItem:
        item = self.get_item(sku)
        item.decrease(Quantity(qty, item.on_hand.uom), reason)
        self.repo.save(item)
        return item

    def reserve_stock(self, sku: str, order_id: str, qty: int):
        item = self.get_item(sku)
        reservation = item.reserve(order_id, Quantity(qty, item.on_hand.uom))
        self.repo.save(item)
        return item, reservation

    def release_reservation(self, sku: str, reservation_id: str) -> InventoryItem:
        item = self.get_item(sku)
        item.release(reservation_id)
        self.repo.save(item)
        return item

    def adjust_stock(self, sku: str, delta: int, reason: str = "ADJUST") -> InventoryItem:
        item = self.get_item(sku)
        item.adjust(Quantity(delta, item.on_hand.uom), reason)
        self.repo.save(item)
        return item

    # ------ Query untuk OHS / manajer ------

    def get_availability(self, sku: str):
        item = self.get_item(sku)
        return {
            "sku": item.sku.value,
            "on_hand": item.on_hand.amount,
            "reserved": item.reserved.amount,
            "available": item.available.amount,
            "uom": item.on_hand.uom,
            "low_stock": item.is_low_stock(),
        }

    def get_low_stock_items(self) -> List[InventoryItem]:
        return [i for i in self.repo.list_all() if i.is_low_stock()]