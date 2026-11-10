import uuid

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_repo
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

    def _repo_override() -> InMemoryRepository:
        return repo

    app.dependency_overrides[get_repo] = _repo_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
