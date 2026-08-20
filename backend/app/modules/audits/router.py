from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.modules.audits.schemas import (
    AuditCreate,
    AuditResponse,
)
from app.modules.audits.service import AuditService


router = APIRouter(
    prefix="/audits",
    tags=["Audits"],
)

service = AuditService()


# =========================================================
# CREATE AUDIT
# =========================================================

@router.post(
    "",
    response_model=AuditResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_audit(
    payload: AuditCreate,
):
    """
    Create a new PTA CTDISR audit.
    """

    try:
        return service.create_audit(
            audit_name=payload.audit_name,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# =========================================================
# GET ALL AUDITS
# =========================================================

@router.get(
    "",
    response_model=list[AuditResponse],
)
def get_audits():
    """
    Return all audits.
    """

    return service.get_audits()


# =========================================================
# GET ONE AUDIT
# =========================================================

@router.get(
    "/{audit_id}",
    response_model=AuditResponse,
)
def get_audit(
    audit_id: str,
):
    """
    Return one audit.
    """

    audit = service.get_audit(
        audit_id,
    )

    if audit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit '{audit_id}' was not found.",
        )

    return audit


# =========================================================
# RUN COMPLETE AUDIT
# =========================================================

@router.post(
    "/{audit_id}/run",
)
def run_audit(
    audit_id: str,
):
    """
    Run the AI audit for ALL active CTDISR controls.

    The user only selects an audit.
    The backend automatically processes every control.
    """

    try:
        return service.run_audit(
            audit_id=audit_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audit failed: {str(exc)}",
        )