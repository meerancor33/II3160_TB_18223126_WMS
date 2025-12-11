from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

import logging

from src.auth import (
    Token,
    authenticate_user,
    create_access_token,
    require_role,
    get_current_user,
    logout_token,
    hash_password,
    oauth2_scheme,
)
from src.db import (
    init_db,
    get_db,
    UserModel,
    InventoryRepositoryDB,
)
from src.services.inventory_service import InventoryService
from src.schemas.inventory import (
    CreateItemRequest,
    IncreaseStockRequest,
    DecreaseStockRequest,
    AdjustStockRequest,
    SetThresholdRequest,
    ReserveStockRequest,
    ReleaseReservationRequest,
    InventoryItemDto,
    InventoryStats,
    ReservationDto,
)
from pydantic import BaseModel


# =============================================================
# STARTUP
# =============================================================

app = FastAPI(title="Inventory Control API with JWT Auth")
init_db()

repo = InventoryRepositoryDB()
service = InventoryService(repo)

@app.on_event("startup")
async def startup_event():
    logging.warning(
        "\n=============================================\n"
        "FastAPI server is running inside Docker\n"
        "Open: http://localhost:8000/docs\n"
        "Note: http://0.0.0.0:8000 TIDAK bisa dibuka dari browser\n"
        "=============================================\n"
    )

# =============================================================
# HELPERS
# =============================================================

class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str | None = None
    role: str  # admin / client / manager


class UserDto(BaseModel):
    username: str
    full_name: str | None
    role: str
    disabled: bool


# Convert domain → DTO
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
                reserved_qty=r.reserved_qty.amount
            )
            for r in item.reservations
        ],
    )


# =============================================================
# ROOT → REDIRECT TO SWAGGER
# =============================================================

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health_check():
    return {"status": "ok"}


# =============================================================
# AUTH: REGISTER
# =============================================================

@app.post("/auth/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):

    if payload.role not in {"admin", "manager", "client"}:
        raise HTTPException(status_code=400, detail="Role must be admin/manager/client")

    exists = db.query(UserModel).filter(UserModel.username == payload.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="Username already registered")

    user = UserModel(
        username=payload.username,
        full_name=payload.full_name,
        role=payload.role,
        disabled=False,
        hashed_password=hash_password(payload.password)
    )

    db.add(user)
    db.commit()
    return {"message": "User registered successfully."}


# =============================================================
# AUTH: LOGIN
# =============================================================

@app.post("/auth/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


# =============================================================
# AUTH: LOGOUT
# =============================================================

@app.post("/auth/logout")
def logout(token: str = Depends(oauth2_scheme)):
    logout_token(token)
    return {"message": "Logout successful. Token blacklisted."}


# =============================================================
# LIST USERS (ADMIN ONLY)
# =============================================================

@app.get("/admin/users", response_model=List[UserDto])
def list_users(
    _user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    users = db.query(UserModel).all()
    return [
        UserDto(
            username=u.username,
            full_name=u.full_name,
            role=u.role,
            disabled=u.disabled,
        )
        for u in users
    ]


# =============================================================
# ADMIN ENDPOINTS
# =============================================================

@app.post("/admin/items", response_model=InventoryItemDto)
def create_item(
    payload: CreateItemRequest,
    _admin=Depends(require_role("admin"))
):
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
def list_items(_admin=Depends(require_role("admin"))):
    return [to_item_dto(i) for i in service.list_items()]


@app.get("/admin/items/{sku}", response_model=InventoryItemDto)
def get_item(sku: str, _admin=Depends(require_role("admin"))):
    try:
        return to_item_dto(service.get_item(sku))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/admin/items/{sku}/threshold", response_model=InventoryItemDto)
def set_threshold(
    sku: str,
    payload: SetThresholdRequest,
    _admin=Depends(require_role("admin")),
):
    try:
        item = service.set_threshold(sku, payload.min_qty)
        return to_item_dto(item)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/admin/items/{sku}/adjust", response_model=InventoryItemDto)
def adjust_stock(
    sku: str,
    payload: AdjustStockRequest,
    _admin=Depends(require_role("admin")),
):
    try:
        item = service.adjust_stock(sku, payload.delta, payload.reason)
        return to_item_dto(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================
# CLIENT / OHS ENDPOINTS
# =============================================================

@app.get("/ohs/availability/{sku}", response_model=InventoryStats)
def availability(
    sku: str,
    _client=Depends(require_role("client")),
):
    try:
        stats = service.get_availability(sku)
        return InventoryStats(**stats)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/ohs/{sku}/increase", response_model=InventoryItemDto)
def increase_stock(
    sku: str,
    payload: IncreaseStockRequest,
    _client=Depends(require_role("client")),
):
    try:
        item = service.increase_stock(sku, payload.qty, payload.reason)
        return to_item_dto(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/ohs/{sku}/decrease", response_model=InventoryItemDto)
def decrease_stock(
    sku: str,
    payload: DecreaseStockRequest,
    _client=Depends(require_role("client")),
):
    try:
        item = service.decrease_stock(sku, payload.qty, payload.reason)
        return to_item_dto(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/ohs/{sku}/reserve", response_model=InventoryItemDto)
def reserve(
    sku: str,
    payload: ReserveStockRequest,
    _client=Depends(require_role("client"))
):
    try:
        item, _res = service.reserve_stock(sku, payload.order_id, payload.qty)
        return to_item_dto(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/ohs/{sku}/release", response_model=InventoryItemDto)
def release_reservation(
    sku: str,
    payload: ReleaseReservationRequest,
    _client=Depends(require_role("client")),
):
    try:
        item = service.release_reservation(sku, payload.reservation_id)
        return to_item_dto(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/ohs/{sku}/reservations", response_model=List[ReservationDto])
def list_reservations(
    sku: str,
    _client=Depends(require_role("client")),
):
    try:
        item = service.get_item(sku)
        return [
            ReservationDto(
                id=r.id,
                order_id=r.order_id,
                reserved_qty=r.reserved_qty.amount,
            )
            for r in item.reservations
        ]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# =============================================================
# MANAGER ENDPOINTS
# =============================================================

@app.get("/manager/low-stock", response_model=List[InventoryItemDto])
def low_stock(_manager=Depends(require_role("manager"))):
    return [to_item_dto(i) for i in service.get_low_stock_items()]
