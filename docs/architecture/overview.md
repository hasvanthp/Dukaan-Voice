# DukaanAI Architecture Overview

Pipeline:
Speech Input → Transcription → Intent Detection → Entity Extraction → Confidence Assessment → Business Validation → User Confirmation → Database Operation → Response Generation → Speech Output.

Key modules are separated across API routes, services, repositories, integrations, configuration and schemas.

Sensitive operations (inventory updates, sales creation, payments) require confirmation and idempotency keys to prevent duplicate execution.

Gnani and LLM integrations are adapter-based and require explicit environment configuration.
