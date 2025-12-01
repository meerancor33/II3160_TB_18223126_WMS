from uuid import uuid4
from src.domain.inventory import InventoryItem, SKU, Quantity, Threshold


class InventoryService:
    def __init__(self, repo):
        self.repo = repo

    def get_item(self, sku: str):
        item = self.repo.get_by_sku(sku)
        if not item:
            raise ValueError("Item not found")
        return item

    def create_item(self, sku, initial_qty, uom, min_qty):
        if self.repo.get_by_sku(sku):
            raise ValueError("SKU already exists")
        item = InventoryItem(
            id=str(uuid4()),
            sku=SKU(sku),
            on_hand=Quantity(initial_qty, uom),
            reserved=Quantity(0, uom),
            threshold=Threshold(min_qty),
        )
        return self.repo.save(item)

    def list_items(self):
        return self.repo.list_all()

    def set_threshold(self, sku, min_qty):
        item = self.get_item(sku)
        item.threshold = Threshold(min_qty)
        return self.repo.save(item)

    def increase_stock(self, sku, qty, reason):
        item = self.get_item(sku)
        item.increase(Quantity(qty, item.on_hand.uom), reason)
        return self.repo.save(item)

    def decrease_stock(self, sku, qty, reason):
        item = self.get_item(sku)
        item.decrease(Quantity(qty, item.on_hand.uom), reason)
        return self.repo.save(item)

    def adjust_stock(self, sku, delta, reason):
        item = self.get_item(sku)
        item.adjust(Quantity(delta, item.on_hand.uom), reason)
        return self.repo.save(item)

    def reserve_stock(self, sku, order_id, qty):
        item = self.get_item(sku)
        reservation = item.reserve(order_id, Quantity(qty, item.on_hand.uom))
        self.repo.save(item)
        return item, reservation

    def release_reservation(self, sku, res_id):
        item = self.get_item(sku)
        item.release(res_id)
        return self.repo.save(item)

    def get_availability(self, sku):
        item = self.get_item(sku)
        return {
            "sku": sku,
            "on_hand": item.on_hand.amount,
            "reserved": item.reserved.amount,
            "available": item.available.amount,
            "uom": item.on_hand.uom,
            "low_stock": item.is_low_stock(),
        }

    def get_low_stock_items(self):
        return [i for i in self.list_items() if i.is_low_stock()]
