from __future__ import annotations

from fastapi import APIRouter

from app.modules.audits.router import (
    router as audits_router,
)

from app.modules.ctdisr.router import (
    router as ctdisr_router,
)


# =========================================================
# API V1 ROOT ROUTER
# =========================================================

router = APIRouter()


# =========================================================
# CTDISR ROUTES
# =========================================================

router.include_router(
    ctdisr_router,
)


# =========================================================
# AUDIT ROUTES
# =========================================================

router.include_router(
    audits_router,
)