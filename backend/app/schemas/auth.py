"""Authentication request and response schemas."""

import re
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RegisterRequest(BaseModel):
    """Public registration data; role assignment is server-controlled."""

    model_config = ConfigDict(extra="forbid")

    full_name: Annotated[str, Field(min_length=1, max_length=100)]
    email: Annotated[str, Field(min_length=3, max_length=255)]
    password: Annotated[str, Field(min_length=12)]

    @field_validator("full_name")
    @classmethod
    def full_name_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Full name cannot be blank.")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("A valid email address is required.")
        return value

    @field_validator("password")
    @classmethod
    def bcrypt_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes.")
        return value


class LoginRequest(BaseModel):
    """Credentials for creating a server-managed session."""

    email: Annotated[str, Field(min_length=3, max_length=255)]
    password: Annotated[str, Field(min_length=1, max_length=72)]

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("password")
    @classmethod
    def bcrypt_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes.")
        return value


class PasswordResetRequest(BaseModel):
    """Email address for a password-reset request."""

    email: Annotated[str, Field(min_length=3, max_length=255)]

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class PasswordResetConfirm(BaseModel):
    """Reset token and replacement password."""

    token: Annotated[str, Field(min_length=20, max_length=200)]
    new_password: Annotated[str, Field(min_length=12)]

    @field_validator("new_password")
    @classmethod
    def bcrypt_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes.")
        return value


class AuthenticatedUser(BaseModel):
    """Identity and role resolved from a valid database session."""

    user_id: int
    session_id: int
    full_name: str
    email: str
    role_name: str


class SafeUserResponse(BaseModel):
    """User information safe to return to a client."""

    user_id: int
    full_name: str
    email: str
    role: str


class RegisterResponse(BaseModel):
    """Safe registration result."""

    user: SafeUserResponse


class LoginResponse(BaseModel):
    """New bearer token and safe user information."""

    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: SafeUserResponse


class PasswordResetRequestResponse(BaseModel):
    """Generic reset acknowledgement, optionally with a local dev token."""

    message: str
    reset_token: str | None = None
