import pytest
from src.services.inventory_service import InventoryService
from src.domain.inventory import InventoryItem, SKU, Quantity, Threshold
from uuid import uuid4

class FakeRepo:
    def __init__(self):
        self.items = {}

    def get_by_sku(self, sku):
        return self.items.get(sku)

    def save(self, item):
        self.items[item.sku.value] = item
        return item

    def list_all(self):
        return list(self.items.values())


@pytest.fixture
def repo():
    return FakeRepo()

@pytest.fixture
def service(repo):
    return InventoryService(repo)


def test_create_item(service):
    item = service.create_item("A01", 10, "pcs", 5)
    assert item.sku.value == "A01"
    assert item.on_hand.amount == 10

def test_create_duplicate_sku(service):
    service.create_item("A01", 10, "pcs", 5)
    with pytest.raises(ValueError):
        service.create_item("A01", 1, "pcs", 1)

def test_increase_stock(service):
    service.create_item("A01", 5, "pcs", 1)
    item = service.increase_stock("A01", 5, "INBOUND")
    assert item.on_hand.amount == 10

def test_decrease_stock(service):
    service.create_item("A01", 10, "pcs", 1)
    item = service.decrease_stock("A01", 5, "CONSUME")
    assert item.on_hand.amount == 5

def test_decrease_stock_fail(service):
    service.create_item("A01", 3, "pcs", 1)
    with pytest.raises(ValueError):
        service.decrease_stock("A01", 5, "CONSUME")

def test_reservation(service):
    service.create_item("A01", 10, "pcs", 1)
    item, res = service.reserve_stock("A01", "ORD1", 3)
    assert item.reserved.amount == 3
    assert len(item.reservations) == 1

def test_reservation_not_found():
    item = InventoryItem("1", SKU("A01"), Quantity(10), Quantity(0), Threshold(5))
    # try release nonexistent reservation
    with pytest.raises(ValueError):
        item.release("random-id")


def test_adjust_negative_delta():
    item = InventoryItem("1", SKU("A01"), Quantity(10), Quantity(0), Threshold(5))
    item.adjust(-3, "NEG_ADJUST")
    assert item.on_hand.amount == 7


def test_invariant_reserved_exceeds_onhand():
    item = InventoryItem("1", SKU("A01"), Quantity(5), Quantity(5), Threshold(1))
    with pytest.raises(ValueError):
        # force invariants break via decrease
        item.decrease(Quantity(1))


def test_is_low_stock_exact_border():
    item = InventoryItem("1", SKU("A01"), Quantity(5), Quantity(3), Threshold(2))
    # available = 2 → NOT low stock
    assert item.is_low_stock() is False

    item2 = InventoryItem("2", SKU("A02"), Quantity(5), Quantity(4), Threshold(2))
    # available = 1 → low stock
    assert item2.is_low_stock() is True

def test_get_item_not_found(service):
    with pytest.raises(ValueError):
        service.get_item("UNKNOWN")


def test_set_threshold(service):
    service.create_item("A01", 10, "pcs", 1)
    updated = service.set_threshold("A01", 99)
    assert updated.threshold.min_qty == 99


def test_adjust_stock(service):
    service.create_item("A01", 10, "pcs", 1)
    item = service.adjust_stock("A01", -3, "ADJ")
    assert item.on_hand.amount == 7


def test_get_availability(service):
    service.create_item("A01", 10, "pcs", 2)
    result = service.get_availability("A01")
    assert result["available"] == 10
    assert result["low_stock"] is False


def test_get_low_stock_items(service):
    service.create_item("A01", 3, "pcs", 5)  # low stock
    service.create_item("B01", 10, "pcs", 2)
    lows = service.get_low_stock_items()
    assert len(lows) == 1
    assert lows[0].sku.value == "A01"


def test_reserve_fail(service):
    service.create_item("A01", 3, "pcs", 1)
    with pytest.raises(ValueError):
        service.reserve_stock("A01", "ORDX", 10)


def test_adjust_stock_beyond_available(service):
    service.create_item("A01", 5, "pcs", 1)
    with pytest.raises(ValueError):
        service.adjust_stock("A01", -10, "ADJ")


def test_adjust_stock_positive(service):
    service.create_item("A01", 10, "pcs", 1)
    item = service.adjust_stock("A01", 5, "ADJ")
    assert item.on_hand.amount == 15


def test_get_availability_complete(service):
    service.create_item("A01", 10, "pcs", 2)
    availability = service.get_availability("A01")
    assert availability["sku"] == "A01"
    assert availability["on_hand"] == 10
    assert availability["reserved"] == 0
    assert availability["available"] == 10
    assert availability["uom"] == "pcs"


def test_get_low_stock_items_empty(service):
    service.create_item("A01", 10, "pcs", 1)
    lows = service.get_low_stock_items()
    assert lows == []


def test_low_stock_items_when_none_are_low(service):
    service.create_item("A01", 10, "pcs", 1)
    service.create_item("B01", 20, "pcs", 1)

    lows = service.get_low_stock_items()
    assert lows == []


def test_low_stock_items_mixed_cases(service):
    service.create_item("A01", 3, "pcs", 5)   # low
    service.create_item("B01", 100, "pcs", 1) # high
    service.create_item("C01", 1, "pcs", 2)   # low

    lows = service.get_low_stock_items()
    assert len(lows) == 2
    assert {i.sku.value for i in lows} == {"A01", "C01"}


def test_low_stock_items_large_list(service):
    for i in range(10):
        service.create_item(f"S{i}", 100, "pcs", 50)

    # bikin satu low stock
    service.create_item("LOW1", 10, "pcs", 20)

    lows = service.get_low_stock_items()
    assert len(lows) == 1
    assert lows[0].sku.value == "LOW1"


def test_low_stock_items_mixed(service):
    # low
    service.create_item("A01", 2, "pcs", 5)
    # high
    service.create_item("B01", 10, "pcs", 2)
    # low
    service.create_item("C01", 1, "pcs", 3)

    lows = service.get_low_stock_items()

    assert {i.sku.value for i in lows} == {"A01", "C01"}



def test_low_stock_items_many_items(service):
    # bikin banyak item tidak low
    for i in range(10):
        service.create_item(f"S{i}", 50, "pcs", 10)

    # bikin satu low stock
    service.create_item("LOWX", 1, "pcs", 5)

    lows = service.get_low_stock_items()
    assert len(lows) == 1
    assert lows[0].sku.value == "LOWX"


def test_release_reservation_success(repo):
    service = InventoryService(repo)

    # Create item
    item = service.create_item("A01", 10, "pcs", 2)

    # Reserve stock
    item, res = service.reserve_stock("A01", "ORD1", 3)

    # Release reservation via service
    updated_item = service.release_reservation("A01", res.id)

    assert updated_item.reserved.amount == 0
    assert len(updated_item.reservations) == 0


def test_release_reservation_not_found(repo):
    service = InventoryService(repo)

    service.create_item("A01", 10, "pcs", 2)

    with pytest.raises(ValueError, match="Reservation not found"):
        service.release_reservation("A01", "INVALID-ID")


