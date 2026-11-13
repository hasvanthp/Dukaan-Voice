from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_repo, get_user_context
from app.repositories.memory import InMemoryRepository
from app.schemas.sales import SaleCreateRequest
from app.services.sales import SalesService

router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("/")
def create_sale(
    payload: SaleCreateRequest,
    context=Depends(get_user_context),
    repo: InMemoryRepository = Depends(get_repo),
) -> dict:
    user_id, store_id = context
    if not payload.confirmed:
        raise HTTPException(status_code=409, detail="Confirmation required for sale recording")
    service = SalesService(repo)
    try:
        sale = service.create_sale(store_id, user_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"success": True, "sale": sale}


@router.get("/report")
def sales_report(
    days: int = Query(default=1, ge=1, le=365),
    context=Depends(get_user_context),
    repo: InMemoryRepository = Depends(get_repo),
) -> dict:
    _, store_id = context
    service = SalesService(repo)
    report = service.get_sales_report(store_id, days=days)
    return {"success": True, "report": report.model_dump(mode="json")}
