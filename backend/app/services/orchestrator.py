from __future__ import annotations

from uuid import uuid4

from app.core.config import Settings
from app.repositories.memory import InMemoryRepository
from app.services.intents import RuleBasedIntentService


class ConversationOrchestrator:
    def __init__(self, repo: InMemoryRepository, settings: Settings) -> None:
        self.repo = repo
        self.settings = settings
        self.intent_service = RuleBasedIntentService()

    def process(self, user_id, store_id, text: str, conversation_id: str | None, confirmed: bool = False) -> dict:
        # Pipeline: Input -> Intent -> Entity -> Confidence -> Validate -> Confirm -> Execute -> Response
        intent_result = self.intent_service.detect(text)
        conv_id = conversation_id or f"conv-{uuid4()}"

        if intent_result.confidence < 0.6:
            return {
                "intent": intent_result.intent,
                "confidence": intent_result.confidence,
                "requires_confirmation": False,
                "message": "Mujhe thoda clear boliye. Kya aap stock update, sales ya payment karna chahte hain?",
                "preview_action": None,
            }

        requires_confirmation = intent_result.intent in self.settings.sensitive_intents
        preview = {
            "intent": intent_result.intent,
            "entities": intent_result.entities,
        }
        self.repo.save_conversation_state(conv_id, preview)

        if requires_confirmation and not confirmed:
            return {
                "intent": intent_result.intent,
                "confidence": intent_result.confidence,
                "requires_confirmation": True,
                "message": "Please confirm this action before execution.",
                "preview_action": preview,
            }

        # Execution is intentionally routed to explicit business APIs for safety.
        self.repo.append_audit(store_id, user_id, "conversation.intent_confirmed", preview)
        return {
            "intent": intent_result.intent,
            "confidence": intent_result.confidence,
            "requires_confirmation": False,
            "message": "Action confirmed. Executing via business API.",
            "preview_action": preview,
        }
