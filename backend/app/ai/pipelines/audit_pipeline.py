from __future__ import annotations

import re
from typing import Any

from app.ai.llm.llama_inference import get_llama
from app.ai.retrieval.context_builder import ContextBuilder
from app.modules.ctdisr.service import CTDISRControlService


class AuditPipeline:
    """
    AI-assisted PTA CTDISR audit pipeline.

    Static fields:
        - Control
        - Control Level
        - Control Description
        - Control Interpretation

    AI-generated fields:
        - PTA Response
        - PTA Recommendation
        - Action By

    Auditor field:
        - NTC Comments
    """

    def __init__(
        self,
        control_service: CTDISRControlService | None = None,
        context_builder: ContextBuilder | None = None,
    ) -> None:

        self.control_service = (
            control_service
            if control_service is not None
            else CTDISRControlService()
        )

        self.context_builder = (
            context_builder
            if context_builder is not None
            else ContextBuilder()
        )

    # =========================================================
    # CLEAN MODEL RESPONSE
    # =========================================================

    @staticmethod
    def _clean_response(text: str) -> str:

        if not text:
            return ""

        text = text.strip()

        text = re.sub(
            r"```(?:text|markdown)?",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = text.replace(
            "```",
            "",
        )

        text = re.sub(
            r"^\s*assistant\s*:\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        return text.strip()

    # =========================================================
    # EXTRACT SECTION
    # =========================================================

    @classmethod
    def _extract_section(
        cls,
        text: str,
        labels: list[str],
        next_labels: list[str],
    ) -> str:

        if not text:
            return ""

        label_pattern = "|".join(
            re.escape(label)
            for label in labels
        )

        next_pattern = "|".join(
            re.escape(label)
            for label in next_labels
        )

        pattern = (
            rf"(?:^|\n)\s*"
            rf"(?:{label_pattern})"
            rf"\s*:\s*"
            rf"(.*?)"
            rf"(?=\n\s*(?:{next_pattern})\s*:|$)"
        )

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if not match:
            return ""

        return match.group(1).strip()

    # =========================================================
    # PARSE LLM RESPONSE
    # =========================================================

    @classmethod
    def _parse_llm_response(
        cls,
        response: str,
    ) -> dict[str, str]:

        response = cls._clean_response(response)

        if not response:
            return {
                "raw_response": "",
                "pta_response": "",
                "pta_recommendation": "",
                "action_by": "",
            }

        # ------------------------------------------------------
        # If the model accidentally repeats PTA Response,
        # keep the last occurrence.
        # ------------------------------------------------------

        pta_positions = [
            match.start()
            for match in re.finditer(
                r"(?im)^\s*PTA\s+Response\s*:",
                response,
            )
        ]

        if pta_positions:
            response = response[
                pta_positions[-1]:
            ].strip()

        # ------------------------------------------------------
        # PTA RESPONSE
        # ------------------------------------------------------

        pta_response = cls._extract_section(
            response,
            labels=[
                "PTA Response",
                "PTA response",
                "Response",
            ],
            next_labels=[
                "PTA Recommendation",
                "PTA Recommendations",
                "Recommendation",
                "Recommendations",
                "Action By",
                "Action",
            ],
        )

        # ------------------------------------------------------
        # PTA RECOMMENDATION
        # ------------------------------------------------------

        pta_recommendation = cls._extract_section(
            response,
            labels=[
                "PTA Recommendation",
                "PTA Recommendations",
                "Recommendation",
                "Recommendations",
            ],
            next_labels=[
                "Action By",
                "Action",
                "PTA Response",
                "PTA Recommendation",
                "PTA Recommendations",
            ],
        )

        # ------------------------------------------------------
        # ACTION BY
        # ------------------------------------------------------

        action_by = cls._extract_section(
            response,
            labels=[
                "Action By",
                "Action by",
                "Action",
            ],
            next_labels=[
                "PTA Response",
                "PTA Recommendation",
                "PTA Recommendations",
                "Recommendation",
            ],
        )

        return {
            "raw_response": response,
            "pta_response": pta_response,
            "pta_recommendation": pta_recommendation,
            "action_by": action_by,
        }

    # =========================================================
    # VALIDATE AI OUTPUT
    # =========================================================

    @staticmethod
    def _validate_ai_output(
        parsed: dict[str, str],
        control_id: str,
    ) -> None:

        response = parsed.get(
            "pta_response",
            "",
        ).strip()

        recommendation = parsed.get(
            "pta_recommendation",
            "",
        ).strip()

        action_by = parsed.get(
            "action_by",
            "",
        ).strip()

        # ------------------------------------------------------
        # PTA RESPONSE CANNOT SIMPLY BE THE CONTROL ID
        # ------------------------------------------------------

        if response == control_id:
            raise ValueError(
                "AI audit produced an invalid PTA Response: "
                "the response only contains the Control ID."
            )

        # ------------------------------------------------------
        # ALL THREE AI FIELDS ARE REQUIRED
        # ------------------------------------------------------

        missing_fields = []

        if not response:
            missing_fields.append(
                "PTA Response"
            )

        if not recommendation:
            missing_fields.append(
                "PTA Recommendation"
            )

        if not action_by:
            missing_fields.append(
                "Action By"
            )

        if missing_fields:
            raise ValueError(
                "AI audit did not generate all required fields: "
                + ", ".join(missing_fields)
            )

    # =========================================================
    # AUDIT CONTROL
    # =========================================================

    def audit_control(
        self,
        control_id: str,
        top_k: int = 5,
        max_new_tokens: int = 200,
    ) -> dict[str, Any]:

        if not control_id:
            raise ValueError(
                "Control ID cannot be empty."
            )

        # =====================================================
        # CONTROL
        # =====================================================

        control = self.control_service.get_control(
            control_id,
        )

        if control is None:
            raise ValueError(
                f"CTDISR control "
                f"'{control_id}' not found."
            )

        # =====================================================
        # RETRIEVE EVIDENCE
        # =====================================================

        context = self.context_builder.build(
            control=control,
            top_k=top_k,
        )

        # =====================================================
        # BUILD LLM CONTEXT
        # =====================================================

        llm_context = (
            self.context_builder.build_llm_context(
                context,
            )
        )

        # =====================================================
        # STATIC CONTROL INFORMATION
        # =====================================================

        control_name = str(
            control.get("control_id")
            or control.get("control")
            or control_id
        ).strip()

        description = str(
            control.get(
                "control_description",
                "",
            )
        ).strip()

        interpretation = str(
            control.get("interpretation")
            or control.get(
                "control_interpretation",
                "",
            )
        ).strip()

        # =====================================================
        # GENERATE WITH FINE-TUNED LLAMA
        # =====================================================

        llama = get_llama()

        raw_response = llama.generate_pta_audit(
            control=control_name,
            control_description=description,
            control_interpretation=interpretation,
            evidence=llm_context,
            max_new_tokens=max_new_tokens,
        )

        # =====================================================
        # PARSE
        # =====================================================

        parsed = self._parse_llm_response(
            raw_response
        )

        # =====================================================
        # VALIDATE
        # =====================================================

        self._validate_ai_output(
            parsed=parsed,
            control_id=control_name,
        )

        # =====================================================
        # FINAL RESULT
        # =====================================================

        return {
            # -------------------------------------------------
            # STATIC FIELDS
            # -------------------------------------------------

            "control_id": control_name,

            "control_level": control.get(
                "control_level",
                "",
            ),

            "control_description": description,

            "control_interpretation": interpretation,

            # -------------------------------------------------
            # AI-GENERATED FIELDS
            # -------------------------------------------------

            "pta_response": parsed[
                "pta_response"
            ],

            "pta_recommendation": parsed[
                "pta_recommendation"
            ],

            "action_by": parsed[
                "action_by"
            ],

            # -------------------------------------------------
            # EXISTING NTC COMMENTS
            # -------------------------------------------------

            "ntc_comments": control.get(
                "ntc_comments",
                "",
            ),

            # -------------------------------------------------
            # DEBUG / EVIDENCE
            # -------------------------------------------------

            "raw_ai_response": parsed[
                "raw_response"
            ],

            "evidence": context.get(
                "all_evidence",
                [],
            ),

            "evidence_count": context.get(
                "evidence_count",
                0,
            ),

            "evidence_counts": context.get(
                "evidence_counts",
                {
                    "ctdisr": 0,
                    "policy": 0,
                    "advisory": 0,
                    "asset": 0,
                },
            ),

            "retrieval_query": context.get(
                "query",
                "",
            ),
        }


# =========================================================
# SHARED PIPELINE
# =========================================================

_pipeline: AuditPipeline | None = None


def get_audit_pipeline() -> AuditPipeline:

    global _pipeline

    if _pipeline is None:
        _pipeline = AuditPipeline()

    return _pipeline