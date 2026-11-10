from functools import lru_cache
from uuid import UUID

from fastapi import Header, HTTPException

from app.core.config import Settings, get_settings
from app.repositories.memory import InMemoryRepository


@lru_cache
def get_repo() -> InMemoryRepository:
    return InMemoryRepository()


def get_settings_dep() -> Settings:
    return get_settings()


def get_user_context(
    x_user_id: str = Header(...),
    x_store_id: str = Header(...),
) -> tuple[UUID, UUID]:
    try:
        return UUID(x_user_id), UUID(x_store_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid auth context headers") from exc
