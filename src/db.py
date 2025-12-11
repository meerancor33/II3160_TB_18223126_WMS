from typing import Generator, Optional, List, Dict
import os

from sqlalchemy import Column, String, Integer, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from src.domain.inventory import InventoryItem, SKU, Quantity, Threshold, Reservation

# DATABASE_URL = "sqlite:////data/app.db"

# ==========================
# Path Database (Windows + Docker friendly)
# ==========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src/
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)  # pastikan folder ada

DB_FILE = os.path.join(DATA_DIR, "app.db")
DATABASE_URL = f"sqlite:///{DB_FILE}"

# ==========================
# Engine & Session
# ==========================
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


# ==========================
# User Table
# ==========================
class UserModel(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True)
    full_name = Column(String)
    role = Column(String)
    disabled = Column(Boolean, default=False)
    hashed_password = Column(String)


# ==========================
# Inventory Item Table
# ==========================
class InventoryItemModel(Base):
    __tablename__ = "inventory_items"

    id = Column(String, primary_key=True)
    sku = Column(String, unique=True, index=True)
    on_hand = Column(Integer, nullable=False)
    reserved = Column(Integer, nullable=False)
    uom = Column(String, nullable=False)
    min_qty = Column(Integer, nullable=False)


# ==========================
# Reservation Table
# ==========================
class ReservationModel(Base):
    __tablename__ = "reservations"

    id = Column(String, primary_key=True)
    order_id = Column(String, nullable=False)
    sku = Column(String, index=True, nullable=False)  
    qty = Column(Integer, nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================
# MAPPING DB <-> DOMAIN
# ==========================

def inventory_model_to_domain(
    m: InventoryItemModel,
    reservation_models: List[ReservationModel],
) -> InventoryItem:
    """
    Bangun InventoryItem domain lengkap dari:
    - baris inventory_items
    - daftar reservation untuk SKU terkait
    """
    item = InventoryItem(
        id=m.id,
        sku=SKU(m.sku),
        on_hand=Quantity(m.on_hand, m.uom),
        reserved=Quantity(m.reserved, m.uom),
        threshold=Threshold(m.min_qty),
        batch=None,
    )

    # rebuild reservations di domain
    for r in reservation_models:
        item.reservations.append(
            Reservation(
                id=r.id,
                order_id=r.order_id,
                reserved_qty=Quantity(r.qty, m.uom),
            )
        )

    return item


def domain_to_model(item: InventoryItem, existing: Optional[InventoryItemModel] = None) -> InventoryItemModel:
    """
    Mapping InventoryItem domain -> InventoryItemModel DB.
    """
    m = existing or InventoryItemModel(id=item.id)
    m.sku = item.sku.value
    m.on_hand = item.on_hand.amount
    m.reserved = item.reserved.amount
    m.uom = item.on_hand.uom
    m.min_qty = item.threshold.min_qty
    return m


# ==========================
# REPOSITORY DB
# ==========================

class InventoryRepositoryDB:
    def __init__(self):
        self.session_factory = SessionLocal

    def list_all(self) -> List[InventoryItem]:
        """
        Ambil semua item + reservations-nya dari DB.
        """
        with self.session_factory() as db:
            item_models: List[InventoryItemModel] = db.query(InventoryItemModel).all()
            if not item_models:
                return []

            skus = [m.sku for m in item_models]

            res_models: List[ReservationModel] = (
                db.query(ReservationModel)
                .filter(ReservationModel.sku.in_(skus))
                .all()
            )

            # group reservation per sku
            res_by_sku: Dict[str, List[ReservationModel]] = {}
            for r in res_models:
                res_by_sku.setdefault(r.sku, []).append(r)

            items: List[InventoryItem] = []
            for m in item_models:
                reservations = res_by_sku.get(m.sku, [])
                items.append(inventory_model_to_domain(m, reservations))

            return items

    def get_by_sku(self, sku: str) -> Optional[InventoryItem]:
        """
        Ambil single item + reservations berdasarkan SKU.
        """
        with self.session_factory() as db:
            m = db.query(InventoryItemModel).filter(InventoryItemModel.sku == sku).first()
            if not m:
                return None

            res_models = (
                db.query(ReservationModel)
                .filter(ReservationModel.sku == sku)
                .all()
            )
            return inventory_model_to_domain(m, res_models)

    def get_by_id(self, item_id: str) -> Optional[InventoryItem]:
        with self.session_factory() as db:
            m = db.query(InventoryItemModel).filter(InventoryItemModel.id == item_id).first()
            if not m:
                return None

            res_models = (
                db.query(ReservationModel)
                .filter(ReservationModel.sku == m.sku)
                .all()
            )
            return inventory_model_to_domain(m, res_models)

    def save(self, item: InventoryItem) -> InventoryItem:
        """
        Simpan item + sinkronisasi semua reservations ke DB:
        - inventory_items: insert/update
        - reservations: delete semua by sku, lalu insert ulang sesuai item.reservations
        """
        with self.session_factory() as db:
            existing = db.query(InventoryItemModel).filter(InventoryItemModel.id == item.id).first()
            model = domain_to_model(item, existing)
            if not existing:
                db.add(model)

            # hapus semua reservation lama untuk SKU ini
            db.query(ReservationModel).filter(ReservationModel.sku == model.sku).delete()

            # tulis ulang reservation sesuai state domain
            for r in item.reservations:
                db.add(
                    ReservationModel(
                        id=r.id,
                        order_id=r.order_id,
                        sku=model.sku,
                        qty=r.reserved_qty.amount,
                    )
                )

            db.commit()

            # ambil ulang reservations untuk object domain hasil simpan
            res_models = (
                db.query(ReservationModel)
                .filter(ReservationModel.sku == model.sku)
                .all()
            )

            return inventory_model_to_domain(model, res_models)
