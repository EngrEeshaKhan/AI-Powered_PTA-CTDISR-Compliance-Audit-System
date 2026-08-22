from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token


# =========================================================
# USER ROLES
# =========================================================


class UserRole(str, Enum):
    """
    Application-level user roles.
    """

    ADMIN = "admin"
    AUDITOR = "auditor"


# =========================================================
# CURRENT USER
# =========================================================


@dataclass(frozen=True)
class CurrentUser:
    """
    Represents the authenticated application user.
    """

    username: str
    role: UserRole

    # =====================================================
    # ROLE HELPERS
    # =====================================================

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def is_auditor(self) -> bool:
        return self.role == UserRole.AUDITOR


# =========================================================
# HTTP BEARER
# =========================================================

security_scheme = HTTPBearer(
    auto_error=False,
)


# =========================================================
# GET CURRENT USER
# =========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        security_scheme
    ),
) -> CurrentUser:

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    payload = decode_access_token(
        credentials.credentials
    )

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    username = payload.get("sub")
    role_value = payload.get("role")

    if not username or not role_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        role = UserRole(role_value)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user role in access token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return CurrentUser(
        username=username,
        role=role,
    )


# =========================================================
# ADMIN-ONLY DEPENDENCY
# =========================================================

def require_admin(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
) -> CurrentUser:

    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required.",
        )

    return current_user


# =========================================================
# AUDITOR-ONLY DEPENDENCY
# =========================================================

def require_auditor(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
) -> CurrentUser:

    if not current_user.is_auditor():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Auditor privileges required.",
        )

    return current_user