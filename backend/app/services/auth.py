"""Authentication, session, and password-reset application logic."""

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import APIError
from app.core.security import generate_token, hash_password, hash_token, verify_password
from app.repositories.auth import AuthRepository
from app.schemas.auth import (
    AuthenticatedUser,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
)

FAILED_LOGIN_LIMIT = 5
LOCKOUT_DURATION = timedelta(minutes=15)
SESSION_DURATION = timedelta(hours=24)
RESET_TOKEN_DURATION = timedelta(minutes=30)
DUMMY_PASSWORD_HASH = hash_password("AEGIS constant-time authentication placeholder")
GENERIC_RESET_MESSAGE = (
    "If the account exists, password reset instructions will be provided."
)


def _utc_now() -> datetime:
    """Use naive UTC timestamps to match the database's timestamp columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AuthService:
    """Coordinate authentication workflows using the existing auth tables."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._repository = AuthRepository(session)

    def register(self, request: RegisterRequest) -> dict[str, Any]:
        if self._repository.find_user_by_email(request.email) is not None:
            raise APIError(409, "EMAIL_ALREADY_REGISTERED", "Email is already registered.")
        try:
            user = self._repository.create_user(
                full_name=request.full_name.strip(),
                email=request.email,
                password_hash=hash_password(request.password),
            )
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            diagnostic = getattr(error.orig, "diag", None)
            if getattr(diagnostic, "constraint_name", None) == "users_email_key":
                raise APIError(
                    409, "EMAIL_ALREADY_REGISTERED", "Email is already registered."
                ) from error
            raise
        return self._safe_user(user)

    def login(self, request: LoginRequest) -> dict[str, Any]:
        now = _utc_now()
        user = self._repository.find_user_by_email(request.email)
        if user is None:
            verify_password(request.password, DUMMY_PASSWORD_HASH)
            self._session.rollback()
            raise APIError(401, "INVALID_CREDENTIALS", "Email or password is incorrect.")

        password_matches = verify_password(request.password, user["password_hash"])
        if not user["is_active"] or (
            user["locked_until"] is not None and user["locked_until"] > now
        ):
            self._session.rollback()
            raise APIError(401, "INVALID_CREDENTIALS", "Email or password is incorrect.")
        if not password_matches:
            self._repository.record_failed_login(
                user["user_id"],
                now=now,
                lock_until=now + LOCKOUT_DURATION,
                lock_after=FAILED_LOGIN_LIMIT,
            )
            self._session.commit()
            raise APIError(401, "INVALID_CREDENTIALS", "Email or password is incorrect.")

        token = generate_token()
        expires_at = now + SESSION_DURATION
        self._repository.record_successful_login(user["user_id"], now)
        self._repository.create_session(
            user["user_id"], token_hash=hash_token(token), expires_at=expires_at
        )
        self._session.commit()
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_at": expires_at,
            "user": self._safe_user(user),
        }

    def resolve_session(self, token: str) -> AuthenticatedUser:
        user = self._repository.find_valid_session(hash_token(token), _utc_now())
        if user is None:
            raise APIError(401, "UNAUTHENTICATED", "A valid session is required.")
        return AuthenticatedUser(
            user_id=user["user_id"],
            session_id=user["session_id"],
            full_name=user["full_name"],
            email=user["email"],
            role_name=user["role_name"],
        )

    def logout(self, user: AuthenticatedUser) -> None:
        self._repository.revoke_session(user.session_id, _utc_now())
        self._session.commit()

    def request_password_reset(
        self,
        request: PasswordResetRequest,
    ) -> dict[str, str]:
        now = _utc_now()
        user = self._repository.find_user_by_email(request.email)
        result = {"message": GENERIC_RESET_MESSAGE}
        if user is not None:
            token = generate_token()
            self._repository.create_password_reset(
                user_id=user["user_id"],
                token_hash=hash_token(token),
                expires_at=now + RESET_TOKEN_DURATION,
            )
            self._session.commit()
            settings = get_settings()
            if (
                settings.environment.lower() in {"development", "dev", "local"}
                and settings.auth_expose_reset_token
            ):
                result["reset_token"] = token
        else:
            self._session.rollback()
        return result

    def confirm_password_reset(self, request: PasswordResetConfirm) -> None:
        now = _utc_now()
        token_hash = hash_token(request.token)
        if not self._repository.has_valid_password_reset(token_hash, now):
            raise APIError(
                400, "INVALID_RESET_TOKEN", "The reset token is invalid or expired."
            )
        consumed = self._repository.consume_password_reset(
            token_hash=token_hash,
            password_hash=hash_password(request.new_password),
            now=now,
        )
        if not consumed:
            self._session.rollback()
            raise APIError(400, "INVALID_RESET_TOKEN", "The reset token is invalid or expired.")
        self._session.commit()

    @staticmethod
    def _safe_user(user: dict[str, Any]) -> dict[str, Any]:
        return {
            "user_id": user["user_id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role_name"],
        }
