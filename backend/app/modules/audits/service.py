from __future__ import annotations

from uuid import uuid4

from app.ai.pipelines.audit_pipeline import get_audit_pipeline
from app.modules.audits.models import Audit
from app.modules.audits.repository import AuditRepository
from app.modules.audits.result_models import AuditResult
from app.modules.audits.result_repository import AuditResultRepository
from app.modules.ctdisr.service import CTDISRControlService


class AuditService:

    def __init__(self) -> None:
        self.repository = AuditRepository()
        self.result_repository = AuditResultRepository()
        self.control_service = CTDISRControlService()

    # =========================================================
    # CREATE AUDIT
    # =========================================================

    def create_audit(
        self,
        audit_name: str,
    ) -> Audit:

        audit = Audit(
            audit_id=str(uuid4()),
            audit_name=audit_name,
        )

        return self.repository.create(audit)

    # =========================================================
    # GET ALL AUDITS
    # =========================================================

    def get_audits(self) -> list[Audit]:

        return self.repository.get_all()

    # =========================================================
    # GET ONE AUDIT
    # =========================================================

    def get_audit(
        self,
        audit_id: str,
    ) -> Audit | None:

        return self.repository.get_by_id(
            audit_id,
        )

    # =========================================================
    # RUN COMPLETE AUDIT
    # =========================================================

    def run_audit(
        self,
        audit_id: str,
    ) -> dict:

        audit = self.repository.get_by_id(
            audit_id,
        )

        if audit is None:
            raise ValueError(
                f"Audit '{audit_id}' was not found."
            )

        controls = self.control_service.get_controls(
            include_inactive=False,
        )

        if not controls:
            raise ValueError(
                "No active CTDISR controls were found."
            )

        pipeline = get_audit_pipeline()

        results = []

        for control in controls:

            control_id = str(
                control.get("control_id")
                or control.get("control")
                or ""
            ).strip()

            if not control_id:
                continue

            # -------------------------------------------------
            # Run AI for this control
            # -------------------------------------------------

            ai_result = pipeline.audit_control(
                control_id=control_id,
            )

            # -------------------------------------------------
            # Avoid duplicate result for same audit + control
            # -------------------------------------------------

            existing = (
                self.result_repository
                .get_by_audit_and_control(
                    audit_id,
                    control_id,
                )
            )

            if existing is not None:
                results.append(existing)
                continue

            # -------------------------------------------------
            # Save AI result
            # -------------------------------------------------

            result = AuditResult(
                result_id=str(uuid4()),
                audit_id=audit_id,
                control_id=control_id,

                control_level=str(
                    ai_result.get(
                        "control_level",
                        "",
                    )
                ),

                control_description=str(
                    ai_result.get(
                        "control_description",
                        "",
                    )
                ),

                interpretation=str(
                    ai_result.get(
                        "control_interpretation",
                        "",
                    )
                ),

                pta_response=str(
                    ai_result.get(
                        "pta_response",
                        "",
                    )
                ),

                pta_recommendations=str(
                    ai_result.get(
                        "pta_recommendation",
                        "",
                    )
                ),

                action_by=str(
                    ai_result.get(
                        "action_by",
                        "",
                    )
                ),
            )

            saved_result = (
                self.result_repository.create(
                    result,
                )
            )

            results.append(
                saved_result
            )

        return {
            "success": True,
            "message": "AI audit completed successfully.",
            "audit_id": audit_id,
            "audit_name": audit.audit_name,
            "controls_audited": len(results),
            "results": results,
        }