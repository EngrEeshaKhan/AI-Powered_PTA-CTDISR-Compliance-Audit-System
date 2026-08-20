from fastapi import FastAPI

from app.api.v1.uploads import router as uploads_router
from app.api.v1.ctdisr import router as ctdisr_router

from app.modules.audits.json_audit_router import (
    router as saved_audit_router,
)


app = FastAPI(
    title="AI-Powered PTA CTDISR Compliance Audit System",
    description=(
        "Backend API for document ingestion, knowledge-base indexing, "
        "retrieval, and PTA CTDISR compliance auditing."
    ),
    version="1.0.0",
)


# =========================================================
# API ROUTERS
# =========================================================

app.include_router(
    uploads_router,
    prefix="/api/v1",
)

app.include_router(
    ctdisr_router,
    prefix="/api/v1",
)

app.include_router(
    saved_audit_router,
    prefix="/api/v1",
)


# =========================================================
# SYSTEM
# =========================================================

@app.get(
    "/",
    tags=["System"],
)
def root():
    return {
        "status": "online",
        "message": (
            "AI-Powered PTA CTDISR "
            "Compliance Audit System API"
        ),
    }


@app.get(
    "/health",
    tags=["System"],
)
def health_check():
    return {
        "status": "healthy",
    }