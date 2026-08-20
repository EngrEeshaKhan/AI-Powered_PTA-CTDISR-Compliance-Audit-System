from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from app.ai.chunking.advisory_chunker import chunk_advisory
from app.ai.chunking.asset_chunker import chunk_asset
from app.ai.chunking.ctdisr_chunker import chunk_ctdisr
from app.ai.chunking.policy_chunker import chunk_policy
from app.ai.embeddings.embed_documents import embed_chunks
from app.ai.vectorstore.index_manager import IndexManager


PROJECT_ROOT = Path(__file__).resolve().parents[4]

DOCUMENT_ROOT = (
    PROJECT_ROOT
    / "storage"
    / "documents"
)

ADVISORY_DIR = DOCUMENT_ROOT / "advisories"
POLICY_DIR = DOCUMENT_ROOT / "policies"
CTDISR_DIR = DOCUMENT_ROOT / "ctdisr"
ASSET_DIR = DOCUMENT_ROOT / "assets"


def create_chunk_key(
    chunk: dict[str, Any],
) -> str:
    """
    Create a stable identifier for a chunk.

    The document path + chunk text are used so that identical
    text appearing in different documents is still treated as
    a separate document occurrence.
    """

    file_path = str(
        chunk.get("file_path", "")
    )

    text = str(
        chunk.get("text", "")
    ).strip()

    document_type = str(
        chunk.get("document_type", "")
    )

    raw_key = (
        f"{document_type}|"
        f"{file_path}|"
        f"{text}"
    )

    return hashlib.sha256(
        raw_key.encode("utf-8")
    ).hexdigest()


def prepare_chunks(
    chunks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Add stable chunk identifiers.
    """

    prepared: list[dict[str, Any]] = []

    for chunk in chunks:

        text = str(
            chunk.get("text", "")
        ).strip()

        if not text:
            continue

        chunk = dict(chunk)

        chunk["chunk_key"] = (
            create_chunk_key(chunk)
        )

        prepared.append(chunk)

    return prepared


# ============================================================
# INDIVIDUAL DOCUMENT INDEXING
# ============================================================


def index_document(
    file_path: str | Path,
    document_type: str,
    index_manager: IndexManager,
) -> dict[str, Any]:
    """
    Chunk, embed, and persist one document.
    """

    path = Path(file_path)

    print()
    print("=" * 70)
    print(
        f"INDEXING: {path.name}"
    )
    print(
        f"TYPE: {document_type}"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # CHUNK
    # --------------------------------------------------------

    if document_type == "advisory":

        chunks = chunk_advisory(path)

    elif document_type == "policy":

        chunks = chunk_policy(path)

    elif document_type == "ctdisr":

        chunks = chunk_ctdisr(path)

    elif document_type == "asset":

        chunks = chunk_asset(path)

    else:

        raise ValueError(
            f"Unsupported document type: "
            f"{document_type}"
        )

    chunks = prepare_chunks(chunks)

    print(
        f"Chunks created: {len(chunks)}"
    )

    if not chunks:

        print(
            "WARNING: No chunks generated."
        )

        return {
            "file": str(path),
            "document_type": document_type,
            "chunks": 0,
            "embedded": 0,
            "indexed": 0,
        }

    # --------------------------------------------------------
    # EMBEDDINGS
    # --------------------------------------------------------

    embedded_chunks = embed_chunks(
        chunks,
        batch_size=32,
    )

    print(
        f"Embeddings available: "
        f"{len(embedded_chunks)}"
    )

    # --------------------------------------------------------
    # VECTOR INDEX
    # --------------------------------------------------------

    indexed_count = (
        index_manager.add_embedded_chunks(
            embedded_chunks
        )
    )

    print(
        f"New vectors indexed: "
        f"{indexed_count}"
    )

    return {
        "file": str(path),
        "document_type": document_type,
        "chunks": len(chunks),
        "embedded": len(embedded_chunks),
        "indexed": indexed_count,
    }


# ============================================================
# DISCOVERY
# ============================================================


def discover_documents() -> list[tuple[Path, str]]:
    """
    Discover all supported source documents.

    Returns:
        [(path, document_type), ...]
    """

    documents: list[
        tuple[Path, str]
    ] = []

    # --------------------------------------------------------
    # ADVISORIES
    # --------------------------------------------------------

    if ADVISORY_DIR.exists():

        for path in sorted(
            ADVISORY_DIR.rglob("*")
        ):

            if path.is_file() and path.suffix.lower() in {
                ".pdf",
                ".docx",
                ".doc",
            }:

                documents.append(
                    (
                        path,
                        "advisory",
                    )
                )

    # --------------------------------------------------------
    # POLICIES
    # --------------------------------------------------------

    if POLICY_DIR.exists():

        for path in sorted(
            POLICY_DIR.rglob("*")
        ):

            if path.is_file() and path.suffix.lower() in {
                ".pdf",
                ".docx",
                ".doc",
            }:

                documents.append(
                    (
                        path,
                        "policy",
                    )
                )

    # --------------------------------------------------------
    # CTDISR
    # --------------------------------------------------------

    if CTDISR_DIR.exists():

        for path in sorted(
            CTDISR_DIR.rglob("*")
        ):

            if path.is_file() and path.suffix.lower() in {
                ".pdf",
                ".docx",
                ".doc",
            }:

                documents.append(
                    (
                        path,
                        "ctdisr",
                    )
                )

    # --------------------------------------------------------
    # ASSETS
    # --------------------------------------------------------

    if ASSET_DIR.exists():

        for path in sorted(
            ASSET_DIR.rglob("*")
        ):

            if path.is_file() and path.suffix.lower() in {
                ".xlsx",
                ".xls",
            }:

                documents.append(
                    (
                        path,
                        "asset",
                    )
                )

    return documents


# ============================================================
# BUILD KNOWLEDGE BASE
# ============================================================


def build_index() -> list[dict[str, Any]]:
    """
    Build/update the persistent vector knowledge base.

    Existing chunks are skipped.

    New chunks are embedded and added.

    The final vector index and metadata are saved to:

        storage/vectors/knowledge.index
        storage/vectors/knowledge_metadata.json
    """

    documents = discover_documents()

    print()
    print("=" * 70)
    print("PTA CTDISR KNOWLEDGE BASE INDEXING")
    print("=" * 70)

    print(
        f"Documents discovered: {len(documents)}"
    )

    if not documents:

        print(
            "ERROR: No documents found."
        )

        return []

    index_manager = IndexManager()

    print(
        f"Existing vectors: "
        f"{index_manager.count()}"
    )

    results: list[
        dict[str, Any]
    ] = []

    for file_path, document_type in documents:

        try:

            result = index_document(
                file_path=file_path,
                document_type=document_type,
                index_manager=index_manager,
            )

            results.append(result)

        except Exception as exc:

            print()
            print(
                f"ERROR processing: "
                f"{file_path.name}"
            )

            print(
                f"Reason: {exc}"
            )

            results.append(
                {
                    "file": str(file_path),
                    "document_type": document_type,
                    "chunks": 0,
                    "embedded": 0,
                    "indexed": 0,
                    "error": str(exc),
                }
            )

    # --------------------------------------------------------
    # FINAL SAVE
    # --------------------------------------------------------

    index_manager.save()

    print()
    print("=" * 70)
    print("INDEXING COMPLETE")
    print("=" * 70)

    print(
        f"Final vector count: "
        f"{index_manager.count()}"
    )

    print(
        f"Vector index: "
        f"storage/vectors/knowledge.index"
    )

    print(
        f"Metadata: "
        f"storage/vectors/knowledge_metadata.json"
    )

    return results


if __name__ == "__main__":

    build_index()