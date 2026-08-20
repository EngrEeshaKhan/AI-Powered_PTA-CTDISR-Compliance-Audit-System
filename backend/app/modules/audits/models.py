from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Audit:
    """
    PTA CTDISR Audit record.

    The audit itself stores only its basic metadata.
    Individual CTDISR audit results are stored separately.
    """

    audit_id: str
    audit_name: str

    status: str = "draft"

    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)