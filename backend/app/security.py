from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import secrets
from typing import Literal


def hash_password(password: str, salt: str) -> str:
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    )
    return password_hash.hex()


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    calculated_hash = hash_password(password, salt)
    return hmac.compare_digest(calculated_hash, expected_hash)


def generate_salt() -> str:
    return secrets.token_hex(16)


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


@dataclass(frozen=True)
class UserRecord:
    email: str
    full_name: str
    role: Literal["coach", "student"]
    salt: str
    password_hash: str
    coach_code: str | None = None
    assignment_status: Literal["unassigned", "pending", "assigned"] = "unassigned"
    assigned_coach_email: str | None = None
    assigned_coach_name: str | None = None
    requested_coach_email: str | None = None
    requested_coach_name: str | None = None
    requested_coach_code: str | None = None
    coach_request_sent_at: str | None = None
    sport: str | None = None
    focus_area: str | None = None
    date_of_birth: str | None = None
    performance_score: int | None = None
