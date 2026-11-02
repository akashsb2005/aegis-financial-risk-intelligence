"""Database access for existing authentication tables."""

from datetime import datetime
from functools import lru_cache
from typing import Any

from sqlalchemy import MetaData, Table, case, insert, select, update
from sqlalchemy.orm import Session

from app.core.database import engine


@lru_cache(maxsize=1)
def _users_table() -> Table:
    return Table("users", MetaData(), schema="public", autoload_with=engine)


@lru_cache(maxsize=1)
def _roles_table() -> Table:
    return Table("roles", MetaData(), schema="public", autoload_with=engine)


@lru_cache(maxsize=1)
def _sessions_table() -> Table:
    return Table("user_sessions", MetaData(), schema="public", autoload_with=engine)


@lru_cache(maxsize=1)
def _reset_tokens_table() -> Table:
    return Table(
        "password_reset_tokens",
        MetaData(),
        schema="public",
        autoload_with=engine,
    )


class AuthRepository:
    """Query and update the database's existing authentication tables."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._users = _users_table()
        self._roles = _roles_table()
        self._sessions = _sessions_table()
        self._reset_tokens = _reset_tokens_table()

    def find_user_by_email(self, email: str) -> dict[str, Any] | None:
        statement = (
            select(
                self._users.c.user_id,
                self._users.c.role_id,
                self._users.c.full_name,
                self._users.c.email,
                self._users.c.password_hash,
                self._users.c.is_active,
                self._users.c.failed_login_attempts,
                self._users.c.locked_until,
                self._roles.c.role_name,
            )
            .join(self._roles, self._roles.c.role_id == self._users.c.role_id)
            .where(self._users.c.email == email)
        )
        row = self._session.execute(statement).mappings().one_or_none()
        return dict(row) if row is not None else None

    def create_user(
        self,
        full_name: str,
        email: str,
        password_hash: str,
    ) -> dict[str, Any]:
        role_id = self._session.execute(
            select(self._roles.c.role_id).where(self._roles.c.role_name == "ANALYST")
        ).scalar_one()
        statement = (
            insert(self._users)
            .values(
                role_id=role_id,
                full_name=full_name,
                email=email,
                password_hash=password_hash,
                is_active=True,
                failed_login_attempts=0,
            )
            .returning(
                self._users.c.user_id,
                self._users.c.full_name,
                self._users.c.email,
            )
        )
        row = self._session.execute(statement).mappings().one()
        return {**dict(row), "role_name": "ANALYST"}

    def record_failed_login(
        self,
        user_id: int,
        now: datetime,
        lock_until: datetime,
        lock_after: int,
    ) -> None:
        next_attempts = self._users.c.failed_login_attempts + 1
        self._session.execute(
            update(self._users)
            .where(self._users.c.user_id == user_id)
            .values(
                failed_login_attempts=next_attempts,
                locked_until=case(
                    (next_attempts >= lock_after, lock_until),
                    else_=None,
                ),
                updated_at=now,
            )
        )

    def record_successful_login(self, user_id: int, now: datetime) -> None:
        self._session.execute(
            update(self._users)
            .where(self._users.c.user_id == user_id)
            .values(
                failed_login_attempts=0,
                locked_until=None,
                last_login_at=now,
                updated_at=now,
            )
        )

    def create_session(
        self,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
    ) -> int:
        statement = (
            insert(self._sessions)
            .values(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
            .returning(self._sessions.c.session_id)
        )
        return self._session.execute(statement).scalar_one()

    def find_valid_session(
        self,
        token_hash: str,
        now: datetime,
    ) -> dict[str, Any] | None:
        statement = (
            select(
                self._sessions.c.session_id,
                self._users.c.user_id,
                self._users.c.full_name,
                self._users.c.email,
                self._roles.c.role_name,
            )
            .join(self._users, self._users.c.user_id == self._sessions.c.user_id)
            .join(self._roles, self._roles.c.role_id == self._users.c.role_id)
            .where(
                self._sessions.c.token_hash == token_hash,
                self._sessions.c.expires_at > now,
                self._sessions.c.revoked_at.is_(None),
                self._users.c.is_active.is_(True),
            )
        )
        row = self._session.execute(statement).mappings().one_or_none()
        return dict(row) if row is not None else None

    def revoke_session(self, session_id: int, now: datetime) -> None:
        self._session.execute(
            update(self._sessions)
            .where(
                self._sessions.c.session_id == session_id,
                self._sessions.c.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )

    def create_password_reset(
        self,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
    ) -> None:
        self._session.execute(
            insert(self._reset_tokens).values(
                user_id=user_id,
                token_hash=token_hash,
                expires_at=expires_at,
            )
        )

    def has_valid_password_reset(self, token_hash: str, now: datetime) -> bool:
        statement = (
            select(self._reset_tokens.c.token_id)
            .where(
                self._reset_tokens.c.token_hash == token_hash,
                self._reset_tokens.c.used_at.is_(None),
                self._reset_tokens.c.expires_at > now,
            )
            .limit(1)
        )
        return self._session.execute(statement).scalar_one_or_none() is not None

    def consume_password_reset(
        self,
        token_hash: str,
        password_hash: str,
        now: datetime,
    ) -> bool:
        statement = (
            select(
                self._reset_tokens.c.token_id,
                self._reset_tokens.c.user_id,
            )
            .where(
                self._reset_tokens.c.token_hash == token_hash,
                self._reset_tokens.c.used_at.is_(None),
                self._reset_tokens.c.expires_at > now,
            )
            .with_for_update(of=self._reset_tokens)
        )
        row = self._session.execute(statement).mappings().one_or_none()
        if row is None:
            return False

        self._session.execute(
            update(self._users)
            .where(self._users.c.user_id == row["user_id"])
            .values(password_hash=password_hash, updated_at=now)
        )
        self._session.execute(
            update(self._reset_tokens)
            .where(self._reset_tokens.c.token_id == row["token_id"])
            .values(used_at=now)
        )
        self._session.execute(
            update(self._sessions)
            .where(
                self._sessions.c.user_id == row["user_id"],
                self._sessions.c.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )
        return True
