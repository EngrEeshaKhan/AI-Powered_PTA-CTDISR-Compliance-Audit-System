from pathlib import Path
from typing import Any

from app.ai.chunking.semantic_chunker import semantic_chunk
from app.ai.ingestion.loader import load_document


def chunk_advisory(
    file_path: str | Path,
) -> list[dict[str, Any]]:
    """
    Load and chunk a security/technical advisory.

    The complete extracted document is passed through the
    semantic chunker. Content is not intentionally discarded.
    """

    result = load_document(file_path)

    text = result.get("text", "")

    if not text or not text.strip():
        return []

    chunks = semantic_chunk(
        text=text,
        chunk_size=1200,
        overlap=200,
        minimum_words=40,
    )

    for chunk in chunks:
        chunk["document_type"] = "advisory"
        chunk["file_name"] = result.get(
            "file_name",
            Path(file_path).name,
        )
        chunk["file_path"] = result.get(
            "file_path",
            str(file_path),
        )

    return chunks