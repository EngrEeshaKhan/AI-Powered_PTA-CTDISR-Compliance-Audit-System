from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.ai.processing.document_processor import DocumentProcessor

from app.core.auth import CurrentUser
from app.core.dependencies import require_admin

from app.modules.uploads.service import (
    DocumentCategory,
    save_uploaded_file,
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)


# =========================================================
# UPLOAD DOCUMENT
# =========================================================

@router.post(
    "/",
    summary="Upload and process document",
)
async def upload_document(
    category: DocumentCategory = Form(...),
    file: UploadFile = File(...),

    # -----------------------------------------------------
    # ADMIN ONLY
    # -----------------------------------------------------
    current_user: CurrentUser = Depends(
        require_admin
    ),
):
    """
    Upload and automatically process a document.

    Admin only.

    Workflow:

        Upload
          ↓
        Validate
          ↓
        Save original document
          ↓
        Register document
          ↓
        Process document
          ↓
        Chunk
          ↓
        Embed
          ↓
        Update vector store
    """

    # =====================================================
    # 1. SAVE DOCUMENT
    # =====================================================

    try:

        upload_result = await save_uploaded_file(
            file=file,
            category=category,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except FileExistsError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to upload document: "
                f"{exc}"
            ),
        )

    # =====================================================
    # 2. DOCUMENT INFORMATION
    # =====================================================

    document_id = upload_result["document_id"]
    file_path = upload_result["file_path"]
    document_category = upload_result["category"]
    file_name = upload_result["file_name"]

    # =====================================================
    # 3. PROCESS DOCUMENT
    # =====================================================

    try:

        print()
        print("=" * 70)
        print("AUTOMATIC DOCUMENT PROCESSING")
        print("=" * 70)

        print(
            f"Document ID : {document_id}"
        )

        print(
            f"File        : {file_name}"
        )

        print(
            f"Category    : {document_category}"
        )

        print(
            f"Path        : {file_path}"
        )

        print("=" * 70)

        processor = DocumentProcessor()

        processing_result = processor.process(
            file_path=file_path,
            document_type=document_category,
        )

    # =====================================================
    # PROCESSING ERRORS
    # =====================================================

    except FileNotFoundError as exc:

        return {
            "success": False,
            "message": (
                "Document was uploaded successfully, "
                "but processing failed because the "
                "file could not be found."
            ),
            "document_id": document_id,
            "file_name": file_name,
            "category": document_category,
            "file_path": file_path,
            "status": "processing_failed",
            "error": str(exc),
        }

    except ValueError as exc:

        return {
            "success": False,
            "message": (
                "Document was uploaded successfully, "
                "but processing failed."
            ),
            "document_id": document_id,
            "file_name": file_name,
            "category": document_category,
            "file_path": file_path,
            "status": "processing_failed",
            "error": str(exc),
        }

    except Exception as exc:

        return {
            "success": False,
            "message": (
                "Document was uploaded successfully, "
                "but processing failed during "
                "chunking, embedding, or vector storage."
            ),
            "document_id": document_id,
            "file_name": file_name,
            "category": document_category,
            "file_path": file_path,
            "status": "processing_failed",
            "error": str(exc),
        }

    # =====================================================
    # 4. PROCESSING RESULT
    # =====================================================

    if not processing_result.get(
        "success",
        False,
    ):

        return {
            "success": False,
            "message": (
                "Document was uploaded successfully, "
                "but processing did not complete."
            ),
            "document_id": document_id,
            "file_name": file_name,
            "category": document_category,
            "file_path": file_path,
            "status": "processing_failed",
            "processing": processing_result,
        }

    # =====================================================
    # 5. SUCCESS
    # =====================================================

    return {
        "success": True,
        "message": (
            "Document uploaded and processed "
            "successfully."
        ),
        "document_id": document_id,
        "file_name": file_name,
        "category": document_category,
        "file_path": file_path,
        "status": "processed",
        "processing": processing_result,
    }