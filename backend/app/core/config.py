from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DukaanAI"
    environment: Literal["dev", "staging", "prod", "test"] = "dev"
    api_prefix: str = "/api/v1"

    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None
    database_url: str | None = None

    llm_provider: str = "rule_based"
    llm_model: str = "gpt-4o-mini"

    gnani_prisma_url: str | None = None
    gnani_prisma_api_key: str | None = None
    gnani_timbre_url: str | None = None
    gnani_timbre_api_key: str | None = None

    sensitive_intents: set[str] = Field(
        default_factory=lambda: {"create_sale", "record_payment", "add_inventory"}
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
