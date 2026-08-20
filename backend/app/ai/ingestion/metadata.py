from datetime import datetime
from pathlib import Path


def create_metadata(
    file_path: str | Path,
    document_type: str,
    extracted_data: dict,
) -> dict:
    """
    Create standardized metadata for an ingested document.
    """

    path = Path(file_path)

    stat = path.stat()

    metadata = {
        "file_name": path.name,
        "file_path": str(path),
        "file_type": document_type,
        "file_size_bytes": stat.st_size,
        "created_at": datetime.fromtimestamp(
            stat.st_ctime
        ).isoformat(),
        "modified_at": datetime.fromtimestamp(
            stat.st_mtime
        ).isoformat(),
        "ingested_at": datetime.now().isoformat(),
    }

    # PDF metadata
    if "page_count" in extracted_data:
        metadata["page_count"] = extracted_data["page_count"]

    # Text metadata
    if "word_count" in extracted_data:
        metadata["word_count"] = extracted_data["word_count"]

    if "character_count" in extracted_data:
        metadata["character_count"] = extracted_data["character_count"]

    # Excel metadata
    if "sheet_count" in extracted_data:
        metadata["sheet_count"] = extracted_data["sheet_count"]

    if "row_count" in extracted_data:
        metadata["row_count"] = extracted_data["row_count"]

    return metadata