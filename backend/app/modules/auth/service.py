from __future__ import annotations

from app.core.auth import UserRole
from app.core.security import hash_password, verify_password
from app.modules.auth.models import User
from app.modules.auth.repository import UserRepository


class AuthService:
    """
    Authentication and user-management business logic.
    """

    def __init__(
        self,
        repository: UserRepository | None = None,
    ) -> None:
        self.repository = (
            repository
            or UserRepository()
        )

    # =========================================================
    # CREATE USER
    # =========================================================

    def create_user(
        self,
        username: str,
        password: str,
        role: UserRole,
    ) -> User:

        username = username.strip()

        if not username:
            raise ValueError(
                "Username cannot be empty."
            )

        if not password:
            raise ValueError(
                "Password cannot be empty."
            )

        existing = self.repository.get_by_username(
            username
        )

        if existing is not None:
            raise ValueError(
                f"User '{username}' already exists."
            )

        user = User(
            username=username,
            password_hash=hash_password(password),
            role=role,
            is_active=True,
        )

        return self.repository.create(user)

    # =========================================================
    # AUTHENTICATE
    # =========================================================

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> User | None:

        user = self.repository.get_by_username(
            username.strip()
        )

        if user is None:
            return None

        if not user.is_active:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        return user

    # =========================================================
    # GET USER
    # =========================================================

    def get_user(
        self,
        username: str,
    ) -> User | None:

        return self.repository.get_by_username(
            username.strip()
        )

    # =========================================================
    # GET ALL USERS
    # =========================================================

    def get_users(self) -> list[User]:

        return self.repository.get_all()

    # =========================================================
    # DEACTIVATE USER
    # =========================================================

    def deactivate_user(
        self,
        username: str,
    ) -> User | None:

        user = self.repository.get_by_username(
            username.strip()
        )

        if user is None:
            return None

        user.is_active = False

        return self.repository.update(user)