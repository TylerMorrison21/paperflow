import io
import logging

import fitz
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def parser_available() -> bool:
    return True


async def parse_pdf(pdf_bytes: bytes) -> dict:
    """
    Fast local fallback parser using PyMuPDF.

    Quality is lower than Marker, but setup is minimal and fully local.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_markdown: list[str] = []

    for page_index, page in enumerate(doc, start=1):
        try:
            page_md = page.get_text("markdown")
        except Exception:
            page_md = page.get_text("text")

        page_md = (page_md or "").strip()
        if page_md:
            page_markdown.append(page_md)
        else:
            page_markdown.append(f"\n\n# Page {page_index}\n\n")

    metadata = doc.metadata or {}
    pages = _safe_page_count(pdf_bytes, len(doc))

    return {
        "markdown": "\n\n".join(page_markdown).strip(),
        "images": {},
        "metadata": {
            "title": metadata.get("title") or "",
            "author": metadata.get("author") or "",
            "source": "PyMuPDF local parser",
            "pages": pages,
        },
    }


def _safe_page_count(pdf_bytes: bytes, fallback: int) -> int:
    try:
        return len(PdfReader(io.BytesIO(pdf_bytes)).pages)
    except Exception:
        return fallback
