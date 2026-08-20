from __future__ import annotations

from pydantic import BaseModel, Field


# =========================================================
# CREATE AUDIT
# =========================================================

class AuditCreate(BaseModel):
    audit_name: str = Field(
        min_length=1,
        description="Name of the audit.",
    )


# =========================================================
# AUDIT RESPONSE
# =========================================================

class AuditResponse(BaseModel):
    audit_id: str
    audit_name: str
    status: str
    created_at: str
    updated_at: str


# =========================================================
# EDIT AUDIT RESULT
# =========================================================

class AuditResultEdit(BaseModel):
    """
    Fields that the PTA auditor is allowed to edit
    after AI generates the audit result.

    Control information is intentionally NOT included.
    NTC comments are also intentionally NOT included.
    """

    pta_response: str | None = Field(
        default=None,
        description="Auditor-edited PTA response.",
    )

    pta_recommendations: str | None = Field(
        default=None,
        description="Auditor-edited PTA recommendation.",
    )

    action_by: str | None = Field(
        default=None,
        description="Auditor-edited responsible action owner.",
    )


# =========================================================
# AUDIT RESULT RESPONSE
# =========================================================

class AuditResultResponse(BaseModel):

    result_id: str
    audit_id: str
    control_id: str

    control_level: str
    control_description: str
    interpretation: str

    pta_response: str
    pta_recommendations: str
    action_by: str

    ntc_comments: str

    status: str

    last_edited_by: str | None
    last_edited_at: str | None

    created_at: str
    updated_at: str


# =========================================================
# FINALIZE AUDIT RESULT
# =========================================================

class AuditResultFinalize(BaseModel):
    """
    Used when the PTA auditor finalizes
    an individual control result.
    """

    finalized_by: str = Field(
        default="auditor",
        min_length=1,
    )