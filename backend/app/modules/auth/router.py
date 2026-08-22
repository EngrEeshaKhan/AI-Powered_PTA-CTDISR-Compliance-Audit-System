from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

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

    Currently this validates the username/password and
    returns the authenticated user's role.

    JWT/session authentication will be connected later.
    """

    user = service.authenticate(
        username=data.username,
        password=data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    return {
        "success": True,
        "message": "Login successful.",
        "username": user.username,
        "role": user.role,
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
):
    """
    Create a new application user.

    NOTE:
    Permission protection will be added after the
    authentication dependency layer is implemented.
    """

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
def get_users():
    """
    Return all registered application users.

    Admin-only protection will be added later.
    """

    return service.get_users()


# =========================================================
# GET CURRENT USER
# =========================================================

@router.get(
    "/users/{username}",
    response_model=UserResponse,
)
def get_user(
    username: str,
):
    user = service.get_user(
        username
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found.",
        )

    return user