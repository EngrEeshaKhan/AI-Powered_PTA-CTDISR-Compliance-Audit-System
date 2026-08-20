from __future__ import annotations

from pathlib import Path

import textract


def parse_doc(file_path: str | Path) -> dict:
    """
    Extract text from a legacy Microsoft Word .doc file.

    Returns:
        Dictionary containing extracted text.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"DOC file not found: {path}"
        )

    if path.suffix.lower() != ".doc":
        raise ValueError(
            f"Expected a .doc file, got: {path.suffix}"
        )

    try:
        extracted = textract.process(
            str(path)
        )
    except Exception as exc:
        raise RuntimeError(
            f"Failed to extract text from DOC file "
            f"'{path.name}': {exc}"
        ) from exc

    text = extracted.decode(
        "utf-8",
        errors="replace",
    ).strip()

    if not text:
        raise ValueError(
            f"No usable text extracted from: {path.name}"
        )

    return {
        "text": text,
    }