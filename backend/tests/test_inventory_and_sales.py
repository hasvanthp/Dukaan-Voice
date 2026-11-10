from fastapi.testclient import TestClient


def test_inventory_confirmation_required(client: TestClient, headers: dict[str, str]) -> None:
    payload = {
        "product": {
            "name": "rice",
            "purchase_price": "40.00",
            "selling_price": "50.00",
            "unit": "kg",
            "stock_qty": "10",
        },
        "quantity_delta": "5",
        "reason": "initial_stock",
        "idempotency_key": "inv-unique-1",
        "confirmed": False,
    }
    response = client.post("/api/v1/inventory/add", json=payload, headers=headers)
    assert response.status_code == 409


def test_inventory_add_and_duplicate_guard(client: TestClient, headers: dict[str, str]) -> None:
    payload = {
        "product": {
            "name": "rice",
            "purchase_price": "40.00",
            "selling_price": "50.00",
            "unit": "kg",
            "stock_qty": "10",
        },
        "quantity_delta": "5",
        "reason": "initial_stock",
        "idempotency_key": "inv-unique-2",
        "confirmed": True,
    }
    first = client.post("/api/v1/inventory/add", json=payload, headers=headers)
    assert first.status_code == 200

    second = client.post("/api/v1/inventory/add", json=payload, headers=headers)
    assert second.status_code == 400
    assert "duplicate" in second.text.lower()


def test_sales_report_flow(client: TestClient, headers: dict[str, str]) -> None:
    inv = {
        "product": {
            "name": "sugar",
            "purchase_price": "30.00",
            "selling_price": "45.00",
            "unit": "kg",
            "stock_qty": "10",
        },
        "quantity_delta": "10",
        "reason": "initial_stock",
        "idempotency_key": "inv-unique-3",
        "confirmed": True,
    }
    resp = client.post("/api/v1/inventory/add", json=inv, headers=headers)
    product_id = resp.json()["result"]["product_id"]

    sale_payload = {
        "items": [{"product_id": product_id, "quantity": "2", "unit_price": "45.00"}],
        "paid_amount": "90.00",
        "idempotency_key": "sale-unique-1",
        "confirmed": True,
    }
    sale_resp = client.post("/api/v1/sales/", json=sale_payload, headers=headers)
    assert sale_resp.status_code == 200

    report = client.get("/api/v1/sales/report?days=1", headers=headers)
    assert report.status_code == 200
    data = report.json()["report"]
    assert data["total_sales"] == 1
    assert data["total_revenue"] == 90.0
