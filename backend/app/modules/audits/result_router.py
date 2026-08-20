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
# GET ALL RESULTS FOR AN AUDIT
# =========================================================

@router.get(
    "/{audit_id}/results",
)
def get_audit_results(
    audit_id: str,
):
    """
    Return all saved results for one audit.
    """

    return service.get_audit_results(
        audit_id
    )


# =========================================================
# GET ONE RESULT
# =========================================================

@router.get(
    "/results/{result_id}",
)
def get_result(
    result_id: str,
):
    """
    Return one saved audit result.
    """

    result = service.get_result(
        result_id
    )

    if result is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Audit result "
                f"'{result_id}' not found."
            ),
        )

    return result


# =========================================================
# EDIT / SAVE RESULT
# =========================================================

class AuditResultEdit(BaseModel):

    pta_response: str | None = None

    pta_recommendations: str | None = None

    action_by: str | None = None

    ntc_comments: str | None = None


@router.put(
    "/results/{result_id}",
)
def edit_result(
    result_id: str,
    data: AuditResultEdit,
):
    """
    Edit and SAVE an audit result.

    Editable:
        - PTA Response
        - PTA Recommendations
        - Action By
        - NTC Comments

    Static control fields are protected.
    """

    try:

        return service.edit_result(
            result_id=result_id,
            pta_response=data.pta_response,
            pta_recommendations=(
                data.pta_recommendations
            ),
            action_by=data.action_by,
            ntc_comments=data.ntc_comments,
            edited_by="auditor",
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# =========================================================
# DELETE RESULT
# =========================================================

@router.delete(
    "/results/{result_id}",
)
def delete_result(
    result_id: str,
):
    """
    Delete a saved audit result.
    """

    try:

        result = service.get_result(
            result_id
        )

        if result is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Audit result "
                    f"'{result_id}' not found."
                ),
            )

        if result.status == "finalized":

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Finalized audit results "
                    "cannot be deleted."
                ),
            )

        deleted = service.repository.delete(
            result_id
        )

        if not deleted:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Audit result "
                    f"'{result_id}' not found."
                ),
            )

        return {
            "success": True,
            "message": (
                "Audit result deleted successfully."
            ),
            "result_id": result_id,
        }

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )