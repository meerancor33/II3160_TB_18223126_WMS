import pytest

from src.domain.inventory import (
    InventoryItem,
    SKU,
    Quantity,
    Threshold,
)


def make_item(
    sku: str = "TEST-SKU",
    on_hand: int = 0,
    reserved: int = 0,
    min_qty: int = 0,
) -> InventoryItem:
    """
    Helper kecil untuk membuat InventoryItem siap pakai.
    """
    return InventoryItem(
        id="item-1",
        sku=SKU(sku),
        on_hand=Quantity(on_hand, "pcs"),
        reserved=Quantity(reserved, "pcs"),
        threshold=Threshold(min_qty),
    )


def test_increase_stock_adds_on_hand():
    item = make_item(on_hand=10)

    item.increase(Quantity(5, "pcs"), reason="inbound")

    assert item.on_hand.amount == 15
    assert item.available.amount == 15
    assert len(item.moves) == 1
    assert item.moves[0].movement_type == "IN"


def test_reserve_reduces_available_and_increases_reserved():
    item = make_item(on_hand=10)

    res = item.reserve(order_id="ORD-1", qty=Quantity(4, "pcs"))

    assert item.on_hand.amount == 10
    assert item.reserved.amount == 4
    assert item.available.amount == 6
    assert len(item.reservations) == 1
    assert res.order_id == "ORD-1"


def test_reserve_raises_when_not_enough_available():
    item = make_item(on_hand=5)

    with pytest.raises(ValueError):
        item.reserve(order_id="ORD-2", qty=Quantity(10, "pcs"))


def test_decrease_reduces_on_hand_and_available():
    item = make_item(on_hand=20)

    item.decrease(Quantity(5, "pcs"), reason="consume")

    assert item.on_hand.amount == 15
    assert item.available.amount == 15
    assert len(item.moves) == 1
    assert item.moves[0].movement_type == "OUT"


def test_low_stock_flag_works():
    item = make_item(on_hand=5, min_qty=10)

    assert item.is_low_stock() is True

    item.increase(Quantity(10, "pcs"))
    assert item.is_low_stock() is False
