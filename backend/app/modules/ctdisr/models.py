from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CTDISRControl:
    """
    CTDISR Control Master Record.

    These fields are maintained by the administrator.

    The AI audit process will use these fields later when
    generating an audit assessment for this control.
    """

    # ---------------------------------------------------------
    # REGULATORY CONTROL
    # ---------------------------------------------------------

    control_id: str
    control_level: str
    control_description: str
    interpretation: str = ""

    # ---------------------------------------------------------
    # AUDIT INFORMATION
    # ---------------------------------------------------------

    pta_response: str = ""
    pta_recommendations: str = ""
    action_by: str = ""
    ntc_comments: str = ""

    # ---------------------------------------------------------
    # SOURCE / VERSION
    # ---------------------------------------------------------

    source_document: str | None = None

    status: str = "active"
    version: str = "1.0"

    # ---------------------------------------------------------
    # TIMESTAMPS
    # ---------------------------------------------------------

    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)