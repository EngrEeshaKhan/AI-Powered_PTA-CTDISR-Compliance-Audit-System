from __future__ import annotations

from pydantic import BaseModel, Field

from app.core.auth import UserRole


# =========================================================
# LOGIN REQUEST
# =========================================================

class LoginRequest(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )

    password: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )


# =========================================================
# USER CREATE
# =========================================================

class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )

    password: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    role: UserRole = UserRole.AUDITOR


# =========================================================
# USER RESPONSE
# =========================================================

class UserResponse(BaseModel):
    username: str
    role: UserRole
    is_active: bool


# =========================================================
# LOGIN RESPONSE
# =========================================================

class LoginResponse(BaseModel):
    success: bool
    message: str
    username: str
    role: UserRole

    access_token: str
    token_type: str = "bearer"