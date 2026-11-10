from dataclasses import dataclass


@dataclass
class TimbreSynthesizer:
    endpoint: str | None
    api_key: str | None

    def synthesize(self, _text: str, _language: str = "hi-IN") -> bytes:
        if not self.endpoint or not self.api_key:
            raise RuntimeError(
                "Gnani Timbre configuration missing. Set GNANI_TIMBRE_URL and GNANI_TIMBRE_API_KEY."
            )
        raise NotImplementedError("Implement according to verified Gnani Timbre API documentation.")
