from uuid import UUID

from app.repositories.memory import InMemoryRepository
from app.schemas.inventory import InventoryUpdateRequest


class InventoryService:
    def __init__(self, repo: InMemoryRepository) -> None:
        self.repo = repo

    def add_inventory(self, store_id: UUID, user_id: UUID, payload: InventoryUpdateRequest) -> dict:
        if self.repo.seen_idempotency_key(store_id, payload.idempotency_key):
            raise ValueError("duplicate transaction detected")

        if payload.product_id is None and payload.product is None:
            raise ValueError("either product_id or product payload is required")

        if payload.product_id is None and payload.product:
            product = self.repo.upsert_product(store_id, payload.product.model_dump())
        else:
            product = self.repo.add_stock(
                store_id,
                payload.product_id,
                float(payload.quantity_delta),
                payload.reason,
                user_id,
            )

        self.repo.record_idempotency_key(store_id, payload.idempotency_key)
        self.repo.append_audit(store_id, user_id, "inventory.updated", payload.model_dump(mode="json"))
        return {"product_id": str(product.id), "stock_qty": product.stock_qty}

    def list_inventory(self, store_id: UUID) -> list[dict]:
        return self.repo.list_products(store_id)
