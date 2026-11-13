from fastapi import APIRouter, Depends

from app.api.deps import get_repo, get_settings_dep, get_user_context
from app.core.config import Settings
from app.repositories.memory import InMemoryRepository
from app.schemas.conversation import VoiceCommandRequest, VoiceCommandResponse
from app.services.orchestrator import ConversationOrchestrator

router = APIRouter(prefix="/conversation", tags=["conversation"])


@router.post("/voice-command", response_model=VoiceCommandResponse)
def process_voice_command(
    payload: VoiceCommandRequest,
    context=Depends(get_user_context),
    repo: InMemoryRepository = Depends(get_repo),
    settings: Settings = Depends(get_settings_dep),
) -> VoiceCommandResponse:
    user_id, store_id = context
    orchestrator = ConversationOrchestrator(repo=repo, settings=settings)
    result = orchestrator.process(
        user_id=user_id,
        store_id=store_id,
        text=payload.text,
        conversation_id=payload.conversation_id,
        confirmed=payload.confirmed,
    )
    return VoiceCommandResponse(**result)
