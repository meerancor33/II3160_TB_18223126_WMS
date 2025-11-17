from typing import List, Optional
from pydantic import BaseModel, Field


class InventoryStats(BaseModel):
    sku: str
    on_hand: int
    reserved: int
    available: int
    uom: str
    low_stock: bool


class ReservationDto(BaseModel):
    id: str
    order_id: str
    qty: int


class InventoryItemDto(BaseModel):
    id: str
    sku: str
    on_hand: int
    reserved: int
    available: int
    uom: str
    min_qty: int
    low_stock: bool
    reservations: List[ReservationDto] = []


class CreateItemRequest(BaseModel):
    sku: str = Field(..., example="SKU-001")
    initial_qty: int = 0
    uom: str = "pcs"
    min_qty: int = 0


class IncreaseStockRequest(BaseModel):
    qty: int
    reason: Optional[str] = "INBOUND"


class DecreaseStockRequest(BaseModel):
    qty: int
    reason: Optional[str] = "CONSUME"


class ReserveStockRequest(BaseModel):
    order_id: str
    qty: int


class ReleaseReservationRequest(BaseModel):
    reservation_id: str


class AdjustStockRequest(BaseModel):
    delta: int
    reason: Optional[str] = "ADJUST"


class SetThresholdRequest(BaseModel):
    min_qty: int
