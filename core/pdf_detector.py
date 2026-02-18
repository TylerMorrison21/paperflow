"""Detect whether a PDF is text-based, scanned, or mixed.

Uses PyMuPDF: a page is considered "text" if it has more than TEXT_THRESHOLD
extractable characters, otherwise "scanned".
"""

import fitz  # PyMuPDF

TEXT_THRESHOLD = 50  # chars per page to be counted as text-based


def detect_pdf_type(pdf_path: str) -> str:
    """Return 'text', 'scanned', or 'mixed' based on extractable text per page.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        'text'    — all pages have extractable text
        'scanned' — no pages have extractable text
        'mixed'   — some pages have text, some do not
    """
    doc = fitz.open(pdf_path)
    text_pages = 0
    scanned_pages = 0

    for page in doc:
        chars = len(page.get_text().strip())
        if chars > TEXT_THRESHOLD:
            text_pages += 1
        else:
            scanned_pages += 1

    doc.close()

    if text_pages == 0:
        return "scanned"
    if scanned_pages == 0:
        return "text"
    return "mixed"


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m core.pdf_detector <path/to/file.pdf>")
        sys.exit(1)

    path = sys.argv[1]
    result = detect_pdf_type(path)
    print(f"Result: {result}")

    # Per-page breakdown for debugging
    doc = fitz.open(path)
    for i, page in enumerate(doc):
        chars = len(page.get_text().strip())
        label = "text" if chars > TEXT_THRESHOLD else "scanned"
        print(f"  Page {i + 1:3d}: {chars:6d} chars → {label}")
    doc.close()
