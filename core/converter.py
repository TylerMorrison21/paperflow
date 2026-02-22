"""Conversion orchestrator: all PDFs go through Datalab Marker API → EPUB.

Pipeline:
  PDF → Datalab Marker API → Markdown → build_epub_from_markdown → EPUB
"""

import re
from pathlib import Path

from core.epub_builder import build_epub_from_markdown


def convert_pdf_to_epub(pdf_path: str) -> str:
    """Convert any PDF to EPUB via Datalab Marker API and return the output path."""
    from core import marker_client  # lazy import keeps startup fast

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(output_dir / (Path(pdf_path).stem + ".epub"))

    print(f"[converter] Processing {Path(pdf_path).name}")
    markdown, images = marker_client.convert_pdf(pdf_path)
    print(f"[converter] Marker output: {len(markdown)} chars, {len(images)} images")

    # Save markdown alongside EPUB for comparison / debugging
    md_out = Path(output_path).with_suffix(".md")
    md_out.write_text(markdown, encoding="utf-8")
    print(f"[converter] Markdown saved → {md_out}")

    title = _extract_title_from_markdown(markdown) or _title_from_filename(pdf_path)
    build_epub_from_markdown(markdown, images, output_path, title=title)
    return output_path


# ── helpers ────────────────────────────────────────────────────────────────────

def _extract_title_from_markdown(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _title_from_filename(pdf_path: str) -> str:
    stem = Path(pdf_path).stem
    return re.sub(r"^[0-9a-f]{32}_", "", stem)
