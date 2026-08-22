from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# PROJECT PATHS
# ============================================================

# dashboard.py
#   backend/
#       app/
#           api/
#               v1/
#                   dashboard.py
#
# parents[0] = v1
# parents[1] = api
# parents[2] = app
# parents[3] = backend
#
# The actual storage directory is at:
#
# project_root/
#     storage/
#
# Therefore we go four levels up from this file.

PROJECT_ROOT = Path(__file__).resolve().parents[4]

STORAGE_PATH = PROJECT_ROOT / "storage"

DOCUMENTS_PATH = STORAGE_PATH / "documents"

DOCUMENT_REGISTRY_PATH = (
    DOCUMENTS_PATH / "document_registry.json"
)

CTDISR_CONTROLS_PATH = (
    STORAGE_PATH / "ctdisr" / "controls.json"
)

AUDIT_RESULTS_PATH = (
    STORAGE_PATH / "audits" / "audit_results.json"
)


# ============================================================
# GENERIC JSON LOADER
# ============================================================

def _load_json_file(
    path: Path,
    default: Any,
) -> Any:
    """
    Safely load a JSON file.

    Returns default when:
    - file does not exist
    - file is empty
    - JSON is invalid
    """

    if not path.exists():
        return default

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return default


# ============================================================
# DOCUMENT STATISTICS
# ============================================================

def _count_files_in_directory(
    directory: Path,
    extensions: set[str] | None = None,
) -> int:
    """
    Count physical files in a directory.

    Only direct files are counted.
    Subdirectories such as 'archive' are ignored.
    """

    if not directory.exists():
        return 0

    count = 0

    for path in directory.iterdir():

        if not path.is_file():
            continue

        if extensions is not None:
            if path.suffix.lower() not in extensions:
                continue

        count += 1

    return count


def _document_statistics() -> dict[str, int]:
    """
    Calculate dashboard document statistics from the
    actual persistent document storage.

    This intentionally does NOT use document_registry.json
    because the registry currently contains only documents
    uploaded through/testing the upload endpoint.

    Existing Knowledge Base files are already physically
    stored under:

        storage/documents/advisories
        storage/documents/policies
        storage/documents/ctdisr
        storage/documents/assets
    """

    advisories_path = (
        DOCUMENTS_PATH / "advisories"
    )

    policies_path = (
        DOCUMENTS_PATH / "policies"
    )

    ctdisr_path = (
        DOCUMENTS_PATH / "ctdisr"
    )

    assets_path = (
        DOCUMENTS_PATH / "assets"
    )

    # Supported document extensions.
    document_extensions = {
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
    }

    advisories = _count_files_in_directory(
        advisories_path,
        document_extensions,
    )

    policies = _count_files_in_directory(
        policies_path,
        document_extensions,
    )

    ctdisr = _count_files_in_directory(
        ctdisr_path,
        document_extensions,
    )

    assets = _count_files_in_directory(
        assets_path,
        document_extensions,
    )

    total = (
        advisories
        + policies
        + ctdisr
        + assets
    )

    return {
        "total": total,
        "policies": policies,
        "advisories": advisories,
        "ctdisr": ctdisr,
        "assets": assets,
    }


# ============================================================
# CTDISR CONTROL STATISTICS
# ============================================================

def _load_ctdisr_controls() -> Any:
    """Load the persistent CTDISR controls."""

    return _load_json_file(
        CTDISR_CONTROLS_PATH,
        default=[],
    )


def _normalise_controls(
    data: Any,
) -> list[dict[str, Any]]:
    """
    Convert different possible control JSON formats
    into a predictable list.
    """

    # Standard format:
    #
    # [
    #     {...},
    #     {...}
    # ]

    if isinstance(data, list):

        return [
            item
            for item in data
            if isinstance(item, dict)
        ]

    # Alternative format:
    #
    # {
    #     "controls": [...]
    # }

    if isinstance(data, dict):

        controls = data.get("controls")

        if isinstance(controls, list):

            return [
                item
                for item in controls
                if isinstance(item, dict)
            ]

        # Dictionary-style control storage.
        #
        # {
        #     "3.1": {...},
        #     "4.1": {...}
        # }

        result: list[dict[str, Any]] = []

        for control_id, control in data.items():

            if isinstance(control, dict):

                item = dict(control)

                item.setdefault(
                    "control_id",
                    control_id,
                )

                result.append(item)

        return result

    return []


def _get_control_status(
    control: dict[str, Any],
) -> str:
    """
    Read the status of a CTDISR control.
    """

    status = control.get("status")

    if status is None:
        status = control.get("control_status")

    if status is None:
        status = control.get("state")

    if status is None:
        return ""

    return str(status).strip().lower()


def _control_statistics() -> dict[str, int]:
    """
    Calculate live CTDISR control statistics from
    storage/ctdisr/controls.json.
    """

    data = _load_ctdisr_controls()

    controls = _normalise_controls(data)

    statistics = {
        "total": len(controls),
        "active": 0,
        "inactive": 0,
    }

    for control in controls:

        status = _get_control_status(control)

        if status == "active":
            statistics["active"] += 1

        elif status in {
            "inactive",
            "disabled",
            "deactivated",
        }:
            statistics["inactive"] += 1

    return statistics


# ============================================================
# AUDIT STATISTICS
# ============================================================

def _load_audit_results() -> Any:
    """Load saved audit results."""

    return _load_json_file(
        AUDIT_RESULTS_PATH,
        default=[],
    )


def _normalise_audits(
    data: Any,
) -> list[dict[str, Any]]:
    """
    Convert different possible audit JSON structures
    into a predictable list.
    """

    # Standard list:
    #
    # [
    #     {...},
    #     {...}
    # ]

    if isinstance(data, list):

        return [
            item
            for item in data
            if isinstance(item, dict)
        ]

    if isinstance(data, dict):

        audits = data.get("audits")

        if isinstance(audits, list):

            return [
                item
                for item in audits
                if isinstance(item, dict)
            ]

        # Dictionary-style audit storage.

        result: list[dict[str, Any]] = []

        for audit_id, audit in data.items():

            if isinstance(audit, dict):

                item = dict(audit)

                item.setdefault(
                    "audit_id",
                    audit_id,
                )

                result.append(item)

        return result

    return []


def _get_audit_status(
    audit: dict[str, Any],
) -> str:
    """
    Read the audit status.

    Supports the existing JSON structures.
    """

    status = audit.get("status")

    if status is None:
        status = audit.get("audit_status")

    if status is None:
        status = audit.get("state")

    if status is None:
        return ""

    return str(status).strip().lower()


def _audit_statistics(
    audits: list[dict[str, Any]],
) -> dict[str, int]:
    """
    Calculate live audit statistics.
    """

    statistics = {
        "total": len(audits),
        "draft": 0,
        "generated": 0,
        "reviewed": 0,
        "finalized": 0,
    }

    for audit in audits:

        status = _get_audit_status(audit)

        if status == "draft":
            statistics["draft"] += 1

        elif status == "generated":
            statistics["generated"] += 1

        elif status == "reviewed":
            statistics["reviewed"] += 1

        elif status == "finalized":
            statistics["finalized"] += 1

    return statistics


# ============================================================
# DASHBOARD STATISTICS ENDPOINT
# ============================================================

@router.get(
    "/statistics",
    summary="Get dashboard statistics",
)
def get_dashboard_statistics() -> dict[str, Any]:
    """
    Return live dashboard statistics.

    Sources:

    Documents
        storage/documents/

    CTDISR controls
        storage/ctdisr/controls.json

    Audits
        storage/audits/audit_results.json

    The vector index is intentionally NOT used for document
    counting because vector records represent chunks rather
    than original documents.
    """

    try:

        # ----------------------------------------------------
        # DOCUMENTS
        # ----------------------------------------------------

        document_stats = _document_statistics()

        # ----------------------------------------------------
        # CTDISR CONTROLS
        # ----------------------------------------------------

        control_stats = _control_statistics()

        # ----------------------------------------------------
        # AUDITS
        # ----------------------------------------------------

        audit_data = _load_audit_results()

        audits = _normalise_audits(
            audit_data
        )

        audit_stats = _audit_statistics(
            audits
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {
            "success": True,

            "documents": document_stats,

            "controls": control_stats,

            "audits": audit_stats,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to load dashboard statistics: "
                f"{exc}"
            ),
        ) from exc