# WMS Inventory Control - M4

API ini merupakan implementasi **Milestone 4** dari Tugas Besar II3160 WMS.  

Fokus utama milestone ini adalah:
- Menerapkan **Aggregate `InventoryItem`** sesuai model Domain-Driven Design (DDD).
- Menyediakan **API Inventory Control** berbasis FastAPI untuk:
  - Admin / Staf Gudang
  - Order / Outbound / Inbound (melalui Open Host Service / OHS)
  - Manajer (monitoring stok & low stock)
---
## Stack Teknologi
- **Python ≥ 3.10**
- **FastAPI**
- **Uvicorn** (ASGI server)
- **Pydantic** (Request/Response Schema)

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
   
   Pada M4 ini saya rancang ketika user mengakses 'http://127.0.0.1:8000' akan langsung redirect ke dokumentasi API dengan Swagger UI.
   ```
---
## Dokumentasi & Pengujian API
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
main/
├─ docs/
│  └─ ...                        # Dokumen setiap milestone
│
├─ src/
│  ├─ __init__.py
│  ├─ main.py                    # Entry point FastAPI
│  ├─ domain/
│  │   ├─ __init__.py
│  │   └─ inventory.py           # Aggregate, Value Object, Entity (DDD)
│  ├─ services/
│  │   ├─ __init__.py
│  │   └─ inventory_service.py   # Application Layer / Use Cases
│  └─ schemas/
│      ├─ __init__.py
│      └─ inventory.py           # Pydantic Models (DTO)
│
├─ tests/                        # Unit test
│  └─ ...
│
└─ requirements.txt              # Dependency proyek