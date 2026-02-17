"""PaddleOCR API calls for layout analysis."""

import os
from dataclasses import dataclass, field

import fitz  # PyMuPDF


@dataclass
class PageData:
    """Represents extracted data for a single PDF page."""

    page_number: int
    image_bytes: bytes = b""
    text_blocks: list[dict] = field(default_factory=list)
    raw_text: str = ""


def analyze_layout(pdf_path: str, two_column: bool = False) -> list[PageData]:
    """Extract page images and run PaddleOCR layout analysis.

    Args:
        pdf_path: Path to the PDF file.
        two_column: Whether the PDF uses a two-column layout.

    Returns:
        List of PageData objects, one per page.
    """
    # TODO: Integrate PaddleOCR API for layout detection
    # For now, extract page images with PyMuPDF
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap()
        pages.append(
            PageData(
                page_number=i + 1,
                image_bytes=pix.tobytes("png"),
                raw_text=page.get_text(),
            )
        )
    doc.close()
    return pages
