"""FastAPI authentication and role dependencies."""

from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import APIError
from app.core.database import get_db
from app.schemas.auth import AuthenticatedUser
from app.services.auth import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


def require_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    """Resolve the identity and role from a valid stored session token."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise APIError(401, "UNAUTHENTICATED", "A valid session is required.")
    return AuthService(db).resolve_session(credentials.credentials)


def require_role(role_name: str) -> Callable[..., AuthenticatedUser]:
    """Require the authenticated database role to match a specific role."""

    def role_dependency(
        user: AuthenticatedUser = Depends(require_authenticated_user),
    ) -> AuthenticatedUser:
        if user.role_name != role_name:
            raise APIError(403, "FORBIDDEN", "You do not have permission to perform this action.")
        return user

    return role_dependency
