from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_create_item_success():
    payload = {
        "sku": "TEST-API-001",
        "initial_qty": 100,
        "uom": "pcs",
        "min_qty": 10,
    }

    resp = client.post("/admin/items", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["sku"] == "TEST-API-001"
    assert data["on_hand"] == 100
    assert data["min_qty"] == 10


def test_get_item_after_create():
    payload = {
        "sku": "TEST-API-002",
        "initial_qty": 50,
        "uom": "pcs",
        "min_qty": 5,
    }
    client.post("/admin/items", json=payload)

    resp = client.get("/admin/items/TEST-API-002")

    assert resp.status_code == 200
    data = resp.json()
    assert data["sku"] == "TEST-API-002"
    assert data["on_hand"] == 50


def test_increase_and_decrease_stock_via_api():
    sku = "TEST-API-003"

    # create item
    client.post(
        "/admin/items",
        json={"sku": sku, "initial_qty": 20, "uom": "pcs", "min_qty": 5},
    )

    # increase stock
    inc_resp = client.post(
        f"/ohs/{sku}/increase",
        json={"qty": 10, "reason": "goods_received"},
    )
    assert inc_resp.status_code == 200
    inc_data = inc_resp.json()
    assert inc_data["on_hand"] == 30

    # decrease stock
    dec_resp = client.post(
        f"/ohs/{sku}/decrease",
        json={"qty": 5, "reason": "order_shipped"},
    )
    assert dec_resp.status_code == 200
    dec_data = dec_resp.json()
    assert dec_data["on_hand"] == 25


def test_availability_endpoint():
    sku = "TEST-API-004"

    # create item
    client.post(
        "/admin/items",
        json={"sku": sku, "initial_qty": 40, "uom": "pcs", "min_qty": 10},
    )

    # reserve sebagian stok
    client.post(
        f"/ohs/{sku}/reserve",
        json={"order_id": "ORD-XYZ", "qty": 5},
    )

    # cek availability
    resp = client.get(f"/ohs/availability/{sku}")
    assert resp.status_code == 200
    data = resp.json()

    assert data["sku"] == sku
    assert data["on_hand"] == 40
    assert data["reserved"] == 5
    assert data["available"] == 35
    assert data["uom"] == "pcs"
