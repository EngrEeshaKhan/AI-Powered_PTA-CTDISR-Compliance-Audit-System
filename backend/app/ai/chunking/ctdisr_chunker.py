from pathlib import Path
from typing import Any

from app.ai.chunking.semantic_chunker import semantic_chunk
from app.ai.ingestion.loader import load_document


def chunk_ctdisr(
    file_path: str | Path,
) -> list[dict[str, Any]]:
    """
    Load and chunk a PTA CTDISR framework document.

    All extracted content is retained unless the source parser
    itself produces no text.
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
        chunk["document_type"] = "ctdisr"
        chunk["file_name"] = result.get(
            "file_name",
            Path(file_path).name,
        )
        chunk["file_path"] = result.get(
            "file_path",
            str(file_path),
        )

    return chunks