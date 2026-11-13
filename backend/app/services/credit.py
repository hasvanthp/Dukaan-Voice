from uuid import UUID

from app.repositories.memory import InMemoryRepository
from app.schemas.credit import PaymentRecordRequest


class CreditService:
    def __init__(self, repo: InMemoryRepository) -> None:
        self.repo = repo

    def create_customer(self, store_id: UUID, name: str, phone: str | None) -> dict:
        customer = self.repo.create_customer(store_id, name=name, phone=phone)
        return {
            "customer_id": str(customer.id),
            "name": customer.name,
            "phone": customer.phone,
            "outstanding_balance": customer.outstanding_balance,
        }

    def record_payment(self, store_id: UUID, user_id: UUID, payload: PaymentRecordRequest) -> dict:
        if self.repo.seen_idempotency_key(store_id, payload.idempotency_key):
            raise ValueError("duplicate transaction detected")
        payment = self.repo.record_payment(
            store_id=store_id,
            actor_id=user_id,
            customer_id=payload.customer_id,
            amount=float(payload.amount),
            mode=payload.mode,
            note=payload.note,
        )
        self.repo.record_idempotency_key(store_id, payload.idempotency_key)
        self.repo.append_audit(store_id, user_id, "payment.recorded", payment)
        return payment

    def customer_credit(self, store_id: UUID, customer_id: UUID) -> dict:
        return self.repo.customer_credit(store_id, customer_id)
