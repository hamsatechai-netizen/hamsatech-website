from dataclasses import dataclass
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / "backend" / ".env")
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    session_cookie_name: str = "hamsai_session"
    default_email: str = os.getenv("HAMSA_DEFAULT_EMAIL", "coach@hamsatech.ai")
    default_password: str = os.getenv("HAMSA_DEFAULT_PASSWORD", "Hamsa2026!")
    default_full_name: str = os.getenv("HAMSA_DEFAULT_FULL_NAME", "HamsaTech Coach")
    default_coach_code: str = os.getenv("HAMSA_DEFAULT_COACH_CODE", "HAMSA-COACH-001")
    frontend_origin: str = os.getenv("HAMSA_FRONTEND_ORIGIN", "http://127.0.0.1:5173")
    frontend_origins_raw: str = os.getenv("HAMSA_FRONTEND_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    cookie_secure_raw: str = os.getenv("HAMSA_COOKIE_SECURE", "false")
    cookie_samesite_raw: str = os.getenv("HAMSA_COOKIE_SAMESITE", "lax")

    @property
    def frontend_origins(self) -> list[str]:
        origins = [origin.strip() for origin in self.frontend_origins_raw.split(",") if origin.strip()]
        if self.frontend_origin and self.frontend_origin not in origins:
            origins.append(self.frontend_origin)
        return origins

    @property
    def cookie_secure(self) -> bool:
        return self.cookie_secure_raw.strip().lower() in {"1", "true", "yes", "on"}

    @property
    def cookie_samesite(self) -> Literal["lax", "strict", "none"]:
        normalized = self.cookie_samesite_raw.strip().lower()
        if normalized not in {"lax", "strict", "none"}:
            return "lax"
        return normalized


settings = Settings()
