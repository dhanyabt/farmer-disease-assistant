"""Application configuration for the HACKMINT farmer interface."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    backend_url: str = os.getenv("HACKMINT_BACKEND_URL", "")
    request_timeout_seconds: float = float(
        os.getenv("HACKMINT_REQUEST_TIMEOUT", "30")
    )
    demo_mode: bool = os.getenv("HACKMINT_DEMO_MODE", "true").lower() in {
        "1",
        "true",
        "yes",
    }


settings = Settings()
