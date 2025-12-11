from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4


# ---------- Value Objects ----------

@dataclass(frozen=True)
class SKU:
    value: str

    def __post_init__(self):
        cleaned = self.value.strip()  # normalize whitespace
        if not cleaned:
            raise ValueError("SKU cannot be empty")
        object.__setattr__(self, "value", cleaned)


@dataclass(frozen=True)
class Quantity:
    amount: int
    uom: str = "pcs"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Quantity cannot be negative")

    def add(self, other: "Quantity") -> "Quantity":
        if self.uom != other.uom:
            raise ValueError("UOM mismatch")
        return Quantity(self.amount + other.amount, self.uom)

    def sub(self, other: "Quantity") -> "Quantity":
        if self.uom != other.uom:
            raise ValueError("UOM mismatch")
        if self.amount - other.amount < 0:
            raise ValueError("Resulting quantity cannot be negative")
        return Quantity(self.amount - other.amount, self.uom)


@dataclass(frozen=True)
class Batch:
    code: Optional[str] = None
    exp_date: Optional[datetime] = None


@dataclass(frozen=True)
class Threshold:
    min_qty: int

    def is_low(self, qty: Quantity) -> bool:
        return qty.amount < self.min_qty


# ---------- Entities ----------

@dataclass
class Reservation:
    id: str
    order_id: str
    reserved_qty: Quantity
    created_at: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def create(order_id: str, qty: Quantity) -> "Reservation":
        return Reservation(id=str(uuid4()), order_id=order_id, reserved_qty=qty)


@dataclass
class StockMove:
    id: str
    movement_type: str  # IN, OUT, ADJUST
    qty: Quantity
    created_at: datetime = field(default_factory=datetime.utcnow)
    reason: Optional[str] = None

    @staticmethod
    def create(movement_type: str, qty: Quantity, reason: Optional[str] = None) -> "StockMove":
        return StockMove(
            id=str(uuid4()),
            movement_type=movement_type,
            qty=qty,
            reason=reason,
        )


# ---------- Aggregate Root ----------

@dataclass
class InventoryItem:
    id: str
    sku: SKU
    on_hand: Quantity
    reserved: Quantity
    threshold: Threshold
    batch: Optional[Batch] = None
    reservations: List[Reservation] = field(default_factory=list)
    moves: List[StockMove] = field(default_factory=list)

    # invariants:
    # - on_hand.amount >= 0
    # - reserved.amount >= 0
    # - reserved.amount <= on_hand.amount

    @property
    def available(self) -> Quantity:
        return Quantity(self.on_hand.amount - self.reserved.amount, self.on_hand.uom)

    def _ensure_invariants(self):
        if self.on_hand.amount < 0:
            raise ValueError("On hand cannot be negative")
        if self.reserved.amount < 0:
            raise ValueError("Reserved cannot be negative")
        if self.reserved.amount > self.on_hand.amount:
            raise ValueError("Reserved cannot exceed on hand")

    def increase(self, qty: Quantity, reason: str = "INBOUND"):
        self.on_hand = self.on_hand.add(qty)
        self.moves.append(StockMove.create("IN", qty, reason))
        self._ensure_invariants()

    def decrease(self, qty: Quantity, reason: str = "CONSUME"):
        if qty.amount > self.available.amount:
            raise ValueError("Not enough available stock to decrease")
        self.on_hand = self.on_hand.sub(qty)
        self.moves.append(StockMove.create("OUT", qty, reason))
        self._ensure_invariants()

    def reserve(self, order_id: str, qty: Quantity) -> Reservation:
        if qty.amount > self.available.amount:
            raise ValueError("Not enough available stock to reserve")
        self.reserved = self.reserved.add(qty)
        reservation = Reservation.create(order_id, qty)
        self.reservations.append(reservation)
        self._ensure_invariants()
        return reservation

    def release(self, reservation_id: str):
        res = next((r for r in self.reservations if r.id == reservation_id), None)
        if not res:
            raise ValueError("Reservation not found")
        self.reservations.remove(res)
        self.reserved = self.reserved.sub(res.reserved_qty)
        self._ensure_invariants()

    def adjust(self, delta: int, reason: str = "ADJUST"):
        """
        Adjust stock using a positive or negative integer delta.
        Rules:
        - delta > 0  → increase stock
        - delta < 0  → decrease stock
        - Quantity must always be positive inside the domain
        """
        if delta == 0:
            return  # no operation
        if delta > 0:
            # Positive adjustment: add stock
            self.on_hand = self.on_hand.add(Quantity(delta, self.on_hand.uom))
            moved_qty = Quantity(delta, self.on_hand.uom)
        else:
            # Negative adjustment: reduce stock
            abs_delta = -delta
            if abs_delta > self.on_hand.amount:
                raise ValueError("Cannot adjust below zero stock")
            self.on_hand = self.on_hand.sub(Quantity(abs_delta, self.on_hand.uom))
            moved_qty = Quantity(abs_delta, self.on_hand.uom)
        # Record stock movement
        self.moves.append(StockMove.create("ADJUST", moved_qty, reason))
        # Re-validate invariants
        self._ensure_invariants()

    def is_low_stock(self) -> bool:
        return self.threshold.is_low(self.available)