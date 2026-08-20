from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


@dataclass
class AuditResult:
    """
    Result of an AI audit for one CTDISR control.

    Static/reference fields:
        - control_id
        - control_level
        - control_description
        - interpretation

    AI-generated fields:
        - pta_response
        - pta_recommendations
        - action_by

    Auditor-editable field:
        - ntc_comments
    """

    # =========================================================
    # IDENTIFICATION
    # =========================================================

    result_id: str
    audit_id: str
    control_id: str

    # =========================================================
    # CONTROL INFORMATION
    # =========================================================

    control_level: str
    control_description: str
    interpretation: str

    # =========================================================
    # AI / AUDIT OUTPUT
    # =========================================================

    pta_response: str = ""
    pta_recommendations: str = ""
    action_by: str = ""

    # =========================================================
    # NTC COMMENTS
    # =========================================================

    ntc_comments: str = ""

    # =========================================================
    # STATUS
    # =========================================================

    status: str = "generated"

    # =========================================================
    # EDIT METADATA
    # =========================================================

    manually_edited: bool = False

    last_edited_by: str | None = None

    last_edited_at: str | None = None

    # =========================================================
    # TIMESTAMPS
    # =========================================================

    created_at: str = field(
        default_factory=utc_now
    )

    updated_at: str = field(
        default_factory=utc_now
    )

    # =========================================================
    # SERIALIZATION
    # =========================================================

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)