import pytest
from src.domain.inventory import SKU, Quantity, Threshold, InventoryItem

def test_sku_not_empty():
    with pytest.raises(ValueError):
        SKU("")

def test_quantity_negative():
    with pytest.raises(ValueError):
        Quantity(-1)

def test_quantity_add():
    q1 = Quantity(10)
    q2 = Quantity(5)
    assert q1.add(q2).amount == 15

def test_quantity_sub():
    q1 = Quantity(10)
    q2 = Quantity(3)
    assert q1.sub(q2).amount == 7

def test_quantity_sub_negative():
    q1 = Quantity(5)
    q2 = Quantity(10)
    with pytest.raises(ValueError):
        q1.sub(q2)

def test_inventory_available():
    item = InventoryItem("1", SKU("A01"), Quantity(10), Quantity(2), Threshold(3))
    assert item.available.amount == 8

def test_inventory_increase():
    item = InventoryItem("1", SKU("A01"), Quantity(10), Quantity(0), Threshold(3))
    item.increase(Quantity(5))
    assert item.on_hand.amount == 15

def test_inventory_decrease():
    item = InventoryItem("1", SKU("A01"), Quantity(10), Quantity(0), Threshold(3))
    item.decrease(Quantity(5))
    assert item.on_hand.amount == 5

def test_inventory_decrease_not_enough():
    item = InventoryItem("1", SKU("A01"), Quantity(3), Quantity(0), Threshold(3))
    with pytest.raises(ValueError):
        item.decrease(Quantity(5))

def test_inventory_low_stock():
    item = InventoryItem("1", SKU("A01"), Quantity(5), Quantity(4), Threshold(3))
    assert item.is_low_stock() == True

def test_inventory_adjust_positive():
    item = InventoryItem("1", SKU("A01"), Quantity(10), Quantity(0), Threshold(3))
    item.adjust(5, "ADJ_POS")
    assert item.on_hand.amount == 15
    assert len(item.moves) == 1
    assert item.moves[0].movement_type == "ADJUST"
    assert item.moves[0].qty.amount == 5

def test_inventory_adjust_negative():
    item = InventoryItem("1", SKU("A01"), Quantity(10), Quantity(0), Threshold(3))
    item.adjust(-4, "ADJ_NEG")
    assert item.on_hand.amount == 6
    assert len(item.moves) == 1
    assert item.moves[0].qty.amount == 4

def test_inventory_adjust_zero():
    item = InventoryItem("1", SKU("A01"), Quantity(10), Quantity(0), Threshold(3))
    item.adjust(0)
    assert item.on_hand.amount == 10   # no change
    assert len(item.moves) == 0        # no movement recorded

def test_inventory_adjust_negative_beyond_stock():
    item = InventoryItem("1", SKU("A01"), Quantity(5), Quantity(0), Threshold(3))
    with pytest.raises(ValueError):
        item.adjust(-10)

def test_inventory_adjust_keeps_invariants():
    item = InventoryItem("1", SKU("A01"), Quantity(5), Quantity(2), Threshold(1))
    item.adjust(3)  # on_hand becomes 8
    assert item.on_hand.amount >= item.reserved.amount   # invariant check

def test_inventory_invariants_reserved_greater_than_onhand():
    item = InventoryItem("1", SKU("A01"), Quantity(5), Quantity(4), Threshold(1))
    with pytest.raises(ValueError):
        item.adjust(-5)  # membuat on_hand=0 padahal reserved=4 → invalid

def test_sku_strip_invalid():
    # SKU("   ") → setelah strip menjadi "" → gagal
    with pytest.raises(ValueError):
        SKU("   ")

def test_inventory_adjust_zero_does_not_change_stock():
    item = InventoryItem("1", SKU("A01"), Quantity(10), Quantity(2), Threshold(3))
    before = item.on_hand.amount
    item.adjust(0)  # should do nothing
    assert item.on_hand.amount == before

def test_inventory_adjust_large_positive():
    item = InventoryItem("1", SKU("A01"), Quantity(5), Quantity(0), Threshold(1))
    item.adjust(1000)
    assert item.on_hand.amount == 1005

def test_sku_strip_and_normalize():
    sku = SKU("   A01   ")
    assert sku.value == "A01"   # whitespace trimmed

def test_inventory_release_success():
    item = InventoryItem("1", SKU("A01"), Quantity(10), Quantity(0), Threshold(3))
    res = item.reserve("ORD1", Quantity(3))

    item.release(res.id)

    assert item.reserved.amount == 0
    assert len(item.reservations) == 0

def test_inventory_adjust_negative_overflow():
    item = InventoryItem("1", SKU("A01"), Quantity(5), Quantity(0), Threshold(3))
    with pytest.raises(ValueError):
        item.adjust(-10)  # cannot adjust below zero stock

def test_release_reservation_success():
    item = InventoryItem("1", SKU("A01"), Quantity(10), Quantity(0), Threshold(3))
    res = item.reserve("ORD1", Quantity(3))

    item.release(res.id)

    assert item.reserved.amount == 0
    assert len(item.reservations) == 0


def test_quantity_add_uom_mismatch():
    q1 = Quantity(5, "pcs")
    q2 = Quantity(5, "kg")
    with pytest.raises(ValueError):
        q1.add(q2)

def test_quantity_sub_uom_mismatch():
    q1 = Quantity(5, "pcs")
    q2 = Quantity(1, "kg")
    with pytest.raises(ValueError):
        q1.sub(q2)


def test_invariant_on_hand_negative():
    item = InventoryItem("1", SKU("A01"), Quantity(1), Quantity(0), Threshold(1))

    # Force-break state WITHOUT calling Quantity constructor
    object.__setattr__(item.on_hand, "amount", -5)

    with pytest.raises(ValueError, match="On hand cannot be negative"):
        item._ensure_invariants()


def test_invariant_reserved_negative():
    item = InventoryItem("1", SKU("A01"), Quantity(10), Quantity(0), Threshold(1))

    # Create valid reservation
    res = item.reserve("ORD1", Quantity(3))

    # BREAK state intentionally
    object.__setattr__(item.reserved, "amount", -1)

    with pytest.raises(ValueError, match="Reserved cannot be negative"):
        item._ensure_invariants()
