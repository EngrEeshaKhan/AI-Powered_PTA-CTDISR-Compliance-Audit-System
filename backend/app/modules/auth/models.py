from __future__ import annotations

from dataclasses import dataclass

from app.core.auth import UserRole


@dataclass
class User:
    """
    Application user.

    Passwords are never stored in plain text.
    """

    username: str
    password_hash: str
    role: UserRole
    is_active: bool = True