from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.modules.audits.result_models import AuditResult
from app.modules.audits.result_repository import AuditResultRepository


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AuditResultService:

    def __init__(
        self,
        repository: AuditResultRepository | None = None,
    ) -> None:

        self.repository = (
            repository
            or AuditResultRepository()
        )

    # =========================================================
    # GET ALL RESULTS
    # =========================================================

    def get_all_results(self) -> list[AuditResult]:

        return self.repository.get_all()

    # =========================================================
    # GET RESULTS FOR AUDIT
    # =========================================================

    def get_audit_results(
        self,
        audit_id: str,
    ) -> list[AuditResult]:

        return self.repository.get_by_audit(
            audit_id
        )

    # =========================================================
    # GET ONE RESULT
    # =========================================================

    def get_result(
        self,
        result_id: str,
    ) -> AuditResult | None:

        return self.repository.get_by_id(
            result_id
        )

    # =========================================================
    # GET RESULT BY AUDIT + CONTROL
    # =========================================================

    def get_control_result(
        self,
        audit_id: str,
        control_id: str,
    ) -> AuditResult | None:

        return self.repository.get_by_audit_and_control(
            audit_id,
            control_id,
        )

    # =========================================================
    # CREATE AI RESULT
    # =========================================================

    def create_result(
        self,
        result: AuditResult,
    ) -> AuditResult:

        existing = (
            self.repository.get_by_audit_and_control(
                result.audit_id,
                result.control_id,
            )
        )

        if existing is not None:
            raise ValueError(
                f"Audit result already exists for "
                f"audit '{result.audit_id}' and "
                f"control '{result.control_id}'."
            )

        result.status = "generated"
        result.manually_edited = False
        result.last_edited_by = None
        result.last_edited_at = None

        return self.repository.create(
            result
        )

    # =========================================================
    # EDIT AI-GENERATED FIELDS
    # =========================================================

    def edit_result(
        self,
        result_id: str,
        pta_response: str | None = None,
        pta_recommendations: str | None = None,
        action_by: str | None = None,
        edited_by: str = "auditor",
    ) -> AuditResult:

        result = self.repository.get_by_id(
            result_id
        )

        if result is None:
            raise ValueError(
                f"Audit result '{result_id}' not found."
            )

        # -----------------------------------------------------
        # FINALIZED RESULTS ARE LOCKED
        # -----------------------------------------------------

        if result.status == "finalized":
            raise ValueError(
                "This audit result has been finalized "
                "and can no longer be edited."
            )

        updates: dict[str, Any] = {}

        if pta_response is not None:
            updates["pta_response"] = (
                pta_response.strip()
            )

        if pta_recommendations is not None:
            updates["pta_recommendations"] = (
                pta_recommendations.strip()
            )

        if action_by is not None:
            updates["action_by"] = (
                action_by.strip()
            )

        # Nothing was actually changed.
        if not updates:
            return result

        # -----------------------------------------------------
        # EDIT METADATA
        # -----------------------------------------------------

        now = utc_now()

        updates["status"] = "reviewed"
        updates["manually_edited"] = True
        updates["last_edited_by"] = edited_by
        updates["last_edited_at"] = now
        updates["updated_at"] = now

        updated = self.repository.update(
            result_id,
            updates,
        )

        if updated is None:
            raise ValueError(
                f"Audit result '{result_id}' could not be updated."
            )

        return updated

    # =========================================================
    # FINALIZE RESULT
    # =========================================================

    def finalize_result(
        self,
        result_id: str,
        finalized_by: str = "auditor",
    ) -> AuditResult:

        result = self.repository.get_by_id(
            result_id
        )

        if result is None:
            raise ValueError(
                f"Audit result '{result_id}' not found."
            )

        if result.status == "finalized":
            raise ValueError(
                "This audit result is already finalized."
            )

        now = utc_now()

        updated = self.repository.update(
            result_id,
            {
                "status": "finalized",
                "last_edited_by": finalized_by,
                "last_edited_at": now,
                "updated_at": now,
            },
        )

        if updated is None:
            raise ValueError(
                f"Audit result '{result_id}' "
                "could not be finalized."
            )

        return updated