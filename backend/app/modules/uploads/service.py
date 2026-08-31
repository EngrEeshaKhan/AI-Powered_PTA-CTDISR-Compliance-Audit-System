from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from fastapi import UploadFile


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[4]

DOCUMENT_ROOT = (
    PROJECT_ROOT
    / "storage"
    / "documents"
)

REGISTRY_FILE = (
    DOCUMENT_ROOT
    / "document_registry.json"
)


# =========================================================
# DOCUMENT CATEGORIES
# =========================================================

class DocumentCategory(str, Enum):
    ADVISORY = "advisory"
    POLICY = "policy"
    CTDISR = "ctdisr"
    ASSET = "asset"


# =========================================================
# CATEGORY DIRECTORIES
# =========================================================

CATEGORY_DIRECTORIES = {
    DocumentCategory.ADVISORY: "advisories",
    DocumentCategory.POLICY: "policies",
    DocumentCategory.CTDISR: "ctdisr",
    DocumentCategory.ASSET: "assets",
}


# =========================================================
# ALLOWED FILE TYPES
# =========================================================

ALLOWED_EXTENSIONS = {
    DocumentCategory.ADVISORY: {
        ".pdf",
        ".docx",
        ".doc",
    },

    DocumentCategory.POLICY: {
        ".pdf",
        ".docx",
        ".doc",
    },

    DocumentCategory.CTDISR: {
        ".pdf",
        ".docx",
        ".doc",
    },

    DocumentCategory.ASSET: {
        ".xlsx",
        ".xls",
    },
}


# =========================================================
# CATEGORY DIRECTORY
# =========================================================

def get_category_directory(
    category: DocumentCategory,
) -> Path:
    """
    Return the permanent storage directory
    for the selected category.
    """

    directory_name = CATEGORY_DIRECTORIES[category]

    directory = (
        DOCUMENT_ROOT
        / directory_name
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return directory


# =========================================================
# FILE VALIDATION
# =========================================================

def validate_file_extension(
    filename: str,
    category: DocumentCategory,
) -> None:
    """
    Validate that the uploaded file extension
    is allowed for the selected category.
    """

    extension = (
        Path(filename)
        .suffix
        .lower()
    )

    allowed_extensions = (
        ALLOWED_EXTENSIONS[category]
    )

    if extension not in allowed_extensions:

        allowed_text = ", ".join(
            sorted(allowed_extensions)
        )

        raise ValueError(
            f"File type '{extension}' is not allowed "
            f"for category '{category.value}'. "
            f"Allowed types: {allowed_text}"
        )


# =========================================================
# DOCUMENT ID
# =========================================================

def create_document_id(
    category: DocumentCategory,
    filename: str,
) -> str:
    """
    Create a stable document ID from category + filename.
    """

    value = (
        f"{category.value}:{filename}"
    )

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()[:24]


# =========================================================
# REGISTRY
# =========================================================

def _ensure_registry() -> None:
    """
    Ensure the document registry exists.
    """

    DOCUMENT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not REGISTRY_FILE.exists():

        REGISTRY_FILE.write_text(
            "{}",
            encoding="utf-8",
        )


def _load_registry() -> dict[str, Any]:
    """
    Load the persistent uploaded-document registry.
    """

    _ensure_registry()

    try:

        with REGISTRY_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

    except json.JSONDecodeError:

        data = {}

    if not isinstance(data, dict):

        data = {}

    return data


def _save_registry(
    registry: dict[str, Any],
) -> None:
    """
    Save the persistent uploaded-document registry.
    """

    DOCUMENT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = (
        REGISTRY_FILE.with_suffix(".tmp")
    )

    with temporary_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            registry,
            file,
            indent=2,
            ensure_ascii=False,
        )

    temporary_file.replace(
        REGISTRY_FILE
    )


# =========================================================
# REGISTER DOCUMENT
# =========================================================

def register_document(
    document_id: str,
    file_name: str,
    category: DocumentCategory,
    file_path: Path,
) -> None:
    """
    Persist complete document metadata.
    """

    registry = _load_registry()

    file_size = (
        file_path.stat().st_size
        if file_path.exists()
        else 0
    )

    registry[document_id] = {
        "document_id": document_id,
        "file_name": file_name,
        "category": category.value,
        "file_path": str(file_path),
        "extension": file_path.suffix.lower(),
        "file_size": file_size,
        "uploaded_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "uploaded",
    }

    _save_registry(
        registry
    )


# =========================================================
# GET DOCUMENT
# =========================================================

def get_document(
    document_id: str,
) -> dict[str, Any] | None:
    """
    Retrieve an uploaded document from the registry.
    """

    registry = _load_registry()

    return registry.get(
        document_id
    )


# =========================================================
# LIST DOCUMENTS
# =========================================================

def list_documents() -> list[dict[str, Any]]:
    """
    Return all registered documents.
    """

    registry = _load_registry()

    return list(
        registry.values()
    )


# =========================================================
# UPDATE DOCUMENT STATUS
# =========================================================

def update_document_status(
    document_id: str,
    status: str,
) -> dict[str, Any] | None:
    """
    Update the processing status of a
    registered document.
    """

    registry = _load_registry()

    document = registry.get(
        document_id
    )

    if document is None:
        return None

    document["status"] = status

    registry[document_id] = document

    _save_registry(
        registry
    )

    return document


# =========================================================
# DELETE DOCUMENT
# =========================================================

def delete_document(
    document_id: str,
) -> dict[str, Any] | None:
    """
    Delete a document from physical storage
    and remove its registry entry.

    NOTE:
    Vector-index cleanup must be handled separately
    before this becomes the final production delete flow.
    """

    registry = _load_registry()

    document = registry.get(
        document_id
    )

    if document is None:
        return None

    file_path = Path(
        document["file_path"]
    )

    if file_path.exists():

        file_path.unlink()

    del registry[
        document_id
    ]

    _save_registry(
        registry
    )

    return document


# =========================================================
# SAVE UPLOADED FILE
# =========================================================

async def save_uploaded_file(
    file: UploadFile,
    category: DocumentCategory,
) -> dict[str, Any]:
    """
    Validate and permanently save an uploaded document.

    This function performs:

        Upload
        ↓
        Validation
        ↓
        Category storage
        ↓
        Registry registration

    It does NOT:

        - chunk
        - embed
        - create vectors
        - modify FAISS
    """

    # -----------------------------------------------------
    # 1. VALIDATE FILENAME
    # -----------------------------------------------------

    filename = (
        file.filename or ""
    ).strip()

    if not filename:

        raise ValueError(
            "Uploaded file must have a filename."
        )

    # -----------------------------------------------------
    # 2. REMOVE DIRECTORY TRAVERSAL
    # -----------------------------------------------------

    safe_filename = Path(
        filename
    ).name

    if not safe_filename:

        raise ValueError(
            "Invalid uploaded filename."
        )

    # -----------------------------------------------------
    # 3. VALIDATE EXTENSION
    # -----------------------------------------------------

    validate_file_extension(
        safe_filename,
        category,
    )

    # -----------------------------------------------------
    # 4. GET CATEGORY DIRECTORY
    # -----------------------------------------------------

    directory = get_category_directory(
        category
    )

    # -----------------------------------------------------
    # 5. CREATE DOCUMENT ID
    # -----------------------------------------------------

    document_id = create_document_id(
        category=category,
        filename=safe_filename,
    )

    # -----------------------------------------------------
    # 6. FINAL FILE PATH
    # -----------------------------------------------------

    destination = (
        directory
        / safe_filename
    )

    # -----------------------------------------------------
    # 7. DO NOT OVERWRITE
    # -----------------------------------------------------

    if destination.exists():

        raise FileExistsError(
            "A file with the same name already "
            f"exists in the {category.value} category: "
            f"{safe_filename}"
        )

    # -----------------------------------------------------
    # 8. SAVE FILE
    # -----------------------------------------------------

    try:

        with destination.open(
            "wb"
        ) as output:

            while True:

                data = await file.read(
                    1024 * 1024
                )

                if not data:
                    break

                output.write(data)

    except Exception:

        if destination.exists():
            destination.unlink()

        raise

    # -----------------------------------------------------
    # 9. REGISTER DOCUMENT
    # -----------------------------------------------------

    register_document(
        document_id=document_id,
        file_name=safe_filename,
        category=category,
        file_path=destination,
    )

    # -----------------------------------------------------
    # 10. RETURN DOCUMENT INFORMATION
    # -----------------------------------------------------

    document = get_document(
        document_id
    )

    return document or {
        "document_id": document_id,
        "file_name": safe_filename,
        "category": category.value,
        "file_path": str(destination),
        "extension": destination.suffix.lower(),
        "file_size": destination.stat().st_size,
        "uploaded_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "uploaded",
    }