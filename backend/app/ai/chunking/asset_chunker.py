
from pathlib import Path
from typing import Any

import pandas as pd


def chunk_asset(
    file_path: str | Path,
    sheet_name: str = "SYstem",
) -> list[dict[str, Any]]:
    """
    Chunk the NTC asset inventory.

    Each numbered asset row is stored as one complete retrieval chunk.

    The SYstem sheet contains:
        - Sr. No
        - Device & Role
        - Device Sr.No
        - Asset Tag No
        - Position/Location
        - Platform

    Metadata/title rows before the asset table are ignored.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Asset inventory not found: {path}"
        )

    if path.suffix.lower() not in {".xlsx", ".xls"}:
        raise ValueError(
            "Asset inventory must be an Excel file (.xlsx or .xls)."
        )

    df = pd.read_excel(
        path,
        sheet_name=sheet_name,
        header=None,
    )

    chunks = []

    for row_index, row in df.iterrows():

        # First column should contain the asset serial number.
        serial_number = row.iloc[0]

        # Ignore metadata/header rows.
        try:
            sr_no = int(float(serial_number))
        except (ValueError, TypeError):
            continue

        # Read the six asset fields.
        device_role = str(row.iloc[1]).strip()
        device_serial = str(row.iloc[2]).strip()
        asset_tag = str(row.iloc[3]).strip()
        location = str(row.iloc[4]).strip()
        platform = str(row.iloc[5]).strip()

        # Remove pandas NaN values.
        values = [
            device_role,
            device_serial,
            asset_tag,
            location,
            platform,
        ]

        values = [
            "" if value.lower() == "nan" else value
            for value in values
        ]

        device_role = values[0]
        device_serial = values[1]
        asset_tag = values[2]
        location = values[3]
        platform = values[4]

        # Build a retrieval-friendly representation.
        text_parts = [
            f"Asset Serial Number: {sr_no}",
        ]

        if device_role:
            text_parts.append(
                f"Device & Role: {device_role}"
            )

        if device_serial:
            text_parts.append(
                f"Device Serial Number: {device_serial}"
            )

        if asset_tag:
            text_parts.append(
                f"Asset Tag Number: {asset_tag}"
            )

        if location:
            text_parts.append(
                f"Position/Location: {location}"
            )

        if platform:
            text_parts.append(
                f"Platform: {platform}"
            )

        chunk_text = "\n".join(text_parts)

        chunks.append(
            {
                "chunk_index": len(chunks),
                "row_index": int(row_index),
                "asset_serial_number": sr_no,
                "document_type": "asset",
                "sheet_name": sheet_name,
                "file_name": path.name,
                "file_path": str(path),
                "text": chunk_text,
            }
        )

    return chunks
