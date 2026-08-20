from __future__ import annotations

import re
from typing import Any

from app.ai.embeddings.embedding_model import generate_embeddings
from app.ai.vectorstore.index_manager import IndexManager


class Retriever:
    """
    Semantic + control-aware retrieval engine for the
    PTA CTDISR Compliance Audit System.

    Retrieval flow:

        CTDISR control
              ↓
        semantic query
              ↓
        embedding
              ↓
        FAISS candidate retrieval
              ↓
        metadata/text quality filtering
              ↓
        CTDISR control relevance boosting
              ↓
        final evidence ranking

    The purpose of this class is to avoid returning generic
    document headings/table headers when actual control evidence
    is available.
    """

    # =========================================================
    # GENERIC NOISE PHRASES
    # =========================================================

    NOISE_PHRASES = (
        "controls control level ctdisr control description",
        "control level ctdisr control description interpretation",
        "compensating control supporting documents",
    )

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(
        self,
        index_manager: IndexManager | None = None,
    ) -> None:

        self.index_manager = (
            index_manager
            if index_manager is not None
            else IndexManager()
        )

    # =========================================================
    # TEXT NORMALIZATION
    # =========================================================

    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normalize text for relevance checks.
        """

        text = str(text or "").lower()

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # =========================================================
    # CONTROL ID EXTRACTION
    # =========================================================

    @staticmethod
    def _extract_control_id(
        query: str,
    ) -> str | None:
        """
        Extract a CTDISR control identifier such as:

            4.1
            4.1.1
            11.3
            15.2

        from the retrieval query.
        """

        match = re.search(
            r"(?:ctdisr\s+control\s*:?\s*)"
            r"([0-9]+(?:\.[0-9]+)+)",
            query,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(1)

        # Fallback for a query that simply contains 4.1
        match = re.search(
            r"\b([0-9]+\.[0-9]+(?:\.[0-9]+)?)\b",
            query,
        )

        if match:
            return match.group(1)

        return None

    # =========================================================
    # NOISE DETECTION
    # =========================================================

    @classmethod
    def _is_noise_result(
        cls,
        result: dict[str, Any],
    ) -> bool:
        """
        Detect generic table headers / useless chunks.

        These chunks often receive surprisingly high semantic
        similarity because they contain CTDISR terminology.
        """

        metadata = result.get(
            "metadata"
        ) or {}

        text = cls._normalize_text(
            metadata.get("text", "")
        )

        if not text:
            return True

        # -----------------------------------------------------
        # Very short chunks
        # -----------------------------------------------------

        words = text.split()

        if len(words) < 8:
            return True

        # -----------------------------------------------------
        # Known CTDISR table headers
        # -----------------------------------------------------

        for phrase in cls.NOISE_PHRASES:

            if phrase in text:
                return True

        # -----------------------------------------------------
        # Generic heading-only chunks
        # -----------------------------------------------------

        heading_patterns = (
            r"^controls?\s+control\s+level",
            r"^control\s+level\s+ctdisr",
            r"^compensating\s+control",
            r"^supporting\s+documents$",
        )

        for pattern in heading_patterns:

            if re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            ):
                return True

        return False

    # =========================================================
    # CONTROL RELEVANCE SCORE
    # =========================================================

    @classmethod
    def _control_relevance_bonus(
        cls,
        result: dict[str, Any],
        control_id: str | None,
    ) -> float:
        """
        Give a modest ranking bonus to evidence that explicitly
        refers to the requested CTDISR control.

        This is intentionally a bonus rather than a replacement
        for semantic similarity.
        """

        if not control_id:
            return 0.0

        metadata = result.get(
            "metadata"
        ) or {}

        text = cls._normalize_text(
            metadata.get("text", "")
        )

        if not text:
            return 0.0

        normalized_control = (
            control_id.lower().strip()
        )

        # -----------------------------------------------------
        # Exact control ID
        # -----------------------------------------------------

        if re.search(
            rf"(?<!\d){re.escape(normalized_control)}(?!\d)",
            text,
        ):
            return 0.12

        return 0.0

    # =========================================================
    # RESULT QUALITY SCORE
    # =========================================================

    @classmethod
    def _quality_score(
        cls,
        result: dict[str, Any],
        control_id: str | None = None,
    ) -> float:
        """
        Calculate final retrieval score.

        Base:
            FAISS similarity

        Adjustments:
            + control ID match
            - generic/noisy content
        """

        try:

            score = float(
                result.get(
                    "score",
                    0.0,
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            score = 0.0

        # -----------------------------------------------------
        # Control-specific bonus
        # -----------------------------------------------------

        score += cls._control_relevance_bonus(
            result,
            control_id,
        )

        # -----------------------------------------------------
        # Noise penalty
        # -----------------------------------------------------

        if cls._is_noise_result(result):

            score -= 0.25

        return score

    # =========================================================
    # INTERNAL SEARCH
    # =========================================================

    def _search(
        self,
        query: str,
        top_k: int = 10,
        document_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search the FAISS knowledge base.

        A larger candidate pool is retrieved first. Candidates
        are then filtered and re-ranked before returning the
        final evidence.
        """

        if not query or not query.strip():

            return []

        query = query.strip()

        # -----------------------------------------------------
        # QUERY EMBEDDING
        # -----------------------------------------------------

        embeddings = generate_embeddings(
            [query],
            batch_size=1,
        )

        if not embeddings:

            return []

        query_embedding = embeddings[0]

        # -----------------------------------------------------
        # CONTROL ID
        # -----------------------------------------------------

        control_id = self._extract_control_id(
            query
        )

        # -----------------------------------------------------
        # CANDIDATE POOL
        # -----------------------------------------------------

        if document_type:

            search_k = max(
                top_k * 10,
                50,
            )

        else:

            search_k = max(
                top_k * 5,
                25,
            )

        # -----------------------------------------------------
        # FAISS SEARCH
        # -----------------------------------------------------

        results = (
            self.index_manager
            .vector_manager
            .search(
                query_embedding=query_embedding,
                top_k=search_k,
            )
        )

        if not results:

            return []

        # -----------------------------------------------------
        # DOCUMENT TYPE FILTER
        # -----------------------------------------------------

        if document_type:

            expected_type = (
                document_type
                .strip()
                .lower()
            )

            results = [
                result
                for result in results
                if str(
                    (
                        result.get(
                            "metadata"
                        )
                        or {}
                    ).get(
                        "document_type",
                        "",
                    )
                )
                .strip()
                .lower()
                == expected_type
            ]

        # -----------------------------------------------------
        # REMOVE EMPTY / OBVIOUS NOISE
        # -----------------------------------------------------

        cleaned_results = []

        for result in results:

            metadata = (
                result.get(
                    "metadata"
                )
                or {}
            )

            text = str(
                metadata.get(
                    "text",
                    "",
                )
            ).strip()

            if not text:
                continue

            cleaned_results.append(
                result
            )

        # -----------------------------------------------------
        # RE-RANK
        # -----------------------------------------------------

        ranked_results = sorted(
            cleaned_results,
            key=lambda result: (
                self._quality_score(
                    result,
                    control_id,
                )
            ),
            reverse=True,
        )

        # -----------------------------------------------------
        # FINAL FILTER
        # -----------------------------------------------------

        final_results = []

        for result in ranked_results:

            # Don't return obvious table-header noise
            # when we have enough real evidence.
            if self._is_noise_result(result):
                continue

            final_results.append(
                result
            )

            if len(final_results) >= top_k:
                break

        # -----------------------------------------------------
        # FALLBACK
        # -----------------------------------------------------

        # If filtering removed everything, return the best
        # original candidates rather than returning nothing.
        if not final_results:

            fallback = []

            for result in ranked_results:

                fallback.append(
                    result
                )

                if len(fallback) >= top_k:
                    break

            return fallback

        return final_results

    # =========================================================
    # SEARCH ALL
    # =========================================================

    def search_all(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:

        return self._search(
            query=query,
            top_k=top_k,
            document_type=None,
        )

    # =========================================================
    # GENERIC SEARCH
    # =========================================================

    def search(
        self,
        query: str,
        top_k: int = 10,
        document_type: str | None = None,
    ) -> list[dict[str, Any]]:

        return self._search(
            query=query,
            top_k=top_k,
            document_type=document_type,
        )

    # =========================================================
    # POLICY
    # =========================================================

    def search_policies(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:

        return self._search(
            query=query,
            top_k=top_k,
            document_type="policy",
        )

    # =========================================================
    # ADVISORY
    # =========================================================

    def search_advisories(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:

        return self._search(
            query=query,
            top_k=top_k,
            document_type="advisory",
        )

    # =========================================================
    # CTDISR
    # =========================================================

    def search_ctdisr(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:

        return self._search(
            query=query,
            top_k=top_k,
            document_type="ctdisr",
        )

    # =========================================================
    # ASSETS
    # =========================================================

    def search_assets(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:

        return self._search(
            query=query,
            top_k=top_k,
            document_type="asset",
        )