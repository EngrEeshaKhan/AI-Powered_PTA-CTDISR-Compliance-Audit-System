import re


def normalize_whitespace(text: str) -> str:
    """
    Normalize excessive whitespace while preserving paragraph structure.
    """

    if not text:
        return ""

    # Normalize Windows line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Remove trailing spaces from each line
    text = "\n".join(
        line.rstrip()
        for line in text.split("\n")
    )

    # Collapse multiple spaces
    text = re.sub(r"[ ]{2,}", " ", text)

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def remove_page_artifacts(text: str) -> str:
    """
    Remove common PDF extraction artifacts.

    This is intentionally conservative.
    We do not aggressively modify words because
    policy and CTDISR terminology must be preserved.
    """

    if not text:
        return ""

    # Remove isolated page numbers.
    # Example:
    #     12
    #     13
    #     14
    text = re.sub(
        r"(?m)^\s*\d+\s*$",
        "",
        text,
    )

    # Remove common standalone page markers.
    text = re.sub(
        r"(?im)^\s*page\s+\d+(\s+of\s+\d+)?\s*$",
        "",
        text,
    )

    return text


def clean_extracted_text(text: str) -> str:
    """
    Main preprocessing function for extracted document text.

    The cleaning is deliberately conservative so that
    compliance terminology and control wording are not changed.
    """

    if not text:
        return ""

    text = normalize_whitespace(text)

    text = remove_page_artifacts(text)

    text = normalize_whitespace(text)

    return text