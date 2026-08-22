from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.auth import CurrentUser, UserRole


# =========================================================
# AUTHENTICATION SCHEME
# =========================================================

security = HTTPBearer()


# =========================================================
# TEMPORARY CURRENT USER
# =========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
) -> CurrentUser:
    """
    Temporary authentication dependency.

    For now, this recognizes simple demo tokens.
    We will replace this with proper JWT authentication
    after the role permissions are wired and tested.
    """

    token = credentials.credentials

    # -----------------------------------------------------
    # TEMPORARY ADMIN TOKEN
    # -----------------------------------------------------

    if token == "admin-token":

        return CurrentUser(
            username="admin",
            role=UserRole.ADMIN,
        )

    # -----------------------------------------------------
    # TEMPORARY AUDITOR TOKEN
    # -----------------------------------------------------

    if token == "auditor-token":

        return CurrentUser(
            username="auditor",
            role=UserRole.AUDITOR,
        )

    # -----------------------------------------------------
    # INVALID TOKEN
    # -----------------------------------------------------

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token.",
    )


# =========================================================
# REQUIRE ADMIN
# =========================================================

def require_admin(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
) -> CurrentUser:
    """
    Allow only administrators.
    """

    if not current_user.is_admin():

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )

    return current_user


# =========================================================
# REQUIRE AUDITOR
# =========================================================

def require_auditor(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
) -> CurrentUser:
    """
    Allow only auditors.
    """

    if not current_user.is_auditor():

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Auditor access required.",
        )

    return current_user


# =========================================================
# REQUIRE ADMIN OR AUDITOR
# =========================================================

def require_authenticated_user(
    current_user: CurrentUser = Depends(
        get_current_user
    ),
) -> CurrentUser:
    """
    Allow any authenticated application user.
    """

    return current_user