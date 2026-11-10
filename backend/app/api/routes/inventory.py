from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_repo, get_user_context
from app.repositories.memory import InMemoryRepository
from app.schemas.inventory import InventoryUpdateRequest
from app.services.inventory import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/")
def list_inventory(
    context=Depends(get_user_context),
    repo: InMemoryRepository = Depends(get_repo),
) -> dict:
    _, store_id = context
    service = InventoryService(repo)
    return {"items": service.list_inventory(store_id)}


@router.post("/add")
def add_inventory(
    payload: InventoryUpdateRequest,
    context=Depends(get_user_context),
    repo: InMemoryRepository = Depends(get_repo),
) -> dict:
    user_id, store_id = context
    if not payload.confirmed:
        raise HTTPException(status_code=409, detail="Confirmation required for stock changes")
    service = InventoryService(repo)
    try:
        result = service.add_inventory(store_id, user_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"success": True, "result": result}
