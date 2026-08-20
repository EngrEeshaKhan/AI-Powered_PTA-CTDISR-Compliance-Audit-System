from __future__ import annotations

from pathlib import Path
from typing import Any

from app.ai.embeddings.embed_documents import embed_chunks
from app.ai.vectorstore.index_manager import IndexManager


class DocumentProcessor:
    """
    Main document processing pipeline.

    Flow:

        Uploaded File
             ↓
        Correct Category Chunker
             ↓
        Embedding Model / Cache
             ↓
        IndexManager
             ↓
        VectorManager
             ↓
        Persistent FAISS Index + Metadata

    Supported document types:

        - advisory
        - policy
        - ctdisr
        - asset
    """

    def __init__(self) -> None:
        """
        Initialize the persistent index manager.

        all-MiniLM-L6-v2 produces 384-dimensional embeddings.
        """

        self.index_manager = IndexManager()

    # =========================================================
    # CHUNKING
    # =========================================================

    def chunk_document(
        self,
        file_path: str | Path,
        document_type: str,
    ) -> list[dict[str, Any]]:
        """
        Select the correct chunker according to document type.
        """

        file_path = Path(file_path)

        document_type = (
            document_type
            .strip()
            .lower()
        )

        # -----------------------------------------------------
        # CTDISR
        # -----------------------------------------------------

        if document_type == "ctdisr":

            from app.ai.chunking.ctdisr_chunker import (
                chunk_ctdisr,
            )

            return chunk_ctdisr(file_path)

        # -----------------------------------------------------
        # POLICY
        # -----------------------------------------------------

        if document_type == "policy":

            from app.ai.chunking.policy_chunker import (
                chunk_policy,
            )

            return chunk_policy(file_path)

        # -----------------------------------------------------
        # ADVISORY
        # -----------------------------------------------------

        if document_type == "advisory":

            from app.ai.chunking.advisory_chunker import (
                chunk_advisory,
            )

            return chunk_advisory(file_path)

        # -----------------------------------------------------
        # ASSET
        # -----------------------------------------------------

        if document_type == "asset":

            from app.ai.chunking.asset_chunker import (
                chunk_asset,
            )

            return chunk_asset(file_path)

        # -----------------------------------------------------
        # INVALID TYPE
        # -----------------------------------------------------

        raise ValueError(
            f"Unsupported document type: "
            f"{document_type}. "
            f"Allowed types: advisory, policy, "
            f"ctdisr, asset."
        )

    # =========================================================
    # COMPLETE PROCESSING PIPELINE
    # =========================================================

    def process(
        self,
        file_path: str | Path,
        document_type: str,
    ) -> dict[str, Any]:
        """
        Complete document processing pipeline.

        File
          ↓
        Chunk
          ↓
        Embed / Reuse cached embedding
          ↓
        Save to persistent FAISS vector store
        """

        file_path = Path(file_path)

        document_type = (
            document_type
            .strip()
            .lower()
        )

        # -----------------------------------------------------
        # CHECK FILE
        # -----------------------------------------------------

        if not file_path.exists():
            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        if not file_path.is_file():
            raise ValueError(
                f"Path is not a file: {file_path}"
            )

        # -----------------------------------------------------
        # CHECK DOCUMENT TYPE
        # -----------------------------------------------------

        allowed_types = {
            "advisory",
            "policy",
            "ctdisr",
            "asset",
        }

        if document_type not in allowed_types:
            raise ValueError(
                f"Unsupported document type: "
                f"{document_type}. "
                f"Allowed types: "
                f"{', '.join(sorted(allowed_types))}"
            )

        print()
        print("=" * 70)
        print(
            f"PROCESSING: {file_path.name}"
        )
        print(
            f"TYPE: {document_type}"
        )
        print("=" * 70)

        # =====================================================
        # 1. CHUNK DOCUMENT
        # =====================================================

        print(
            "\n[1/3] CHUNKING DOCUMENT..."
        )

        chunks = self.chunk_document(
            file_path=file_path,
            document_type=document_type,
        )

        print(
            f"Chunks created: {len(chunks)}"
        )

        if not chunks:

            print(
                "No chunks were created."
            )

            return {
                "success": False,
                "file_name": file_path.name,
                "document_type": document_type,
                "chunks": 0,
                "embeddings": 0,
                "vectors_added": 0,
                "total_vectors": (
                    self.index_manager.count()
                ),
                "message": (
                    "No chunks created."
                ),
            }

        # =====================================================
        # 2. GENERATE / REUSE EMBEDDINGS
        # =====================================================

        print(
            "\n[2/3] GENERATING / "
            "REUSING EMBEDDINGS..."
        )

        embedded_chunks = embed_chunks(
            chunks,
            batch_size=32,
        )

        print(
            f"Chunks with embeddings: "
            f"{len(embedded_chunks)}"
        )

        if not embedded_chunks:

            return {
                "success": False,
                "file_name": file_path.name,
                "document_type": document_type,
                "chunks": len(chunks),
                "embeddings": 0,
                "vectors_added": 0,
                "total_vectors": (
                    self.index_manager.count()
                ),
                "message": (
                    "No embeddings were generated."
                ),
            }

        # =====================================================
        # 3. SAVE TO VECTOR STORE
        # =====================================================

        print(
            "\n[3/3] SAVING TO VECTOR STORE..."
        )

        vectors_added = (
            self.index_manager.add_embedded_chunks(
                embedded_chunks
            )
        )

        total_vectors = (
            self.index_manager.count()
        )

        print(
            f"New vectors added: "
            f"{vectors_added}"
        )

        print(
            f"Total vectors: "
            f"{total_vectors}"
        )

        print()
        print("=" * 70)
        print("PROCESSING COMPLETE")
        print("=" * 70)

        # =====================================================
        # RESULT
        # =====================================================

        return {
            "success": True,
            "file_name": file_path.name,
            "document_type": document_type,
            "chunks": len(chunks),
            "embeddings": len(embedded_chunks),
            "vectors_added": vectors_added,
            "total_vectors": total_vectors,
            "message": (
                "Document processed successfully."
            ),
        }