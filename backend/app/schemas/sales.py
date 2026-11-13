from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, condecimal


class SaleItemIn(BaseModel):
    product_id: UUID
    quantity: condecimal(gt=0, decimal_places=3)
    unit_price: condecimal(gt=0, decimal_places=2)


class SaleCreateRequest(BaseModel):
    customer_id: UUID | None = None
    items: list[SaleItemIn] = Field(min_length=1)
    paid_amount: condecimal(ge=0, decimal_places=2) = 0
    idempotency_key: str = Field(min_length=8, max_length=120)
    confirmed: bool = False


class SalesReport(BaseModel):
    total_revenue: float
    total_profit: float
    total_sales: int
    from_date: datetime
    to_date: datetime
