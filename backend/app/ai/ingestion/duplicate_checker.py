
from hashlib import sha256
from pathlib import Path


def calculate_checksum(file_path: Path) -> str:
    """
    Calculate a SHA-256 checksum for a file.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    checksum = sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            checksum.update(chunk)

    return checksum.hexdigest()


def is_duplicate(
    file_path: Path,
    existing_checksums: set[str],
) -> bool:
    """
    Check whether a file already exists based on its checksum.
    """

    checksum = calculate_checksum(file_path)

    return checksum in existing_checksums
