import io
import logging
from contextlib import redirect_stdout

import fitz
from pypdf import PdfReader

try:
    import pymupdf4llm
except ImportError:  # pragma: no cover - exercised via fallback tests
    pymupdf4llm = None

logger = logging.getLogger(__name__)


def parser_available() -> bool:
    return True


async def parse_pdf(pdf_bytes: bytes) -> dict:
    """
    Local parser using PyMuPDF.

    Prefer the official PyMuPDF4LLM markdown extractor when available.
    Fall back to sorted page extraction when that helper package is absent.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    markdown = _extract_markdown(doc)

    metadata = doc.metadata or {}
    pages = _safe_page_count(pdf_bytes, len(doc))

    return {
        "markdown": markdown,
        "images": {},
        "metadata": {
            "title": metadata.get("title") or "",
            "author": metadata.get("author") or "",
            "source": "PyMuPDF local parser",
            "pages": pages,
        },
    }


def _extract_markdown(doc: fitz.Document) -> str:
    if pymupdf4llm is not None:
        try:
            markdown = _extract_with_pymupdf4llm(doc)
            if markdown:
                return markdown
        except Exception:
            logger.exception("PyMuPDF4LLM extraction failed, falling back to PyMuPDF page extraction")

    return _extract_with_pymupdf(doc)


def _extract_with_pymupdf4llm(doc: fitz.Document) -> str:
    with io.StringIO() as captured, redirect_stdout(captured):
        markdown = pymupdf4llm.to_markdown(
            doc,
            page_chunks=False,
            page_separators=False,
            ignore_images=True,
            write_images=False,
            show_progress=False,
            force_text=True,
        )
    return (markdown or "").strip()


def _extract_with_pymupdf(doc: fitz.Document) -> str:
    page_markdown: list[str] = []

    for page_index, page in enumerate(doc, start=1):
        page_md = _extract_page_markdown(page).strip()
        if page_md:
            page_markdown.append(page_md)
        else:
            page_markdown.append(f"\n\n# Page {page_index}\n\n")

    return "\n\n".join(page_markdown).strip()


def _extract_page_markdown(page: fitz.Page) -> str:
    try:
        page_md = page.get_text("markdown", sort=True)
    except TypeError:
        page_md = page.get_text("markdown")
    except Exception:
        page_md = ""

    page_md = (page_md or "").strip()
    if not page_md:
        page_md = _extract_page_blocks(page)

    tables_md = _extract_page_tables(page, page_md)
    if tables_md:
        if page_md:
            return f"{page_md}\n\n{tables_md}".strip()
        return tables_md.strip()

    return page_md


def _extract_page_blocks(page: fitz.Page) -> str:
    blocks: list[str] = []
    try:
        raw_blocks = page.get_text("blocks", sort=True)
    except TypeError:
        raw_blocks = page.get_text("blocks")
    except Exception:
        raw_blocks = []

    for block in raw_blocks:
        text = (block[4] or "").strip()
        if text:
            blocks.append(text)

    return "\n\n".join(blocks).strip()


def _extract_page_tables(page: fitz.Page, existing_markdown: str) -> str:
    try:
        finder = page.find_tables()
    except Exception:
        return ""

    existing_markdown = existing_markdown or ""
    table_chunks: list[str] = []
    for table in getattr(finder, "tables", []) or []:
        try:
            table_md = (table.to_markdown() or "").strip()
        except Exception:
            continue
        if not table_md:
            continue
        if table_md in existing_markdown:
            continue
        table_chunks.append(table_md)

    return "\n\n".join(table_chunks).strip()


def _safe_page_count(pdf_bytes: bytes, fallback: int) -> int:
    try:
        return len(PdfReader(io.BytesIO(pdf_bytes)).pages)
    except Exception:
        return fallback
