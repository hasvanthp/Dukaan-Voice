import uuid

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_repo, get_user_context
from app.main import app
from app.repositories.memory import InMemoryRepository


@pytest.fixture()
def headers() -> dict[str, str]:
    return {
        "x-user-id": str(uuid.uuid4()),
        "x-store-id": str(uuid.uuid4()),
    }


@pytest.fixture()
def client() -> TestClient:
    repo = InMemoryRepository()
    user_id = uuid.uuid4()
    store_id = uuid.uuid4()

    def _repo_override() -> InMemoryRepository:
        return repo

    def _user_context_override() -> tuple[uuid.UUID, uuid.UUID]:
        return user_id, store_id

    app.dependency_overrides[get_repo] = _repo_override
    app.dependency_overrides[get_user_context] = _user_context_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
