from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.modules.audits.json_audit_service import (
    JsonAuditService,
)


router = APIRouter(
    prefix="/audit-results",
    tags=["Saved Audit Results"],
)


service = JsonAuditService()


# =========================================================
# EDIT MODEL
# =========================================================

class AuditResultEdit(BaseModel):

    pta_response: str | None = None

    pta_recommendations: str | None = None

    action_by: str | None = None

    ntc_comments: str | None = None


# =========================================================
# GET ALL SAVED AUDITS
# =========================================================

@router.get(
    "",
)
def get_all_saved_audits():
    """
    Return all saved audit results.
    """

    return {
        "success": True,
        "results": service.get_all(),
    }


# =========================================================
# GET ONE SAVED AUDIT
# =========================================================

@router.get(
    "/{audit_id}",
)
def get_saved_audit(
    audit_id: str,
):
    """
    Return one saved audit by audit_id.
    """

    result = service.get_one(
        audit_id
    )

    if result is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Saved audit "
                f"'{audit_id}' not found."
            ),
        )

    return {
        "success": True,
        "result": result,
    }


# =========================================================
# EDIT + SAVE
# =========================================================

@router.put(
    "/{audit_id}",
)
def edit_saved_audit(
    audit_id: str,
    data: AuditResultEdit,
):
    """
    Edit and SAVE an existing audit.

    Editable:
        - PTA Response
        - PTA Recommendations
        - Action By
        - NTC Comments

    Static fields cannot be changed.
    """

    try:

        updated = service.edit_and_save(
            audit_id=audit_id,
            pta_response=data.pta_response,
            pta_recommendations=(
                data.pta_recommendations
            ),
            action_by=data.action_by,
            ntc_comments=data.ntc_comments,
        )

        return {
            "success": True,
            "message": (
                "Audit result updated and "
                "saved successfully."
            ),
            "result": updated,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# =========================================================
# DELETE
# =========================================================

@router.delete(
    "/{audit_id}",
)
def delete_saved_audit(
    audit_id: str,
):
    """
    Delete one saved audit.
    """

    try:

        deleted = service.delete(
            audit_id
        )

        if not deleted:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Saved audit "
                    f"'{audit_id}' not found."
                ),
            )

        return {
            "success": True,
            "message": (
                "Saved audit deleted successfully."
            ),
            "audit_id": audit_id,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )