"""Password and opaque-token security helpers."""

import hashlib
import secrets

import bcrypt


def hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode(
        "ascii"
    )


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password using bcrypt's constant-time comparison."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
    except (ValueError, UnicodeEncodeError):
        return False


def generate_token() -> str:
    """Create a cryptographically random opaque token."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hash a high-entropy opaque token for database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
