from __future__ import annotations

from typing import Any

from app.ai.retrieval.retriever import Retriever


class ContextBuilder:
    """
    Build evidence context for a single PTA CTDISR control.

    Flow:

        CTDISR Control
             ↓
        Build control-aware query
             ↓
        Retrieve evidence
             ↓
        Normalize evidence
             ↓
        Rank evidence
             ↓
        Build LLM context

    The LLM is NOT called here.
    """

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(
        self,
        retriever: Retriever | None = None,
    ) -> None:

        self.retriever = (
            retriever
            if retriever is not None
            else Retriever()
        )

    # =========================================================
    # BUILD QUERY
    # =========================================================

    def build_query(
        self,
        control: dict[str, Any],
    ) -> str:
        """
        Build a control-focused semantic query.

        The control ID, description and interpretation are all
        included so retrieval can locate both regulatory text
        and supporting organizational evidence.
        """

        control_id = str(
            control.get("control_id")
            or control.get("control")
            or ""
        ).strip()

        description = str(
            control.get(
                "control_description",
                "",
            )
            or ""
        ).strip()

        interpretation = str(
            control.get(
                "control_interpretation",
            )
            or control.get(
                "interpretation",
                "",
            )
            or ""
        ).strip()

        parts: list[str] = []

        if control_id:

            parts.append(
                f"CTDISR Control: {control_id}"
            )

        if description:

            parts.append(
                f"Control Description: {description}"
            )

        if interpretation:

            parts.append(
                f"Control Interpretation: {interpretation}"
            )

        return "\n".join(
            parts
        ).strip()

    # =========================================================
    # FORMAT RESULT
    # =========================================================

    @staticmethod
    def _format_result(
        result: dict[str, Any],
    ) -> dict[str, Any]:

        metadata = (
            result.get(
                "metadata"
            )
            or {}
        )

        return {
            "score": float(
                result.get(
                    "score",
                    0.0,
                )
            ),
            "document_type": metadata.get(
                "document_type"
            ),
            "file_name": metadata.get(
                "file_name"
            ),
            "file_path": metadata.get(
                "file_path"
            ),
            "chunk_index": metadata.get(
                "chunk_index"
            ),
            "section_index": metadata.get(
                "section_index"
            ),
            "chunk_key": metadata.get(
                "chunk_key"
            ),
            "text": str(
                metadata.get(
                    "text",
                    "",
                )
            ).strip(),
        }

    # =========================================================
    # SORT
    # =========================================================

    @staticmethod
    def _sort_by_score(
        results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        return sorted(
            results,
            key=lambda item: float(
                item.get(
                    "score",
                    0.0,
                )
            ),
            reverse=True,
        )

    # =========================================================
    # BUILD
    # =========================================================

    def build(
        self,
        control: dict[str, Any],
        top_k: int = 5,
    ) -> dict[str, Any]:
        """
        Retrieve evidence independently from:

            CTDISR
            Policy
            Advisory
            Asset

        This maintains balanced evidence coverage.
        """

        if not control:

            raise ValueError(
                "Control cannot be empty."
            )

        # -----------------------------------------------------
        # QUERY
        # -----------------------------------------------------

        query = self.build_query(
            control
        )

        if not query:

            raise ValueError(
                "CTDISR control does not contain enough "
                "information for retrieval."
            )

        # -----------------------------------------------------
        # RETRIEVE
        # -----------------------------------------------------

        ctdisr_results = (
            self.retriever.search_ctdisr(
                query=query,
                top_k=top_k,
            )
        )

        policy_results = (
            self.retriever.search_policies(
                query=query,
                top_k=top_k,
            )
        )

        advisory_results = (
            self.retriever.search_advisories(
                query=query,
                top_k=top_k,
            )
        )

        asset_results = (
            self.retriever.search_assets(
                query=query,
                top_k=top_k,
            )
        )

        # -----------------------------------------------------
        # NORMALIZE
        # -----------------------------------------------------

        ctdisr_evidence = self._sort_by_score(
            [
                self._format_result(
                    result
                )
                for result in ctdisr_results
            ]
        )

        policy_evidence = self._sort_by_score(
            [
                self._format_result(
                    result
                )
                for result in policy_results
            ]
        )

        advisory_evidence = self._sort_by_score(
            [
                self._format_result(
                    result
                )
                for result in advisory_results
            ]
        )

        asset_evidence = self._sort_by_score(
            [
                self._format_result(
                    result
                )
                for result in asset_results
            ]
        )

        # -----------------------------------------------------
        # COMBINE
        # -----------------------------------------------------

        all_evidence = (
            ctdisr_evidence
            + policy_evidence
            + advisory_evidence
            + asset_evidence
        )

        all_evidence = self._sort_by_score(
            all_evidence
        )

        # -----------------------------------------------------
        # RETURN
        # -----------------------------------------------------

        return {
            "control": control,
            "query": query,

            "ctdisr_evidence": ctdisr_evidence,
            "policy_evidence": policy_evidence,
            "advisory_evidence": advisory_evidence,
            "asset_evidence": asset_evidence,

            "all_evidence": all_evidence,

            "evidence_count": len(
                all_evidence
            ),

            "evidence_counts": {
                "ctdisr": len(
                    ctdisr_evidence
                ),
                "policy": len(
                    policy_evidence
                ),
                "advisory": len(
                    advisory_evidence
                ),
                "asset": len(
                    asset_evidence
                ),
            },
        }

    # =========================================================
    # BUILD LLM CONTEXT
    # =========================================================

    def build_llm_context(
        self,
        context: dict[str, Any],
    ) -> str:
        """
        Convert structured evidence into a strict evidence
        context for the fine-tuned Llama model.

        The model is explicitly told that retrieved evidence
        may be relevant without proving compliance.
        """

        control = context.get(
            "control",
            {},
        )

        control_id = (
            control.get(
                "control_id"
            )
            or control.get(
                "control"
            )
            or ""
        )

        description = (
            control.get(
                "control_description",
                "",
            )
            or ""
        )

        interpretation = (
            control.get(
                "control_interpretation"
            )
            or control.get(
                "interpretation",
                "",
            )
            or ""
        )

        lines: list[str] = []

        # =====================================================
        # AUDIT CONTROL
        # =====================================================

        lines.append(
            "=== AUDIT CONTROL ==="
        )

        lines.append(
            f"Control ID: {control_id}"
        )

        lines.append(
            f"Control Description: {description}"
        )

        lines.append(
            f"Control Interpretation: {interpretation}"
        )

        # =====================================================
        # EVIDENCE RULES
        # =====================================================

        lines.append("")

        lines.append(
            "=== EVIDENCE USE RULES ==="
        )

        lines.append(
            "Retrieved evidence is supporting information, "
            "not automatic proof of compliance."
        )

        lines.append(
            "Do not infer that an organization has implemented "
            "a control merely because a policy mentions a "
            "committee, process, role, system, or requirement."
        )

        lines.append(
            "Distinguish between evidence that establishes "
            "implementation and evidence that merely describes "
            "a requirement or concept."
        )

        lines.append(
            "If the supplied evidence does not establish "
            "compliance or non-compliance, explicitly state:"
        )

        lines.append(
            '"Evidence is insufficient to establish compliance."'
        )

        # =====================================================
        # EVIDENCE GROUPS
        # =====================================================

        evidence_groups = [
            (
                "CTDISR EVIDENCE",
                context.get(
                    "ctdisr_evidence",
                    [],
                ),
            ),
            (
                "POLICY EVIDENCE",
                context.get(
                    "policy_evidence",
                    [],
                ),
            ),
            (
                "ADVISORY EVIDENCE",
                context.get(
                    "advisory_evidence",
                    [],
                ),
            ),
            (
                "ASSET EVIDENCE",
                context.get(
                    "asset_evidence",
                    [],
                ),
            ),
        ]

        evidence_number = 1

        for title, evidence in evidence_groups:

            lines.append("")

            lines.append(
                f"=== {title} ==="
            )

            if not evidence:

                lines.append(
                    "No relevant evidence retrieved."
                )

                continue

            for item in evidence:

                lines.append("")

                lines.append(
                    f"[Evidence {evidence_number}]"
                )

                evidence_number += 1

                lines.append(
                    f"Source: "
                    f"{item.get('file_name') or 'Unknown'}"
                )

                lines.append(
                    f"Document Type: "
                    f"{item.get('document_type') or 'Unknown'}"
                )

                lines.append(
                    f"Similarity: "
                    f"{float(item.get('score', 0.0)):.4f}"
                )

                if item.get(
                    "chunk_index"
                ) is not None:

                    lines.append(
                        f"Chunk: "
                        f"{item.get('chunk_index')}"
                    )

                lines.append(
                    "Content:"
                )

                text = str(
                    item.get(
                        "text",
                        "",
                    )
                ).strip()

                lines.append(
                    text
                    if text
                    else "No text available."
                )

        return "\n".join(
            lines
        ).strip()