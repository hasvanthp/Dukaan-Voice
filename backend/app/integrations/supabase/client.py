from dataclasses import dataclass


@dataclass
class SupabaseConfig:
    url: str | None
    anon_key: str | None
    service_role_key: str | None

    def is_configured(self) -> bool:
        return bool(self.url and self.anon_key)
