from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, condecimal


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sku: str | None = Field(default=None, max_length=80)
    purchase_price: condecimal(ge=0, decimal_places=2)
    selling_price: condecimal(ge=0, decimal_places=2)
    unit: str = Field(default="kg", max_length=20)
    stock_qty: condecimal(ge=0, decimal_places=3)


class InventoryUpdateRequest(BaseModel):
    product_id: UUID | None = None
    product: ProductCreate | None = None
    quantity_delta: condecimal(gt=0, decimal_places=3)
    reason: str = Field(default="manual_update", max_length=120)
    idempotency_key: str = Field(min_length=8, max_length=120)
    confirmed: bool = False


class ProductRead(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    store_id: UUID
    name: str
    sku: str | None
    purchase_price: float
    selling_price: float
    unit: str
    stock_qty: float
    created_at: datetime
    updated_at: datetime
