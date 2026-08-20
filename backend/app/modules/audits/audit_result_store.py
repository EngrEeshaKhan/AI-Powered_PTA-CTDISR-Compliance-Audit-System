from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[4]

AUDIT_STORAGE_DIR = (
    PROJECT_ROOT
    / "storage"
    / "audits"
)

AUDIT_RESULTS_FILE = (
    AUDIT_STORAGE_DIR
    / "audit_results.json"
)


# =========================================================
# TIME
# =========================================================

def utc_now() -> str:
    """
    Return the current UTC timestamp.
    """
    return datetime.now(
        timezone.utc
    ).isoformat()


# =========================================================
# STORAGE INITIALIZATION
# =========================================================

def _ensure_storage() -> None:
    """
    Ensure the audit storage directory and JSON file exist.
    """

    AUDIT_STORAGE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not AUDIT_RESULTS_FILE.exists():

        AUDIT_RESULTS_FILE.write_text(
            "[]",
            encoding="utf-8",
        )


# =========================================================
# LOAD RESULTS
# =========================================================

def _load_results() -> list[dict[str, Any]]:
    """
    Load all saved audit results.
    """

    _ensure_storage()

    content = (
        AUDIT_RESULTS_FILE
        .read_text(
            encoding="utf-8"
        )
        .strip()
    )

    if not content:
        return []

    try:

        data = json.loads(
            content
        )

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            "audit_results.json contains invalid JSON."
        ) from exc

    if not isinstance(
        data,
        list,
    ):

        raise RuntimeError(
            "audit_results.json must contain a JSON array."
        )

    return data


# =========================================================
# SAVE ALL RESULTS
# =========================================================

def _save_results(
    results: list[dict[str, Any]],
) -> None:
    """
    Persist all audit results to disk.
    """

    _ensure_storage()

    AUDIT_RESULTS_FILE.write_text(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


# =========================================================
# CREATE / SAVE NEW AI AUDIT
# =========================================================

def save_audit_result(
    audit_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Save a newly generated AI audit result.

    Static fields:
        - control_id
        - control_level
        - control_description
        - control_interpretation

    AI-generated fields:
        - pta_response
        - pta_recommendations
        - action_by

    Auditor field:
        - ntc_comments
    """

    results = _load_results()

    now = utc_now()

    record = {
        "audit_id": str(
            uuid4()
        ),

        "control_id": audit_result.get(
            "control_id",
            "",
        ),

        "control_level": audit_result.get(
            "control_level",
            "",
        ),

        "control_description": audit_result.get(
            "control_description",
            "",
        ),

        "control_interpretation": audit_result.get(
            "control_interpretation",
            "",
        ),

        "pta_response": audit_result.get(
            "pta_response",
            "",
        ),

        "pta_recommendations": audit_result.get(
            "pta_recommendation",
            audit_result.get(
                "pta_recommendations",
                "",
            ),
        ),

        "action_by": audit_result.get(
            "action_by",
            "",
        ),

        "ntc_comments": audit_result.get(
            "ntc_comments",
            "",
        ),

        "status": "draft",

        "version": "1.0",

        "created_at": now,

        "updated_at": now,
    }

    results.append(
        record
    )

    _save_results(
        results
    )

    return record


# =========================================================
# GET ALL AUDIT RESULTS
# =========================================================

def get_all_audit_results() -> list[dict[str, Any]]:
    """
    Return all saved audit results.
    """

    return _load_results()


# =========================================================
# GET ONE AUDIT RESULT
# =========================================================

def get_audit_result(
    audit_id: str,
) -> dict[str, Any] | None:
    """
    Return one audit result by audit_id.
    """

    results = _load_results()

    for result in results:

        if result.get(
            "audit_id"
        ) == audit_id:

            return result

    return None


# =========================================================
# UPDATE / SAVE EDITED AUDIT
# =========================================================

def update_audit_result(
    audit_id: str,
    updates: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Update an existing saved audit result.

    Editable fields:
        - pta_response
        - pta_recommendations
        - action_by
        - ntc_comments
        - status

    Static fields are intentionally NOT editable here:
        - control_id
        - control_level
        - control_description
        - control_interpretation

    Calling this function is the actual SAVE operation after edit.
    """

    results = _load_results()

    editable_fields = {
        "pta_response",
        "pta_recommendations",
        "action_by",
        "ntc_comments",
        "status",
    }

    for result in results:

        if result.get(
            "audit_id"
        ) != audit_id:

            continue

        for field, value in updates.items():

            if field not in editable_fields:
                continue

            if value is None:
                continue

            if isinstance(
                value,
                str,
            ):

                result[field] = value.strip()

            else:

                result[field] = value

        result["updated_at"] = utc_now()

        _save_results(
            results
        )

        return result

    return None


# =========================================================
# DELETE AUDIT RESULT
# =========================================================

def delete_audit_result(
    audit_id: str,
) -> bool:
    """
    Delete one saved audit result.
    """

    results = _load_results()

    original_count = len(
        results
    )

    remaining_results = [
        result
        for result in results
        if result.get(
            "audit_id"
        ) != audit_id
    ]

    if len(
        remaining_results
    ) == original_count:

        return False

    _save_results(
        remaining_results
    )

    return True