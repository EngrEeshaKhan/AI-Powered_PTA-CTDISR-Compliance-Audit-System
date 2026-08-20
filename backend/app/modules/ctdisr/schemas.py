from __future__ import annotations

from pydantic import BaseModel, Field


# =========================================================
# CREATE CONTROL
# =========================================================

class CTDISRControlCreate(BaseModel):
    """
    Data entered by administrator when creating a control.
    """

    control_id: str = Field(
        ...,
        min_length=1,
        description="CTDISR control identifier, e.g. 3.1",
    )

    control_level: str = Field(
        ...,
        min_length=1,
        description="Control level, e.g. CL1, CL2, CL3",
    )

    control_description: str = Field(
        ...,
        min_length=1,
        description="Official CTDISR control requirement",
    )

    interpretation: str = Field(
        default="",
        description="Auditor interpretation of the control",
    )

    pta_response: str = Field(
        default="",
        description="PTA audit response/finding",
    )

    pta_recommendations: str = Field(
        default="",
        description="PTA recommendation",
    )

    action_by: str = Field(
        default="",
        description="Responsible department/action owner",
    )

    ntc_comments: str = Field(
        default="",
        description="NTC management comments",
    )

    source_document: str | None = Field(
        default=None,
        description="Source document/reference",
    )


# =========================================================
# UPDATE CONTROL
# =========================================================

class CTDISRControlUpdate(BaseModel):
    """
    Any field may be updated by administrator/auditor.
    """

    control_level: str | None = None

    control_description: str | None = None

    interpretation: str | None = None

    pta_response: str | None = None

    pta_recommendations: str | None = None

    action_by: str | None = None

    ntc_comments: str | None = None

    source_document: str | None = None

    status: str | None = None


# =========================================================
# RESPONSE
# =========================================================

class CTDISRControlResponse(BaseModel):

    control_id: str

    control_level: str

    control_description: str

    interpretation: str

    pta_response: str

    pta_recommendations: str

    action_by: str

    ntc_comments: str

    source_document: str | None

    status: str

    version: str

    created_at: str

    updated_at: str