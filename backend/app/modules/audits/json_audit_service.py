from __future__ import annotations

from typing import Any

from app.modules.audits.audit_result_store import (
    delete_audit_result,
    get_all_audit_results,
    get_audit_result,
    update_audit_result,
)


class JsonAuditService:
    """
    Service for saved audit_results.json records.

    This service intentionally uses the existing JSON format:

        audit_id
        control_id
        control_level
        control_description
        control_interpretation
        pta_response
        pta_recommendations
        action_by
        ntc_comments
        status
        version
        created_at
        updated_at
    """

    # =========================================================
    # GET ALL
    # =========================================================

    def get_all(self) -> list[dict[str, Any]]:
        return get_all_audit_results()

    # =========================================================
    # GET ONE
    # =========================================================

    def get_one(
        self,
        audit_id: str,
    ) -> dict[str, Any] | None:

        return get_audit_result(
            audit_id
        )

    # =========================================================
    # EDIT + SAVE
    # =========================================================

    def edit_and_save(
        self,
        audit_id: str,
        pta_response: str | None = None,
        pta_recommendations: str | None = None,
        action_by: str | None = None,
        ntc_comments: str | None = None,
    ) -> dict[str, Any]:

        existing = get_audit_result(
            audit_id
        )

        if existing is None:

            raise ValueError(
                f"Audit '{audit_id}' not found."
            )

        # -----------------------------------------------------
        # DO NOT ALLOW EDIT AFTER FINALIZATION
        # -----------------------------------------------------

        if existing.get("status") == "finalized":

            raise ValueError(
                "This audit has been finalized "
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

        if ntc_comments is not None:
            updates["ntc_comments"] = (
                ntc_comments.strip()
            )

        if not updates:
            return existing

        updates["status"] = "reviewed"

        updated = update_audit_result(
            audit_id=audit_id,
            updates=updates,
        )

        if updated is None:

            raise ValueError(
                f"Audit '{audit_id}' "
                "could not be updated."
            )

        return updated

    # =========================================================
    # DELETE
    # =========================================================

    def delete(
        self,
        audit_id: str,
    ) -> bool:

        existing = get_audit_result(
            audit_id
        )

        if existing is None:
            return False

        if existing.get("status") == "finalized":

            raise ValueError(
                "Finalized audits cannot be deleted."
            )

        return delete_audit_result(
            audit_id
        )