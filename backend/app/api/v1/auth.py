from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import (
    CurrentUser,
    require_admin,
)

from app.core.security import create_access_token

from app.modules.auth.schemas import (
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserResponse,
)

from app.modules.auth.service import AuthService


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


service = AuthService()


# =========================================================
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    data: LoginRequest,
):
    """
    Authenticate an application user.

    Returns a JWT access token that must be supplied
    as:

        Authorization: Bearer <access_token>
    """

    user = service.authenticate(
        username=data.username,
        password=data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    # -----------------------------------------------------
    # CREATE JWT
    # -----------------------------------------------------

    access_token = create_access_token(
        username=user.username,
        role=user.role.value,
    )

    return {
        "success": True,
        "message": "Login successful.",
        "username": user.username,
        "role": user.role,
        "access_token": access_token,
        "token_type": "bearer",
    }


# =========================================================
# CREATE USER
# =========================================================

@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    current_user: CurrentUser = Depends(
        require_admin
    ),
):
    """
    Create a new application user.

    Only authenticated administrators can create users.
    """

    # -----------------------------------------------------
    # ADMIN CAN CREATE AUDITOR
    # -----------------------------------------------------

    if data.role.value != "auditor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrators can create auditor accounts only.",
        )

    try:

        user = service.create_user(
            username=data.username,
            password=data.password,
            role=data.role,
        )

        return user

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# =========================================================
# GET USERS
# =========================================================

@router.get(
    "/users",
    response_model=list[UserResponse],
)
def get_users(
    current_user: CurrentUser = Depends(
        require_admin
    ),
):
    """
    Return all registered application users.

    Only administrators can view the user list.
    """

    return service.get_users()


# =========================================================
# GET USER
# =========================================================

@router.get(
    "/users/{username}",
    response_model=UserResponse,
)
def get_user(
    username: str,
    current_user: CurrentUser = Depends(
        require_admin
    ),
):
    """
    Return a specific user.

    Only administrators can access user information.
    """

    user = service.get_user(
        username
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found.",
        )

    return user