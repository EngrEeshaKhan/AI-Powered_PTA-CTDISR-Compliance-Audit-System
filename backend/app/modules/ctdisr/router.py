from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.ai.pipelines.audit_pipeline import get_audit_pipeline

from app.modules.audits.audit_result_store import (
    save_audit_result,
)

from app.modules.ctdisr.schemas import (
    CTDISRControlCreate,
    CTDISRControlResponse,
    CTDISRControlUpdate,
)

from app.modules.ctdisr.service import (
    CTDISRControlService,
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/ctdisr/controls",
    tags=["CTDISR Controls"],
)


service = CTDISRControlService()


# =========================================================
# GET ALL CONTROLS
# =========================================================

@router.get(
    "",
    response_model=list[CTDISRControlResponse],
)
def get_controls(
    include_inactive: bool = Query(
        False,
        description="Include inactive CTDISR controls.",
    ),
):
    return service.get_controls(
        include_inactive=include_inactive,
    )


# =========================================================
# GET STATISTICS
# =========================================================

@router.get(
    "/statistics",
)
def get_statistics():
    return service.get_statistics()


# =========================================================
# GET ONE CONTROL
# =========================================================

@router.get(
    "/{control_id}",
    response_model=CTDISRControlResponse,
)
def get_control(
    control_id: str,
):
    control = service.get_control(
        control_id,
    )

    if control is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"CTDISR control "
                f"'{control_id}' not found."
            ),
        )

    return control


# =========================================================
# CREATE CONTROL
# =========================================================

@router.post(
    "",
    response_model=CTDISRControlResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_control(
    data: CTDISRControlCreate,
):
    try:
        return service.create_control(
            data.model_dump(),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# =========================================================
# UPDATE CONTROL
# =========================================================

@router.put(
    "/{control_id}",
    response_model=CTDISRControlResponse,
)
def update_control(
    control_id: str,
    data: CTDISRControlUpdate,
):
    control = service.update_control(
        control_id,
        data.model_dump(
            exclude_unset=True,
        ),
    )

    if control is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"CTDISR control "
                f"'{control_id}' not found."
            ),
        )

    return control


# =========================================================
# DEACTIVATE CONTROL
# =========================================================

@router.delete(
    "/{control_id}",
    response_model=CTDISRControlResponse,
)
def deactivate_control(
    control_id: str,
):
    control = service.deactivate_control(
        control_id,
    )

    if control is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"CTDISR control "
                f"'{control_id}' not found."
            ),
        )

    return control


# =========================================================
# RUN AI AUDIT
# =========================================================

@router.post(
    "/{control_id}/audit",
)
def audit_control(
    control_id: str,
    top_k: int = Query(
        5,
        ge=1,
        le=20,
        description=(
            "Number of evidence chunks retrieved "
            "for each knowledge-base category."
        ),
    ),
    max_new_tokens: int = Query(
        200,
        ge=100,
        le=1000,
        description=(
            "Maximum number of tokens generated "
            "by the fine-tuned Llama model."
        ),
    ),
):
    control = service.get_control(
        control_id,
    )

    if control is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"CTDISR control "
                f"'{control_id}' not found."
            ),
        )

    try:

        # -----------------------------------------------------
        # RUN AI AUDIT
        # -----------------------------------------------------

        pipeline = get_audit_pipeline()

        result = pipeline.audit_control(
            control_id=control_id,
            top_k=top_k,
            max_new_tokens=max_new_tokens,
        )

        # -----------------------------------------------------
        # SAVE AUDIT RESULT
        # -----------------------------------------------------

        saved_result = save_audit_result(
            result
        )

        # -----------------------------------------------------
        # RESPONSE
        # -----------------------------------------------------

        return {
            "success": True,
            "message": (
                "AI CTDISR audit completed "
                "and saved successfully."
            ),
            "result": saved_result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Required AI model or knowledge-base "
                f"file was not found: {str(exc)}"
            ),
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "AI audit pipeline failed: "
                f"{str(exc)}"
            ),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Unexpected error while executing "
                f"AI CTDISR audit: {str(exc)}"
            ),
        )