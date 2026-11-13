from dataclasses import dataclass


@dataclass
class PrismaTranscriber:
    endpoint: str | None
    api_key: str | None

    def transcribe(self, _audio_bytes: bytes, _language: str = "hi-IN") -> str:
        if not self.endpoint or not self.api_key:
            raise RuntimeError(
                "Gnani Prisma configuration missing. Set GNANI_PRISMA_URL and GNANI_PRISMA_API_KEY."
            )
        raise NotImplementedError("Implement according to verified Gnani Prisma API documentation.")
