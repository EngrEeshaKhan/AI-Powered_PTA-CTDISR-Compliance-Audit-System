from __future__ import annotations

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.ai.processing.document_processor import (
    DocumentProcessor,
)

from app.modules.uploads.service import (
    DocumentCategory,
    delete_document,
    get_document,
    list_documents,
    save_uploaded_file,
    update_document_status,
)


router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)


# =========================================================
# UPLOAD + PROCESS DOCUMENT
# =========================================================

@router.post(
    "/",
    summary="Upload and process document",
)
async def upload_document(
    category: DocumentCategory = Form(...),
    file: UploadFile = File(...),
):
    """
    Upload and automatically process a document.
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

    document_id = upload_result[
        "document_id"
    ]

    file_path = upload_result[
        "file_path"
    ]

    document_category = upload_result[
        "category"
    ]

    file_name = upload_result[
        "file_name"
    ]

    # =====================================================
    # 2. MARK PROCESSING
    # =====================================================

    update_document_status(
        document_id,
        "processing",
    )

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

    except FileNotFoundError as exc:

        update_document_status(
            document_id,
            "processing_failed",
        )

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

        update_document_status(
            document_id,
            "processing_failed",
        )

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

        update_document_status(
            document_id,
            "processing_failed",
        )

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
    # 4. CHECK PROCESSING RESULT
    # =====================================================

    if not processing_result.get(
        "success",
        False,
    ):

        update_document_status(
            document_id,
            "processing_failed",
        )

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
    # 5. MARK PROCESSED
    # =====================================================

    update_document_status(
        document_id,
        "processed",
    )

    # =====================================================
    # 6. COMPLETE SUCCESS
    # =====================================================

    return {
        "success": True,
        "message": (
            "Document uploaded and processed successfully."
        ),
        "document_id": document_id,
        "file_name": file_name,
        "category": document_category,
        "file_path": file_path,
        "status": "processed",
        "processing": processing_result,
    }


# =========================================================
# LIST DOCUMENTS
# =========================================================

@router.get(
    "/",
    summary="List uploaded documents",
)
async def get_documents():
    """
    Return all registered documents.
    """

    documents = list_documents()

    return {
        "success": True,
        "count": len(documents),
        "documents": documents,
    }


# =========================================================
# DOCUMENT DETAILS
# =========================================================

@router.get(
    "/{document_id}",
    summary="Get document metadata",
)
async def get_document_details(
    document_id: str,
):
    """
    Return metadata for one document.
    """

    document = get_document(
        document_id
    )

    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return {
        "success": True,
        "document": document,
    }


# =========================================================
# DELETE DOCUMENT
# =========================================================

@router.delete(
    "/{document_id}",
    summary="Delete uploaded document",
)
async def remove_document(
    document_id: str,
):
    """
    Delete a document from storage
    and remove its registry entry.

    NOTE:
    Vector-index cleanup will be added before
    exposing the final Delete action in React.
    """

    document = delete_document(
        document_id
    )

    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return {
        "success": True,
        "message": (
            "Document deleted successfully."
        ),
        "document": document,
    }