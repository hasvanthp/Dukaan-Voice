from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Product:
    id: UUID
    store_id: UUID
    name: str
    sku: str | None
    purchase_price: float
    selling_price: float
    unit: str
    stock_qty: float
    created_at: datetime
    updated_at: datetime


@dataclass
class Customer:
    id: UUID
    store_id: UUID
    name: str
    phone: str | None
    outstanding_balance: float
    created_at: datetime
    updated_at: datetime


class Repository(ABC):
    @abstractmethod
    def seen_idempotency_key(self, store_id: UUID, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def record_idempotency_key(self, store_id: UUID, key: str) -> None:
        raise NotImplementedError
