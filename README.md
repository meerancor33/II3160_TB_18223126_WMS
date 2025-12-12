# WMS Inventory Control 

Ini merupakan implementasi dari **Tugas Besar II3160**.  

Fokus utama tugas ini adalah:
- Menerapkan **Aggregate `InventoryItem`** sesuai model Domain-Driven Design (DDD).
- Menyediakan **API Inventory Control** berbasis FastAPI untuk:
  - Admin / Staf Gudang
  - Order / Outbound / Inbound (melalui Open Host Service / OHS)
  - Manajer (monitoring stok & low stock)

---
## Stack Teknologi
- **Python ≥ 3.10**
- **FastAPI** - Modern web framework untuk building APIs
- **Uvicorn** - ASGI server untuk menjalankan FastAPI
- **Pydantic** - Data validation menggunakan Python type hints
- **SQLAlchemy** - ORM untuk database operations
- **SQLite** - Database untuk development
- **JWT (JSON Web Tokens)** - Authentication & Authorization
- **Passlib + Bcrypt** - Password hashing & verification
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Pytest** - Unit testing framework
- **Pytest-Cov** - Code coverage reporting
- **Pytest-Asyncio** - Async test support

---

## Instalasi
1. Clone repository berikut
   ```bash
   https://github.com/meerancor33/II3160_TB_18223126_WMS.git
   ```
2. Buat virtual environment
   ```bash
   python -m venv .venv
   ```
3. Aktifkan virtual environment
   ```bash
   ## PowerShell
   .\.venv\Scripts\Activate

   ## Git Bash / MinGW
   source .venv/Scripts/activate

   ## macOS / Linux
   source .venv/bin/activate
   ```
   Jika berhasil, terminal akan menampilkan prefix:
   ```bash
   (.venv)
   ```
4. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
5. Jalankan aplikasi 
   ```bash
   ## Jalankan server FastAPI:
   uvicorn src.main:app --reload

   ## Jika berjalan sukses, terminal akan menampilkan:
   Uvicorn running on http://127.0.0.1:8000
   Application startup complete.
   
   Kemudian, klik tombol Ctrl + klik tautan 'http://127.0.0.1:8000' untuk mengakses dokumentasi API dengan Swagger UI.
   Pada M4 ini saya rancang ketika user mengakses 'http://127.0.0.1:8000' akan langsung redirect ke dokumentasi API dengan Swagger UI.
   ```
---
## 📝Dokumentasi & Pengujian API
* **Swagger UI (Direkomendasikan)**
    * `http://127.0.0.1:8000/docs`
    * `http://localhost:8000/docs`
    * Untuk melihat dan menguji (POST, GET, DELETE) semua endpoint.

* **ReDoc UI (Alternatif)**
    * `http://127.0.0.1:8000/redoc`
    * `http://localhost:8000/redoc`
    * Tampilan dokumentasi read-only.

---
## 📁 Struktur Proyek

```text
II3160_TB_18223126_WMS/
├─ src/
│  ├─ __init__.py
│  ├─ main.py                    # Entry point FastAPI, routes definition
│  ├─ auth.py                    # JWT authentication & authorization logic
│  ├─ db.py                      # Database configuration & session management
│  ├─ domain/
│  │   ├─ __init__.py
│  │   └─ inventory.py           # Aggregate InventoryItem, Value Objects, Entities (DDD)
│  ├─ services/
│  │   ├─ __init__.py
│  │   └─ inventory_service.py   # Application Layer / Use Cases / Business Logic
│  └─ schemas/
│      ├─ __init__.py
│      └─ inventory.py           # Pydantic DTOs untuk Request/Response
│
├─ tests/                        # Unit tests
│  ├─ __init__.py
│  ├─ conftest.py                # Pytest fixtures & configuration
│  ├─ test_domain_inventory.py   # Domain layer tests
│  ├─ test_inventory_service.py  # Service layer tests
│  └─ tests/
│      └─ __init__.py
│
├─ data/                          # Data storage (SQLite database)
│  └─ app.db
│
├─ doc/                           # Documentation files
│  └─ ...                         # Dokumentasi milestone & design
│
├─ docker-compose.yml             # Docker Compose configuration (app + test services)
├─ Dockerfile                     # Docker image definition
├─ requirements.txt               # Python dependencies
├─ .gitignore                     # Git ignore rules
└─ README.md                      # Dokumentasi proyek
```

### 📄 File Descriptions

| File | Purpose |
|------|---------|
| `src/main.py` | FastAPI aplikasi utama, definisi routes untuk semua endpoints |
| `src/auth.py` | JWT token generation, password hashing, role-based access control |
| `src/db.py` | SQLAlchemy database setup, ORM models (UserModel, InventoryItem), repository pattern |
| `src/domain/inventory.py` | DDD Aggregate: InventoryItem, Value Objects (SKU, Quantity, Threshold) |
| `src/services/inventory_service.py` | Business logic: create_item, reserve_stock, adjust_stock, dll |
| `src/schemas/inventory.py` | Pydantic DTOs: CreateItemRequest, InventoryItemDto, ReservationDto, dll |
| `tests/conftest.py` | Pytest fixtures: database session, test client, sample data |
| `tests/test_domain_inventory.py` | Unit tests untuk domain logic (aggregate behavior) |
| `tests/test_inventory_service.py` | Unit tests untuk service layer (use cases) |
| `docker-compose.yml` | Multi-service setup: app (uvicorn), test (pytest) |
| `Dockerfile` | Python 3.11 image, dependencies install, entrypoint config |
| `requirements.txt` | Python packages: fastapi, sqlalchemy, pytest, docker, dll |

---

## 🐳 Docker Setup

### Prerequisites
- **Docker Desktop** installed and running
  - Download: https://www.docker.com/products/docker-desktop
  - Verifikasi: `docker --version`
  - Verifikasi daemon: `docker run hello-world`

- **Docker Compose** (sudah include di Docker Desktop)
  - Verifikasi: `docker compose --version`
  - Minimal version: 2.0+

- **Git** (untuk clone repository)
  - Download: https://git-scm.com/download/
  - Verifikasi: `git --version`

- **Python ≥ 3.10** (untuk development tanpa Docker)
  - Download: https://www.python.org/downloads/
  - Verifikasi: `python --version`

**Quick Start Verification:**
```bash
# Check Docker
docker --version
docker run hello-world

# Check Docker Compose
docker compose --version

# Check Git
git --version

# Check Python (opsional, hanya jika tidak pakai Docker)
python --version
```

### Menjalankan dengan Docker

1. **Build dan jalankan aplikasi:**
   ```bash
   docker compose up app --build
   ```
   Akses API di: `http://localhost:8000/docs`

2. **Menjalankan tests:**
   ```bash
   docker compose up test --build
   ```

3. **Stop services:**
   ```bash
   docker compose down
   ```

---

## 🧪 Testing

### Unit Tests (Local)
```bash
## Jalankan semua tests
pytest

## Jalankan tests dengan verbose
pytest -v

## Jalankan tests dengan coverage
pytest --cov=src

## Jalankan tests dengan coverage detail (recommended)
pytest -vv --color=yes --cov=src --cov-report=term-missing
```

**Penjelasan flag:**
- `-vv` : Very verbose output (detailed test results)
- `--color=yes` : Colorized output
- `--cov=src` : Code coverage untuk folder `src/`
- `--cov-report=term-missing` : Tampilkan lines yang tidak tercakup tests

---

**Output yang dihasilkan:**

1. **Test Results** - Setiap test case ditampilkan:
   ```
   tests/test_domain_inventory.py::test_create_item PASSED                     [10%]
   tests/test_domain_inventory.py::test_reserve_stock PASSED                   [20%]
   tests/test_inventory_service.py::test_get_item PASSED                       [30%]
   ```

2. **Coverage Report** - Persentase coverage per file:
   ```
   Name                          Stmts   Miss  Cover   Missing
   ─────────────────────────────────────────────────────────────
   src/auth.py                      45      3    93%    25-27
   src/db.py                        62      5    92%    45-48
   src/domain/inventory.py          85      2    98%    120
   src/services/inventory_service.py 120     8    93%    45-50,85
   src/schemas/inventory.py         35      0   100%
   ─────────────────────────────────────────────────────────────
   TOTAL                           347     18    95%
   ```

3. **Missing Lines** - Lines yang belum tercakup tests:
   - `src/auth.py: 25-27` → Lines 25-27 tidak ditest
   - `src/db.py: 45-48` → Lines 45-48 tidak ditest
   - `src/domain/inventory.py: 120` → Line 120 tidak ditest

**Interpretasi Coverage:**
- 🟢 **95%+ Coverage** → Excellent (hampir semua code teruji)
- 🟡 **80-94% Coverage** → Good (cukup teruji)
- 🟠 **70-79% Coverage** → Fair (perlu improvement)
- 🔴 **<70% Coverage** → Poor (banyak code tidak teruji)

**Target Coverage di Project Ini:** 🎯 **>95%**

---

### Cara Membaca Coverage Report

| Kolom | Arti |
|-------|------|
| **Name** | Nama file |
| **Stmts** | Total statements (baris code) |
| **Miss** | Baris yang tidak tercakup |
| **Cover** | Persentase coverage |
| **Missing** | List line numbers yang tidak ditest |

**Contoh:** `src/auth.py: 45 Stmts, 3 Miss, 93% Cover`
- Total 45 baris code
- 3 baris tidak ditest (93% coverage)
- Lines 25-27 belum ditest

---

### Optimasi Coverage

Untuk meningkatkan coverage, tambah tests untuk lines yang missing:

```python
# Jika Missing: src/auth.py 25-27
# Tambah test untuk case tersebut

def test_invalid_token():
    """Test untuk lines 25-27"""
    with pytest.raises(Exception):
        validate_token("invalid_token")
```

Setelah menambah test, run command lagi:
```bash
pytest -vv --color=yes --cov=src --cov-report=term-missing
```

---

### 🎯 Coverage Report Hasil Test

Berikut adalah hasil test coverage dari project ini:

```
---------- coverage: platform win32, python 3.13.5-final-0 ----------
Name                          Stmts   Miss  Cover    Missing
─────────────────────────────────────────────────────────────
src\domain\inventory.py          117      0   100%
src\services\inventory_service.py 47      0   100%
─────────────────────────────────────────────────────────────
TOTAL                            164      0   100%
```

**Status: ✅ 100% Coverage Achieved!**

- ✅ **src/domain/inventory.py** - 117 statements, **100% covered**
- ✅ **src/services/inventory_service.py** - 47 statements, **100% covered**
- ✅ **Total** - 164 statements, **0 missed, 100% coverage**

Semua code teruji dengan sempurna! 🎉

---

### Unit Tests (Docker)
```bash
docker compose up test --build
```

---

## 🔐 Authentication

API ini menggunakan **JWT (JSON Web Tokens)** untuk autentikasi:

1. **Login** - Dapatkan access token
   ```bash
   POST /login
   ```

2. **Gunakan token** - Header request:
   ```
   Authorization: Bearer <your_access_token>
   ```

3. **Endpoint yang memerlukan autentikasi:**
   - Semua endpoint inventory management
   - Reserved untuk role: `admin`, `staff`, `manager`

---

## 📋 API Endpoints

### Authentication
- `POST /login` - Login dan dapatkan JWT token
- `POST /logout` - Logout

### Inventory Management
- `GET /inventory` - Get semua items
- `GET /inventory/{item_id}` - Get item detail
- `POST /inventory` - Create item baru
- `PUT /inventory/{item_id}/stock/increase` - Increase stock
- `PUT /inventory/{item_id}/stock/decrease` - Decrease stock
- `PUT /inventory/{item_id}/threshold` - Set low stock threshold
- `POST /inventory/{item_id}/reserve` - Reserve stock
- `POST /inventory/{item_id}/release` - Release reservation
- `GET /inventory/stats` - Get inventory statistics
- `GET /health` - Health check

---

## 📋 API Overview

Semua endpoints menggunakan JSON format.

### Authentication Endpoints
| Method | Endpoint              | Description              | Role Required |
|--------|-----------------------|--------------------------|---------------|
| POST   | `/auth/register`      | Daftar user baru         | any           |
| POST   | `/auth/login`         | Login dan dapatkan token | any           |
| POST   | `/auth/logout`        | Logout dan blacklist token | authenticated |

### Health & Status
| Method | Endpoint | Description  | Role Required |
|--------|----------|--------------|---------------|
| GET    | `/health`| Health check | any           |

### Admin Endpoints (Inventory Management)
| Method | Endpoint                   | Description           | Role Required |
|--------|----------------------------|-----------------------|---------------|
| POST   | `/admin/items`             | Create item baru      | admin         |
| GET    | `/admin/items`             | List semua items      | admin         |
| GET    | `/admin/items/{sku}`       | Get item by SKU       | admin         |
| POST   | `/admin/items/{sku}/threshold` | Set low stock threshold | admin      |
| POST   | `/admin/items/{sku}/adjust` | Adjust stock manual   | admin         |
| GET    | `/admin/users`        | List all users (admin only) | admin       |

### Client/OHS Endpoints (Stock Operations)
| Method | Endpoint                      | Description              | Role Required |
|--------|-------------------------------|--------------------------|---------------|
| GET    | `/ohs/availability/{sku}`     | Get stock availability  | client        |
| POST   | `/ohs/{sku}/increase`         | Increase stock (inbound)| client        |
| POST   | `/ohs/{sku}/decrease`         | Decrease stock (outbound) | client      |
| POST   | `/ohs/{sku}/reserve`          | Reserve stock for order | client        |
| POST   | `/ohs/{sku}/release`          | Release reservation     | client        |
| GET    | `/ohs/{sku}/reservations`     | List reservations       | client        |

### Manager Endpoints (Monitoring)
| Method | Endpoint              | Description             | Role Required |
|--------|----------------------|-------------------------|---------------|
| GET    | `/manager/low-stock`  | Get items dengan low stock | manager     |


---

## 🔑 Roles & Permissions

| Role     | Permissions                                |
|----------|---------------------------------------------|
| **admin** | Create/Update items, List items, Set threshold, List users |
| **client** | Increase/Decrease stock, Reserve/Release stock, Check availability |
| **manager** | Monitor low stock items |

---

## 📦 Inventory Workflow

Lifecycle inventori item di WMS:

1. **CREATED** → 2. **ACTIVE** → 3. **LOW_STOCK** → 4. **OUT_OF_STOCK** or back to **ACTIVE**

- **CREATED**: Item baru dibuat oleh admin
- **ACTIVE**: Item siap digunakan, stok tersedia
- **LOW_STOCK**: Stok di bawah minimum threshold (notifikasi ke manager)
- **OUT_OF_STOCK**: Stok habis (no transactions allowed)

**Transisi Status:**
- Item dapat di-adjust stock kapan saja oleh admin
- Status bisa berubah otomatis berdasarkan perubahan stok
- Reservasi tidak mengurangi on-hand, hanya mengurangi available
- Released reservasi mengembalikan available stock

**Stock Operations:**
```
On-Hand (Total stok fisik)
  ├─ Reserved (Sudah dipesan, tunggu outbound)
  └─ Available (Bisa digunakan = On-Hand - Reserved)

Decrease: On-Hand ↓ → Available ↓ (jika tidak ada reservation)
Increase: On-Hand ↑ → Available ↑ (atau habiskan reservation terlebih dahulu)
Reserve: Available ↓, Reserved ↑
Release: Available ↑, Reserved ↓
```

---

## 💾 Data Models

### InventoryItem (Aggregate)
```json
{
  "id": "uuid",
  "sku": "SKU-001",
  "on_hand": 100,
  "reserved": 10,
  "available": 90,
  "uom": "pcs",
  "min_qty": 20,
  "low_stock": false,
  "reservations": []
}
```

### Reservation
```json
{
  "id": "uuid",
  "order_id": "ORD-001",
  "reserved_qty": 5
}
```

### InventoryStats
```json
{
  "sku": "SKU-001",
  "on_hand": 100,
  "available": 90,
  "reserved": 10,
  "min_qty": 20,
  "low_stock": false
}
```

---

## 📖 Dokumentasi Endpoint Lengkap

### 1. Authentication Endpoints

#### POST `/auth/register` - Daftar User Baru
**Request Body:**
```json
{
  "username": "john_doe",
  "password": "password123",
  "full_name": "John Doe",
  "role": "client"
}
```
**Valid Roles:** `admin`, `manager`, `client`

**Response (201 Created):**
```json
{
  "message": "User registered successfully."
}
```

---

#### POST `/auth/login` - Login & Dapatkan Token
**Request Body (form-data):**
```
username: john_doe
password: password123
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```
**Usage:** Tambahkan header: `Authorization: Bearer <access_token>`

---

#### POST `/auth/logout` - Logout & Blacklist Token
**Headers:** `Authorization: Bearer <access_token>`

**Response (200 OK):**
```json
{
  "message": "Logout successful. Token blacklisted."
}
```

---

### 2. Health & Status

#### GET `/health` - Health Check
**Response (200 OK):**
```json
{
  "status": "ok",
  "database": "up",
  "timestamp": "2025-12-12T08:30:45.123Z"
}
```

---

### 3. Admin Endpoints

#### POST `/admin/items` - Create Item Baru
**Headers:** `Authorization: Bearer <admin_token>`

**Request Body:**
```json
{
  "sku": "SKU-001",
  "initial_qty": 100,
  "uom": "pcs",
  "min_qty": 20
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "sku": "SKU-001",
  "on_hand": 100,
  "reserved": 0,
  "available": 100,
  "uom": "pcs",
  "min_qty": 20,
  "low_stock": false,
  "reservations": []
}
```

---

#### GET `/admin/items` - List Semua Items
**Headers:** `Authorization: Bearer <admin_token>`

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "sku": "SKU-001",
    "on_hand": 100,
    "reserved": 10,
    "available": 90,
    "uom": "pcs",
    "min_qty": 20,
    "low_stock": false,
    "reservations": []
  }
]
```

---

#### GET `/admin/items/{sku}` - Get Item by SKU
**Headers:** `Authorization: Bearer <admin_token>`

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "sku": "SKU-001",
  "on_hand": 100,
  "reserved": 10,
  "available": 90,
  "uom": "pcs",
  "min_qty": 20,
  "low_stock": false,
  "reservations": [
    {
      "id": "res-001",
      "order_id": "ORD-001",
      "reserved_qty": 10
    }
  ]
}
```

---

#### POST `/admin/items/{sku}/threshold` - Set Low Stock Threshold
**Headers:** `Authorization: Bearer <admin_token>`

**Request Body:**
```json
{
  "min_qty": 25
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "sku": "SKU-001",
  "on_hand": 100,
  "reserved": 0,
  "available": 100,
  "uom": "pcs",
  "min_qty": 25,
  "low_stock": false,
  "reservations": []
}
```

---

#### POST `/admin/items/{sku}/adjust` - Adjust Stock Manual
**Headers:** `Authorization: Bearer <admin_token>`

**Request Body:**
```json
{
  "delta": -5,
  "reason": "STOCKTAKE_CORRECTION"
}
```
**Delta dapat:** positif (add) atau negatif (reduce)

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "sku": "SKU-001",
  "on_hand": 95,
  "reserved": 0,
  "available": 95,
  "uom": "pcs",
  "min_qty": 20,
  "low_stock": false,
  "reservations": []
}
```

---

#### GET `/admin/users` - List All Users (Admin Only)
**Headers:** `Authorization: Bearer <admin_token>`

**Response (200 OK):**
```json
[
  {
    "username": "admin_user",
    "full_name": "Admin User",
    "role": "admin",
    "disabled": false
  },
  {
    "username": "client_user",
    "full_name": "Client User",
    "role": "client",
    "disabled": false
  }
]
```

---

### 4. Client/OHS Endpoints

#### GET `/ohs/availability/{sku}` - Get Stock Availability
**Headers:** `Authorization: Bearer <client_token>`

**Response (200 OK):**
```json
{
  "sku": "SKU-001",
  "on_hand": 100,
  "reserved": 10,
  "available": 90,
  "uom": "pcs",
  "low_stock": false
}
```

---

#### POST `/ohs/{sku}/increase` - Increase Stock (Inbound)
**Headers:** `Authorization: Bearer <client_token>`

**Request Body:**
```json
{
  "qty": 50,
  "reason": "PURCHASE_ORDER_001"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "sku": "SKU-001",
  "on_hand": 150,
  "reserved": 10,
  "available": 140,
  "uom": "pcs",
  "min_qty": 20,
  "low_stock": false,
  "reservations": []
}
```

---

#### POST `/ohs/{sku}/decrease` - Decrease Stock (Outbound)
**Headers:** `Authorization: Bearer <client_token>`

**Request Body:**
```json
{
  "qty": 30,
  "reason": "SALES_ORDER_002"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "sku": "SKU-001",
  "on_hand": 70,
  "reserved": 10,
  "available": 60,
  "uom": "pcs",
  "min_qty": 20,
  "low_stock": false,
  "reservations": []
}
```
**Error (400 Bad Request):** Jika qty > available (insufficient stock)

---

#### POST `/ohs/{sku}/reserve` - Reserve Stock for Order
**Headers:** `Authorization: Bearer <client_token>`

**Request Body:**
```json
{
  "order_id": "ORD-001",
  "qty": 10
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "sku": "SKU-001",
  "on_hand": 100,
  "reserved": 10,
  "available": 90,
  "uom": "pcs",
  "min_qty": 20,
  "low_stock": false,
  "reservations": [
    {
      "id": "res-001",
      "order_id": "ORD-001",
      "reserved_qty": 10
    }
  ]
}
```

---

#### POST `/ohs/{sku}/release` - Release Reservation
**Headers:** `Authorization: Bearer <client_token>`

**Request Body:**
```json
{
  "reservation_id": "res-001"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "sku": "SKU-001",
  "on_hand": 100,
  "reserved": 0,
  "available": 100,
  "uom": "pcs",
  "min_qty": 20,
  "low_stock": false,
  "reservations": []
}
```

---

#### GET `/ohs/{sku}/reservations` - List Reservations for Item
**Headers:** `Authorization: Bearer <client_token>`

**Response (200 OK):**
```json
[
  {
    "id": "res-001",
    "order_id": "ORD-001",
    "reserved_qty": 10
  },
  {
    "id": "res-002",
    "order_id": "ORD-002",
    "reserved_qty": 5
  }
]
```

---

### 5. Manager Endpoints

#### GET `/manager/low-stock` - Get Items dengan Low Stock
**Headers:** `Authorization: Bearer <manager_token>`

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "sku": "SKU-001",
    "on_hand": 15,
    "reserved": 0,
    "available": 15,
    "uom": "pcs",
    "min_qty": 20,
    "low_stock": true,
    "reservations": []
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "sku": "SKU-002",
    "on_hand": 8,
    "reserved": 0,
    "available": 8,
    "uom": "pcs",
    "min_qty": 10,
    "low_stock": true,
    "reservations": []
  }
]
```

---

## 🚨 Error Responses & Exception Handling

Semua error responses menggunakan format JSON dengan `detail` message:

### Common Error Status Codes

| Status Code | Description                           |
|-------------|---------------------------------------|
| 400         | Bad Request (validation error)        |
| 401         | Unauthorized (invalid/missing token)  |
| 403         | Forbidden (insufficient permissions)  |
| 404         | Not Found (resource tidak ada)        |
| 500         | Internal Server Error                 |

---

### Error Response Format

```json
{
  "detail": "Error message explaining what went wrong"
}
```

---

### Common Error Scenarios

#### 1. Authentication Error - Missing Token
**Request:** `GET /admin/items` (tanpa Authorization header)

**Response (401 Unauthorized):**
```json
{
  "detail": "Not authenticated"
}
```

---

#### 2. Authentication Error - Invalid Token
**Request:** `GET /admin/items`
**Headers:** `Authorization: Bearer invalid_token_here`

**Response (401 Unauthorized):**
```json
{
  "detail": "Could not validate credentials"
}
```

---

#### 3. Authorization Error - Insufficient Role
**Request:** `POST /admin/items` (user role: `client`)
**Headers:** `Authorization: Bearer <client_token>`

**Response (403 Forbidden):**
```json
{
  "detail": "Not enough permissions"
}
```

---

#### 4. Validation Error - Missing Required Field
**Request:** `POST /auth/register`
**Request Body:**
```json
{
  "username": "john_doe",
  "password": "password123"
  // Missing "role" field
}
```

**Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "role"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

#### 5. Validation Error - Invalid Role
**Request:** `POST /auth/register`
**Request Body:**
```json
{
  "username": "john_doe",
  "password": "password123",
  "full_name": "John Doe",
  "role": "superuser"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Role must be admin/manager/client"
}
```

---

#### 6. Duplicate User Error
**Request:** `POST /auth/register`
**Request Body:**
```json
{
  "username": "john_doe",
  "password": "password123",
  "full_name": "John Doe",
  "role": "client"
}
```
(username "john_doe" sudah terdaftar)

**Response (400 Bad Request):**
```json
{
  "detail": "Username already registered"
}
```

---

#### 7. Login Error - Wrong Credentials
**Request:** `POST /auth/login`
**Request Body (form-data):**
```
username: john_doe
password: wrong_password
```

**Response (400 Bad Request):**
```json
{
  "detail": "Incorrect username or password"
}
```

---

#### 8. Item Not Found
**Request:** `GET /admin/items/SKU-999` (item tidak ada)

**Response (404 Not Found):**
```json
{
  "detail": "Item not found"
}
```

---

#### 9. Insufficient Stock Error
**Request:** `POST /ohs/SKU-001/decrease`
**Request Body:**
```json
{
  "qty": 150,
  "reason": "SALES_ORDER_001"
}
```
(available stock: 100)

**Response (400 Bad Request):**
```json
{
  "detail": "Insufficient stock. Available: 100, Requested: 150"
}
```

---

#### 10. Invalid Quantity Error
**Request:** `POST /ohs/SKU-001/increase`
**Request Body:**
```json
{
  "qty": -50,
  "reason": "PURCHASE_ORDER"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Quantity must be positive"
}
```

---

#### 11. Reservation Error - Insufficient Stock
**Request:** `POST /ohs/SKU-001/reserve`
**Request Body:**
```json
{
  "order_id": "ORD-001",
  "qty": 200
}
```
(available stock: 100)

**Response (400 Bad Request):**
```json
{
  "detail": "Cannot reserve. Available: 100, Requested: 200"
}
```

---

#### 12. Release Reservation Error - Not Found
**Request:** `POST /ohs/SKU-001/release`
**Request Body:**
```json
{
  "reservation_id": "res-999"
}
```
(reservation tidak ada)

**Response (404 Not Found):**
```json
{
  "detail": "Reservation not found"
}
```

---

#### 13. Low Stock Threshold Error
**Request:** `POST /admin/items/SKU-001/threshold`
**Request Body:**
```json
{
  "min_qty": -5
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Minimum quantity must be >= 0"
}
```

---

## 🚀 CI/CD

**CI (Continuous Integration)** adalah proses otomatis yang:
- Menjalankan unit tests setiap kali ada commit/push
- Mengecek kualitas kode (linting)
- Menghitung code coverage
- Menolak merge jika tests gagal

**CD (Continuous Deployment)** adalah:
- Build Docker image otomatis
- Push ke Docker Registry
- Deploy ke production otomatis

### Cara Kerja Singkat

```
Developer push code
    ↓
Trigger CI Pipeline
    ↓
Run Tests & Linting
    ↓
Build Docker Image (jika tests passed)
    ↓
Deploy ke Production (opsional)
```

Monitor di tab **Actions** di GitHub.

| Status | Simbol | Arti |
|--------|--------|------|
| Berhasil | ✅ | Tests passed, build succeeded |
| Gagal | ❌ | Tests failed, build error |
| Sedang Berjalan | ⏳ | Pipeline in progress |
| Pending | ⏸️ | Waiting for approval/action |
| Cancelled | 🛑 | Pipeline cancelled |

---

## 🏗️ Architecture (DDD)

- **Domain Layer** (`src/domain/`) - Aggregate, Value Objects, Business Logic
- **Application Layer** (`src/services/`) - Use Cases & Service Logic
- **Infrastructure Layer** (`src/db.py`) - Database Access & Persistence
- **Presentation Layer** (`src/main.py`) - API Endpoints
- **Schemas Layer** (`src/schemas/`) - Pydantic DTOs for Request/Response

---
