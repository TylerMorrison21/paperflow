"""Text cleaning: line-break fixing, header/footer removal."""

import re


def clean_text(page) -> "PageData":
    """Clean raw OCR text on a PageData object.

    Args:
        page: A PageData object with raw_text to clean.

    Returns:
        The same PageData object with cleaned raw_text.
    """
    text = page.raw_text
    text = remove_headers_footers(text)
    text = merge_broken_lines(text)
    page.raw_text = text.strip()
    return page


def remove_headers_footers(text: str) -> str:
    """Remove common header/footer patterns (page numbers, repeated lines).

    Args:
        text: Raw page text.

    Returns:
        Text with headers/footers removed.
    """
    # Remove standalone page numbers
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    # TODO: Detect and remove repeated header/footer lines across pages
    return text


def merge_broken_lines(text: str) -> str:
    """Merge lines that were broken mid-sentence by PDF hard returns.

    Args:
        text: Text with potential mid-sentence line breaks.

    Returns:
        Text with broken lines merged into proper paragraphs.
    """
    # Join lines that don't end with sentence-ending punctuation
    text = re.sub(r"(?<=[a-z,;])\n(?=[a-z])", " ", text)
    return text
