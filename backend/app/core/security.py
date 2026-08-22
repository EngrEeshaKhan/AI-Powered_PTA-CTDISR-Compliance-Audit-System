from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt


# =========================================================
# JWT CONFIGURATION
# =========================================================

# Development secret.
# IMPORTANT:
# Replace this with a long random secret before deployment.
SECRET_KEY = "pta-ctdisr-development-secret-change-before-production"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =========================================================
# PASSWORD HASHING
# =========================================================

def hash_password(password: str) -> str:
    """
    Hash a user password.

    NOTE:
    SHA-256 is retained for compatibility with the existing
    users created by the current system.

    For production, this should eventually be replaced with
    Argon2 or bcrypt.
    """

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """
    Verify a password against its stored hash.
    """

    return hash_password(password) == password_hash


# =========================================================
# CREATE ACCESS TOKEN
# =========================================================

def create_access_token(
    username: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.

    Token payload:

        sub  -> username
        role -> user role
        exp  -> expiration time
    """

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    expire = datetime.now(
        timezone.utc
    ) + expires_delta

    payload = {
        "sub": username,
        "role": role,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# =========================================================
# DECODE ACCESS TOKEN
# =========================================================

def decode_access_token(
    token: str,
) -> dict | None:
    """
    Decode and validate a JWT access token.

    Returns:
        Token payload dictionary if valid.

    Returns:
        None if token is invalid or expired.
    """

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        return payload

    except JWTError:
        return None