from __future__ import annotations

from pathlib import Path

from app.ai.ingestion.pdf_parser import parse_pdf
from app.ai.ingestion.excel_parser import parse_excel
from app.ai.ingestion.docx_parser import parse_docx
from app.ai.ingestion.doc_parser import parse_doc


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".doc",
    ".xlsx",
}


def load_document(file_path: str | Path) -> dict:
    """
    Load a supported document and extract its content.

    Supported:
        - PDF
        - DOCX
        - DOC
        - XLSX

    Returns:
        Dictionary containing extracted content
        and document information.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {path}"
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Supported types: "
            f"{', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # ---------------------------------------------------------
    # Select parser according to file extension
    # ---------------------------------------------------------

    if extension == ".pdf":
        result = parse_pdf(path)

    elif extension == ".docx":
        result = parse_docx(path)

    elif extension == ".doc":
        result = parse_doc(path)

    elif extension == ".xlsx":
        result = parse_excel(path)

    else:
        raise ValueError(
            f"Unsupported document type: {extension}"
        )

    # ---------------------------------------------------------
    # Make sure every parser returns a dictionary
    # ---------------------------------------------------------

    if not isinstance(result, dict):
        raise TypeError(
            f"Parser for {extension} must return a dictionary, "
            f"but returned {type(result).__name__}"
        )

    # ---------------------------------------------------------
    # Add common document metadata
    # ---------------------------------------------------------

    result["file_name"] = path.name
    result["file_path"] = str(path)
    result["file_type"] = extension.replace(
        ".",
        "",
    ).upper()

    # ---------------------------------------------------------
    # Basic validation
    # ---------------------------------------------------------

    if not result.get("text") and not result.get("sheets"):
        raise ValueError(
            f"No usable content was extracted from: "
            f"{path.name}"
        )

    return result