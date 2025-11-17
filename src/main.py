from fastapi import FastAPI, HTTPException
from typing import List
from fastapi.responses import RedirectResponse

from src.services.inventory_service import InventoryRepositoryInMemory, InventoryService
from src.schemas.inventory import (
    CreateItemRequest,
    IncreaseStockRequest,
    DecreaseStockRequest,
    ReserveStockRequest,
    ReleaseReservationRequest,
    AdjustStockRequest,
    SetThresholdRequest,
    InventoryItemDto,
    InventoryStats,
    ReservationDto,
)

app = FastAPI(
    title="Inventory Control API",
    version="0.1.0",
    description="Inventory Control Core Context - Milestone 4",
)

repo = InventoryRepositoryInMemory()
service = InventoryService(repo)


def to_item_dto(item) -> InventoryItemDto:
    return InventoryItemDto(
        id=item.id,
        sku=item.sku.value,
        on_hand=item.on_hand.amount,
        reserved=item.reserved.amount,
        available=item.available.amount,
        uom=item.on_hand.uom,
        min_qty=item.threshold.min_qty,
        low_stock=item.is_low_stock(),
        reservations=[
            ReservationDto(
                id=r.id,
                order_id=r.order_id,
                qty=r.reserved_qty.amount,
            )
            for r in item.reservations
        ],
    )

# buat di M4 aja biar langsung ke tampilan swagger
@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

# ================ ADMIN / STAF GUDANG =================

@app.post("/admin/items", response_model=InventoryItemDto)
def create_item(payload: CreateItemRequest):
    try:
        item = service.create_item(
            sku=payload.sku,
            initial_qty=payload.initial_qty,
            uom=payload.uom,
            min_qty=payload.min_qty,
        )
        return to_item_dto(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/admin/items", response_model=List[InventoryItemDto])
def list_items():
    items = service.list_items()
    return [to_item_dto(i) for i in items]


@app.get("/admin/items/{sku}", response_model=InventoryItemDto)
def get_item(sku: str):
    try:
        item = service.get_item(sku)
        return to_item_dto(item)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/admin/items/{sku}/threshold", response_model=InventoryItemDto)
def set_threshold(sku: str, payload: SetThresholdRequest):
    try:
        item = service.set_threshold(sku, payload.min_qty)
        return to_item_dto(item)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/admin/items/{sku}/adjust", response_model=InventoryItemDto)
def adjust_stock(sku: str, payload: AdjustStockRequest):
    try:
        item = service.adjust_stock(sku, payload.delta, payload.reason)
        return to_item_dto(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ================ OHS: ORDER / INBOUND / OUTBOUND =================

@app.get("/ohs/availability/{sku}", response_model=InventoryStats)
def get_availability(sku: str):
    try:
        stats = service.get_availability(sku)
        return InventoryStats(**stats)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/ohs/{sku}/reserve", response_model=InventoryItemDto)
def reserve_stock(sku: str, payload: ReserveStockRequest):
    try:
        item, _res = service.reserve_stock(sku, payload.order_id, payload.qty)
        return to_item_dto(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/ohs/{sku}/release", response_model=InventoryItemDto)
def release_reservation(sku: str, payload: ReleaseReservationRequest):
    try:
        item = service.release_reservation(sku, payload.reservation_id)
        return to_item_dto(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/ohs/{sku}/increase", response_model=InventoryItemDto)
def increase_stock(sku: str, payload: IncreaseStockRequest):
    try:
        item = service.increase_stock(sku, payload.qty, payload.reason)
        return to_item_dto(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/ohs/{sku}/decrease", response_model=InventoryItemDto)
def decrease_stock(sku: str, payload: DecreaseStockRequest):
    try:
        item = service.decrease_stock(sku, payload.qty, payload.reason)
        return to_item_dto(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ================ MANAGER VIEW =================

@app.get("/manager/low-stock", response_model=List[InventoryItemDto])
def get_low_stock():
    items = service.get_low_stock_items()
    return [to_item_dto(i) for i in items]
