from datetime import datetime, timedelta
from uuid import UUID

from app.repositories.memory import InMemoryRepository
from app.schemas.sales import SaleCreateRequest, SalesReport


class SalesService:
    def __init__(self, repo: InMemoryRepository) -> None:
        self.repo = repo

    def create_sale(self, store_id: UUID, user_id: UUID, payload: SaleCreateRequest) -> dict:
        if self.repo.seen_idempotency_key(store_id, payload.idempotency_key):
            raise ValueError("duplicate transaction detected")
        sale = self.repo.record_sale(
            store_id=store_id,
            actor_id=user_id,
            items=[i.model_dump() for i in payload.items],
            customer_id=payload.customer_id,
            paid_amount=float(payload.paid_amount),
        )
        self.repo.record_idempotency_key(store_id, payload.idempotency_key)
        self.repo.append_audit(store_id, user_id, "sale.created", sale)
        return sale

    def get_sales_report(self, store_id: UUID, days: int) -> SalesReport:
        summary = self.repo.sales_summary(store_id, days=days)
        now = datetime.utcnow()
        return SalesReport(
            **summary,
            from_date=now - timedelta(days=days),
            to_date=now,
        )
