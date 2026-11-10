from pydantic import BaseModel, Field


class VoiceCommandRequest(BaseModel):
    text: str = Field(min_length=2, max_length=500)
    conversation_id: str | None = Field(default=None, max_length=120)
    confirmed: bool = False


class VoiceCommandResponse(BaseModel):
    intent: str
    confidence: float
    requires_confirmation: bool
    message: str
    preview_action: dict | None = None
