from __future__ import annotations

import hashlib
import re
from typing import Any


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_extracted_text(text: str) -> str:
    """
    Clean common PDF/DOCX extraction artifacts.

    Important:
    This function cleans formatting problems without
    intentionally deleting meaningful document content.
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Common extraction/OCR corrections
    text = re.sub(
        r"Classifi\s+c\s+ation",
        "Classification",
        text,
    )

    text = re.sub(
        r"lntemal",
        "Internal",
        text,
    )

    text = re.sub(
        r"l5\b",
        "15",
        text,
    )

    # Normalize spaces/tabs
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    # Normalize excessive blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


# =========================================================
# TABLE OF CONTENTS
# =========================================================

def remove_table_of_contents(text: str) -> str:
    """
    Remove a table-of-contents block when it can be identified
    safely.

    If the TOC cannot be identified confidently, the original
    text is returned.
    """

    if not text:
        return ""

    lines = text.splitlines()

    toc_start = None

    for index, line in enumerate(lines):

        normalized = line.strip().lower()

        if normalized in {
            "table of contents",
            "contents",
        }:
            toc_start = index
            break

    if toc_start is None:
        return text

    # Look for a strong numbered section heading after TOC.
    toc_end = None

    for index in range(
        toc_start + 1,
        len(lines),
    ):

        line = lines[index].strip()

        if re.match(
            r"^\d+(?:\.\d+)*[\.\)]?\s+[A-Za-z]",
            line,
        ):
            toc_end = index
            break

    # If we cannot confidently identify the end,
    # preserve the original document.
    if toc_end is None:
        return text

    cleaned_lines = (
        lines[:toc_start]
        + lines[toc_end:]
    )

    return "\n".join(
        cleaned_lines
    ).strip()


# =========================================================
# SECTION SPLITTING
# =========================================================

def split_into_sections(
    text: str,
) -> list[str]:
    """
    Split text into logical numbered sections.

    Examples:

        1. Objective
        2. Scope
        3. Responsibilities
        3.1 Access Control

    If no numbered headings are found,
    the complete document is returned as one section.
    """

    text = text.strip()

    if not text:
        return []

    pattern = re.compile(
        r"(?m)"
        r"(?=^\s*"
        r"\d+(?:\.\d+)*"
        r"[\.\)]?"
        r"\s+"
        r"[A-Za-z]"
        r"[^\n]*)"
    )

    sections = re.split(
        pattern,
        text,
    )

    sections = [
        section.strip()
        for section in sections
        if section.strip()
    ]

    if not sections:
        return [text]

    return sections


# =========================================================
# LARGE TEXT SPLITTING
# =========================================================

def split_large_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[str]:
    """
    Split large text into overlapping word-based chunks.

    The final smaller chunk is always retained.
    """

    words = text.split()

    if not words:
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative"
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words),
        )

        chunk = " ".join(
            words[start:end]
        ).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


# =========================================================
# CHUNK KEY GENERATION
# =========================================================

def generate_chunk_key(
    text: str,
    chunk_index: int,
) -> str:
    """
    Generate a deterministic SHA-256 identifier
    for a chunk.

    The same chunk content + position produces
    the same key.
    """

    raw = (
        f"{chunk_index}|"
        f"{text.strip()}"
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


# =========================================================
# SEMANTIC CHUNKING
# =========================================================

def semantic_chunk(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
    minimum_words: int = 40,
) -> list[dict[str, Any]]:
    """
    Create retrieval-friendly semantic chunks.

    Pipeline:

        1. Clean extracted text
        2. Remove TOC when safely detectable
        3. Split into logical sections
        4. Split oversized sections
        5. Generate chunk_key
        6. NEVER silently discard document content

    minimum_words is retained as a quality hint.
    Short compliance requirements are NOT discarded.
    """

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative"
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    if minimum_words < 1:
        minimum_words = 1

    # -----------------------------------------------------
    # STEP 1: CLEAN
    # -----------------------------------------------------

    text = clean_extracted_text(text)

    if not text:
        return []

    # -----------------------------------------------------
    # STEP 2: REMOVE TOC
    # -----------------------------------------------------

    text = remove_table_of_contents(text)

    if not text:
        return []

    # -----------------------------------------------------
    # STEP 3: SPLIT INTO SECTIONS
    # -----------------------------------------------------

    sections = split_into_sections(text)

    if not sections:
        return []

    chunks: list[dict[str, Any]] = []

    # -----------------------------------------------------
    # STEP 4: PROCESS EACH SECTION
    # -----------------------------------------------------

    for section_index, section in enumerate(
        sections
    ):

        section = section.strip()

        if not section:
            continue

        words = section.split()

        # -------------------------------------------------
        # SMALL SECTION
        # -------------------------------------------------

        if len(words) <= chunk_size:

            chunk_index = len(chunks)

            chunks.append(
                {
                    "chunk_index": chunk_index,
                    "section_index": section_index,
                    "part_index": 0,
                    "text": section,
                    "word_count": len(words),

                    # IMPORTANT:
                    # Every chunk receives a deterministic key.
                    "chunk_key": generate_chunk_key(
                        text=section,
                        chunk_index=chunk_index,
                    ),
                }
            )

            continue

        # -------------------------------------------------
        # LARGE SECTION
        # -------------------------------------------------

        smaller_chunks = split_large_text(
            section,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for part_index, chunk_text in enumerate(
            smaller_chunks
        ):

            chunk_text = chunk_text.strip()

            if not chunk_text:
                continue

            word_count = len(
                chunk_text.split()
            )

            chunk_index = len(chunks)

            chunks.append(
                {
                    "chunk_index": chunk_index,
                    "section_index": section_index,
                    "part_index": part_index,
                    "text": chunk_text,
                    "word_count": word_count,

                    # IMPORTANT:
                    # Every large-section chunk also gets a key.
                    "chunk_key": generate_chunk_key(
                        text=chunk_text,
                        chunk_index=chunk_index,
                    ),
                }
            )

    # -----------------------------------------------------
    # STEP 5: FINAL SAFETY CHECK
    # -----------------------------------------------------

    if not chunks and text.strip():

        chunk_index = 0

        chunks.append(
            {
                "chunk_index": chunk_index,
                "section_index": 0,
                "part_index": 0,
                "text": text.strip(),
                "word_count": len(
                    text.split()
                ),

                "chunk_key": generate_chunk_key(
                    text=text.strip(),
                    chunk_index=chunk_index,
                ),
            }
        )

    return chunks