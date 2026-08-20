from pathlib import Path

from pypdf import PdfReader


def parse_pdf(file_path: str | Path) -> dict:
    """
    Extract text and page information from a PDF.
    """

    path = Path(file_path)

    reader = PdfReader(path)

    pages = []
    full_text = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        text = text.strip()

        pages.append(
            {
                "page_number": page_number,
                "text": text,
                "character_count": len(text),
                "word_count": len(text.split()),
            }
        )

        if text:
            full_text.append(text)

    combined_text = "\n\n".join(full_text)

    return {
        "text": combined_text,
        "pages": pages,
        "page_count": len(reader.pages),
        "character_count": len(combined_text),
        "word_count": len(combined_text.split()),
    }