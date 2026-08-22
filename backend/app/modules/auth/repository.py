from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.auth import UserRole
from app.modules.auth.models import User


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[4]

AUTH_STORAGE_DIR = (
    PROJECT_ROOT
    / "storage"
    / "auth"
)

USERS_FILE = (
    AUTH_STORAGE_DIR
    / "users.json"
)


# =========================================================
# USER REPOSITORY
# =========================================================

class UserRepository:
    """
    Persistent JSON-based user repository.
    """

    def __init__(self) -> None:

        AUTH_STORAGE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not USERS_FILE.exists():
            self._write_data([])

    # =====================================================
    # INTERNAL READ
    # =====================================================

    def _read_data(self) -> list[dict[str, Any]]:

        try:

            with USERS_FILE.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

        except (
            json.JSONDecodeError,
            OSError,
        ):

            return []

        if not isinstance(data, list):
            return []

        return data

    # =====================================================
    # INTERNAL WRITE
    # =====================================================

    def _write_data(
        self,
        data: list[dict[str, Any]],
    ) -> None:

        temporary_file = (
            USERS_FILE.with_suffix(".tmp")
        )

        with temporary_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )

        temporary_file.replace(
            USERS_FILE
        )

    # =====================================================
    # CONVERT JSON → USER
    # =====================================================

    def _to_user(
        self,
        data: dict[str, Any],
    ) -> User:

        return User(
            username=data["username"],
            password_hash=data["password_hash"],
            role=UserRole(data["role"]),
            is_active=data.get(
                "is_active",
                True,
            ),
        )

    # =====================================================
    # FIND BY USERNAME
    # =====================================================

    def get_by_username(
        self,
        username: str,
    ) -> User | None:

        username = username.strip()

        users = self._read_data()

        for data in users:

            if data.get("username") == username:

                return self._to_user(data)

        return None

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        user: User,
    ) -> User:

        users = self._read_data()

        users.append(
            {
                "username": user.username,
                "password_hash": user.password_hash,
                "role": user.role.value,
                "is_active": user.is_active,
            }
        )

        self._write_data(users)

        return user

    # =====================================================
    # LIST USERS
    # =====================================================

    def get_all(self) -> list[User]:

        users = self._read_data()

        return [
            self._to_user(data)
            for data in users
        ]

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        username: str,
        updates: dict[str, Any],
    ) -> User | None:

        users = self._read_data()

        for index, data in enumerate(users):

            if data.get("username") != username:
                continue

            data.update(updates)

            users[index] = data

            self._write_data(users)

            return self._to_user(data)

        return None

    # =====================================================
    # DELETE / DEACTIVATE
    # =====================================================

    def deactivate(
        self,
        username: str,
    ) -> User | None:

        return self.update(
            username,
            {
                "is_active": False,
            },
        )

    # =====================================================
    # EXISTS
    # =====================================================

    def exists(
        self,
        username: str,
    ) -> bool:

        return (
            self.get_by_username(username)
            is not None
        )