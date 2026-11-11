from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from app.repositories.base import Customer, Product, Repository


class InMemoryRepository(Repository):
    def __init__(self) -> None:
        self.products: dict[UUID, Product] = {}
        self.customers: dict[UUID, Customer] = {}
        self.sales: list[dict] = []
        self.payments: list[dict] = []
        self.inventory_movements: list[dict] = []
        self.audit_events: list[dict] = []
        self.conversations: dict[str, dict] = {}
        self.idempotency_keys: dict[UUID, set[str]] = defaultdict(set)

    def seen_idempotency_key(self, store_id: UUID, key: str) -> bool:
        return key in self.idempotency_keys[store_id]

    def record_idempotency_key(self, store_id: UUID, key: str) -> None:
        self.idempotency_keys[store_id].add(key)

    def upsert_product(self, store_id: UUID, payload: dict) -> Product:
        now = datetime.utcnow()
        product = Product(
            id=uuid4(),
            store_id=store_id,
            name=payload["name"],
            sku=payload.get("sku"),
            purchase_price=float(payload["purchase_price"]),
            selling_price=float(payload["selling_price"]),
            unit=payload["unit"],
            stock_qty=float(payload["stock_qty"]),
            created_at=now,
            updated_at=now,
        )
        self.products[product.id] = product
        return product

    def add_stock(self, store_id: UUID, product_id: UUID, delta: float, reason: str, actor_id: UUID) -> Product:
        product = self.products[product_id]
        if product.store_id != store_id:
            raise ValueError("product not found for this store")
        product.stock_qty += delta
        product.updated_at = datetime.utcnow()
        self.inventory_movements.append(
            {
                "id": uuid4(),
                "store_id": str(store_id),
                "product_id": str(product_id),
                "change_qty": delta,
                "reason": reason,
                "created_by": str(actor_id),
                "created_at": datetime.utcnow().isoformat(),
            }
        )
        return product

    def list_products(self, store_id: UUID) -> list[dict]:
        return [asdict(p) for p in self.products.values() if p.store_id == store_id]

    def create_customer(self, store_id: UUID, name: str, phone: str | None = None) -> Customer:
        now = datetime.utcnow()
        customer = Customer(
            id=uuid4(),
            store_id=store_id,
            name=name,
            phone=phone,
            outstanding_balance=0,
            created_at=now,
            updated_at=now,
        )
        self.customers[customer.id] = customer
        return customer

    def get_customer(self, store_id: UUID, customer_id: UUID) -> Customer:
        customer = self.customers[customer_id]
        if customer.store_id != store_id:
            raise ValueError("customer not found")
        return customer

    def record_sale(self, store_id: UUID, actor_id: UUID, items: list[dict], customer_id: UUID | None, paid_amount: float) -> dict:
        total_revenue = 0.0
        total_cost = 0.0
        validated_items: list[tuple[Product, float, dict]] = []
        for item in items:
            product = self.products[item["product_id"]]
            qty = float(item["quantity"])
            if product.store_id != store_id:
                raise ValueError("product not found for this store")
            if product.stock_qty < qty:
                raise ValueError(f"insufficient stock for {product.name}")

            validated_items.append((product, qty, item))
            total_revenue += qty * float(item["unit_price"])
            total_cost += qty * product.purchase_price

        customer = self.get_customer(store_id, customer_id) if customer_id else None
        for product, qty, item in validated_items:
            product.stock_qty -= qty
            product.updated_at = datetime.utcnow()
            self.inventory_movements.append(
                {
                    "id": uuid4(),
                    "store_id": str(store_id),
                    "product_id": str(product.id),
                    "change_qty": -qty,
                    "reason": "sale",
                    "created_by": str(actor_id),
                    "created_at": datetime.utcnow().isoformat(),
                }
            )

        sale = {
            "id": str(uuid4()),
            "store_id": str(store_id),
            "customer_id": str(customer_id) if customer_id else None,
            "total_amount": round(total_revenue, 2),
            "total_profit": round(total_revenue - total_cost, 2),
            "paid_amount": round(paid_amount, 2),
            "created_by": str(actor_id),
            "created_at": datetime.utcnow().isoformat(),
            "items": [
                {
                    "product_id": str(i["product_id"]),
                    "quantity": float(i["quantity"]),
                    "unit_price": float(i["unit_price"]),
                }
                for i in items
            ],
        }
        self.sales.append(sale)

        if customer:
            credit_delta = total_revenue - paid_amount
            customer.outstanding_balance += credit_delta
            customer.updated_at = datetime.utcnow()

        return sale

    def sales_summary(self, store_id: UUID, days: int = 1) -> dict:
        cutoff = datetime.utcnow() - timedelta(days=days)
        scoped = [s for s in self.sales if s["store_id"] == str(store_id) and datetime.fromisoformat(s["created_at"]) >= cutoff]
        return {
            "total_revenue": round(sum(s["total_amount"] for s in scoped), 2),
            "total_profit": round(sum(s["total_profit"] for s in scoped), 2),
            "total_sales": len(scoped),
        }

    def record_payment(self, store_id: UUID, actor_id: UUID, customer_id: UUID, amount: float, mode: str, note: str | None) -> dict:
        customer = self.get_customer(store_id, customer_id)
        customer.outstanding_balance = round(max(0.0, customer.outstanding_balance - amount), 2)
        customer.updated_at = datetime.utcnow()
        payment = {
            "id": str(uuid4()),
            "store_id": str(store_id),
            "customer_id": str(customer_id),
            "amount": round(amount, 2),
            "mode": mode,
            "note": note,
            "created_by": str(actor_id),
            "created_at": datetime.utcnow().isoformat(),
        }
        self.payments.append(payment)
        return payment

    def customer_credit(self, store_id: UUID, customer_id: UUID) -> dict:
        customer = self.get_customer(store_id, customer_id)
        payments = [p for p in self.payments if p["store_id"] == str(store_id) and p["customer_id"] == str(customer_id)]
        last_payment_at = payments[-1]["created_at"] if payments else None
        return {
            "customer_id": str(customer.id),
            "customer_name": customer.name,
            "outstanding_balance": customer.outstanding_balance,
            "last_payment_at": last_payment_at,
        }

    def append_audit(self, store_id: UUID, actor_id: UUID, event_type: str, payload: dict) -> None:
        self.audit_events.append(
            {
                "id": str(uuid4()),
                "store_id": str(store_id),
                "actor_id": str(actor_id),
                "event_type": event_type,
                "payload": payload,
                "created_at": datetime.utcnow().isoformat(),
            }
        )

    def save_conversation_state(self, conversation_id: str, state: dict) -> None:
        self.conversations[conversation_id] = state

    def get_conversation_state(self, conversation_id: str) -> dict | None:
        return self.conversations.get(conversation_id)
