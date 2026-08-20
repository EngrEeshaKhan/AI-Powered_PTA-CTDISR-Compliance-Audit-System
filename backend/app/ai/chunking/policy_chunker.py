from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from app.ai.chunking.semantic_chunker import semantic_chunk
from app.ai.ingestion.loader import load_document


def _create_chunk_key(
    document_type: str,
    file_name: str,
    chunk_index: int,
    text: str,
) -> str:
    """
    Create a deterministic unique identifier for a chunk.

    The same document + chunk position + content
    will always produce the same key.

    This prevents duplicate vectors when the same
    document is uploaded/processed again.
    """

    value = (
        f"{document_type}:"
        f"{file_name}:"
        f"{chunk_index}:"
        f"{text}"
    )

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def chunk_policy(
    file_path: str | Path,
) -> list[dict[str, Any]]:
    """
    Load and chunk an NTC policy document.

    Every returned chunk contains the metadata required
    by the vector store, including a deterministic
    chunk_key.
    """

    file_path = Path(file_path)

    # -----------------------------------------------------
    # LOAD DOCUMENT
    # -----------------------------------------------------

    result = load_document(file_path)

    text = result.get("text", "")

    if not text or not text.strip():
        return []

    # -----------------------------------------------------
    # SEMANTIC CHUNKING
    # -----------------------------------------------------

    chunks = semantic_chunk(
        text=text,
        chunk_size=1200,
        overlap=200,
        minimum_words=40,
    )

    # -----------------------------------------------------
    # ADD REQUIRED METADATA
    # -----------------------------------------------------

    file_name = result.get(
        "file_name",
        file_path.name,
    )

    file_path_value = result.get(
        "file_path",
        str(file_path),
    )

    for index, chunk in enumerate(chunks):

        chunk_text = str(
            chunk.get("text", "")
        ).strip()

        # Preserve existing chunk metadata
        chunk["document_type"] = "policy"

        chunk["file_name"] = file_name

        chunk["file_path"] = file_path_value

        # Ensure a stable chunk index
        chunk["chunk_index"] = index

        # Ensure word count exists
        chunk["word_count"] = len(
            chunk_text.split()
        )

        # -------------------------------------------------
        # REQUIRED VECTORSTORE KEY
        # -------------------------------------------------

        chunk["chunk_key"] = _create_chunk_key(
            document_type="policy",
            file_name=file_name,
            chunk_index=index,
            text=chunk_text,
        )

    return chunks