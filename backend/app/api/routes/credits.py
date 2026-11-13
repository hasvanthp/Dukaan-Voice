from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_repo, get_user_context
from app.repositories.memory import InMemoryRepository
from app.schemas.credit import CustomerCreate, PaymentRecordRequest
from app.services.credit import CreditService

router = APIRouter(prefix="/credits", tags=["credits"])


@router.post("/customers")
def create_customer(
    payload: CustomerCreate,
    context=Depends(get_user_context),
    repo: InMemoryRepository = Depends(get_repo),
) -> dict:
    _, store_id = context
    service = CreditService(repo)
    return {"success": True, "customer": service.create_customer(store_id, payload.name, payload.phone)}


@router.post("/payments")
def record_payment(
    payload: PaymentRecordRequest,
    context=Depends(get_user_context),
    repo: InMemoryRepository = Depends(get_repo),
) -> dict:
    user_id, store_id = context
    if not payload.confirmed:
        raise HTTPException(status_code=409, detail="Confirmation required for payment recording")
    service = CreditService(repo)
    try:
        payment = service.record_payment(store_id, user_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"success": True, "payment": payment}


@router.get("/customers/{customer_id}")
def check_customer_credit(
    customer_id: UUID,
    context=Depends(get_user_context),
    repo: InMemoryRepository = Depends(get_repo),
) -> dict:
    _, store_id = context
    service = CreditService(repo)
    try:
        summary = service.customer_credit(store_id, customer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"success": True, "credit": summary}
