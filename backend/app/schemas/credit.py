from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, condecimal


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    phone: str | None = Field(default=None, max_length=30)


class PaymentRecordRequest(BaseModel):
    customer_id: UUID
    amount: condecimal(gt=0, decimal_places=2)
    mode: str = Field(default="cash", max_length=40)
    note: str | None = Field(default=None, max_length=200)
    idempotency_key: str = Field(min_length=8, max_length=120)
    confirmed: bool = False


class CustomerCreditSummary(BaseModel):
    customer_id: UUID
    customer_name: str
    outstanding_balance: float
    last_payment_at: datetime | None = None
