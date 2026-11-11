import uuid

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_user_context
from app.main import app
from app.repositories.memory import InMemoryRepository

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


def test_record_sale_rejects_product_from_another_store_without_mutation() -> None:
    repo = InMemoryRepository()
    store_id = uuid.uuid4()
    other_store_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    product = repo.upsert_product(
        other_store_id,
        {
            "name": "rice",
            "purchase_price": "40.00",
            "selling_price": "50.00",
            "unit": "kg",
            "stock_qty": "10",
        },
    )

    with pytest.raises(ValueError, match="product not found for this store"):
        repo.record_sale(
            store_id=store_id,
            actor_id=actor_id,
            items=[{"product_id": product.id, "quantity": "2", "unit_price": "50.00"}],
            customer_id=None,
            paid_amount=100,
        )

    assert product.stock_qty == 10
    assert repo.sales == []
    assert repo.inventory_movements == []


def test_identity_headers_do_not_authenticate_requests(client: TestClient, headers: dict[str, str]) -> None:
    app.dependency_overrides.pop(get_user_context)

    response = client.get("/api/v1/inventory/", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication is not configured"
