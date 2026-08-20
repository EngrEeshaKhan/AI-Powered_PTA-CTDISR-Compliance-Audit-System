from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.modules.audits.result_service import AuditResultService


router = APIRouter(
    prefix="/audits",
    tags=["Audit Results"],
)

service = AuditResultService()


# =========================================================
# GET RESULTS FOR AN AUDIT
# =========================================================

@router.get(
    "/{audit_id}/results",
)
def get_audit_results(
    audit_id: str,
):
    """
    Return all results for the selected audit.
    """

    return service.get_audit_results(
        audit_id,
    )


# =========================================================
# EDIT + SAVE RESULT
# =========================================================

class AuditResultEdit(BaseModel):

    pta_response: str | None = None
    pta_recommendations: str | None = None
    action_by: str | None = None


@router.put(
    "/results/{result_id}",
)
def edit_result(
    result_id: str,
    data: AuditResultEdit,
):
    """
    Edit and save the three audit fields.

    Editable:
        PTA Response
        PTA Recommendations
        Action By
    """

    try:

        return service.edit_result(
            result_id=result_id,
            pta_response=data.pta_response,
            pta_recommendations=data.pta_recommendations,
            action_by=data.action_by,
            edited_by="auditor",
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )