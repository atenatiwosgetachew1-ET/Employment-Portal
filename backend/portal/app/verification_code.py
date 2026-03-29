import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import Profile

CODE_LENGTH = 6
CODE_TTL_MINUTES = 15


def generate_code() -> str:
    return f"{secrets.randbelow(10**CODE_LENGTH):0{CODE_LENGTH}d}"


def _hash_code(six_digits: str) -> str:
    payload = f"{six_digits}{settings.SECRET_KEY}".encode()
    return hashlib.sha256(payload).hexdigest()


def normalize_code_input(raw: str) -> str | None:
    digits = "".join(c for c in (raw or "") if c.isdigit())
    if len(digits) != CODE_LENGTH:
        return None
    return digits


def store_code_on_profile(profile: Profile, plain_code: str) -> None:
    if len(plain_code) != CODE_LENGTH or not plain_code.isdigit():
        raise ValueError("Invalid code format")
    profile.email_verification_code_hash = _hash_code(plain_code)
    profile.email_verification_code_expires = timezone.now() + timedelta(
        minutes=CODE_TTL_MINUTES
    )
    profile.save(
        update_fields=[
            "email_verification_code_hash",
            "email_verification_code_expires",
        ]
    )


def clear_code_on_profile(profile: Profile) -> None:
    profile.email_verification_code_hash = ""
    profile.email_verification_code_expires = None
    profile.save(
        update_fields=[
            "email_verification_code_hash",
            "email_verification_code_expires",
        ]
    )


def verify_code_for_profile(profile: Profile, submitted_raw: str) -> bool:
    normalized = normalize_code_input(submitted_raw)
    if not normalized:
        return False
    if not profile.email_verification_code_hash or not profile.email_verification_code_expires:
        return False
    if timezone.now() > profile.email_verification_code_expires:
        return False
    return _hash_code(normalized) == profile.email_verification_code_hash
