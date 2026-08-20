from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.modules.ctdisr.repository import (
    CTDISRControlRepository,
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


class CTDISRControlService:

    def __init__(
        self,
        repository: CTDISRControlRepository | None = None,
    ) -> None:

        self.repository = (
            repository
            or CTDISRControlRepository()
        )

    # =========================================================
    # GET ALL
    # =========================================================

    def get_controls(
        self,
        include_inactive: bool = False,
    ) -> list[dict[str, Any]]:

        return self.repository.get_all(
            include_inactive=include_inactive
        )

    # =========================================================
    # GET ONE
    # =========================================================

    def get_control(
        self,
        control_id: str,
    ) -> dict[str, Any] | None:

        return self.repository.get_by_id(
            control_id
        )

    # =========================================================
    # CREATE
    # =========================================================

    def create_control(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:

        control_id = data["control_id"].strip()

        existing = self.repository.get_by_id(
            control_id
        )

        if existing is not None:
            raise ValueError(
                f"CTDISR control '{control_id}' already exists."
            )

        now = utc_now()

        control = {
            "control_id": control_id,

            "control_level": data[
                "control_level"
            ].strip(),

            "control_description": data[
                "control_description"
            ].strip(),

            "interpretation": data.get(
                "interpretation",
                "",
            ).strip(),

            "pta_response": data.get(
                "pta_response",
                "",
            ).strip(),

            "pta_recommendations": data.get(
                "pta_recommendations",
                "",
            ).strip(),

            "action_by": data.get(
                "action_by",
                "",
            ).strip(),

            "ntc_comments": data.get(
                "ntc_comments",
                "",
            ).strip(),

            "source_document": data.get(
                "source_document"
            ),

            "status": "active",

            "version": "1.0",

            "created_at": now,

            "updated_at": now,
        }

        return self.repository.create(
            control
        )

    # =========================================================
    # UPDATE
    # =========================================================

    def update_control(
        self,
        control_id: str,
        updates: dict[str, Any],
    ) -> dict[str, Any] | None:

        existing = self.repository.get_by_id(
            control_id
        )

        if existing is None:
            return None

        cleaned: dict[str, Any] = {}

        allowed_fields = {
            "control_level",
            "control_description",
            "interpretation",
            "pta_response",
            "pta_recommendations",
            "action_by",
            "ntc_comments",
            "source_document",
            "status",
        }

        for field, value in updates.items():

            if field not in allowed_fields:
                continue

            if value is None:
                continue

            if isinstance(value, str):
                cleaned[field] = value.strip()
            else:
                cleaned[field] = value

        cleaned["updated_at"] = utc_now()

        return self.repository.update(
            control_id,
            cleaned,
        )

    # =========================================================
    # DEACTIVATE
    # =========================================================

    def deactivate_control(
        self,
        control_id: str,
    ) -> dict[str, Any] | None:

        existing = self.repository.get_by_id(
            control_id
        )

        if existing is None:
            return None

        return self.repository.update(
            control_id,
            {
                "status": "inactive",
                "updated_at": utc_now(),
            },
        )

    # =========================================================
    # STATISTICS
    # =========================================================

    def get_statistics(self) -> dict[str, int]:

        total = self.repository.count(
            include_inactive=True
        )

        active = self.repository.count(
            include_inactive=False
        )

        return {
            "total_controls": total,
            "active_controls": active,
            "inactive_controls": total - active,
        }