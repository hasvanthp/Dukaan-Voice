from functools import lru_cache
from uuid import UUID

from fastapi import HTTPException

from app.core.config import Settings, get_settings
from app.repositories.memory import InMemoryRepository


@lru_cache
def get_repo() -> InMemoryRepository:
    return InMemoryRepository()


def get_settings_dep() -> Settings:
    return get_settings()


def get_user_context() -> tuple[UUID, UUID]:
    raise HTTPException(
        status_code=401,
        detail="Authentication is not configured",
        headers={"WWW-Authenticate": "Bearer"},
    )
