"""Text extraction pipeline for text-based PDFs using PyMuPDF (zero API cost).

Returns the same list[PageData] format as the scanned (Claude Vision) pipeline
so epub_builder.py can consume both without changes.
"""

import re
from collections import Counter

import fitz  # PyMuPDF

from core.layout_analyzer import PageData


def extract_text_pdf(pdf_path: str) -> list[PageData]:
    """Extract and clean text from a text-based PDF, returning PageData objects.

    Steps:
      1. Extract text blocks per page using PyMuPDF
      2. Detect and remove repeated headers/footers (text on ≥40% of pages)
      3. Detect headings via font size ratio, format as Markdown # / ##
      4. Merge broken lines into paragraphs

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        List of PageData with .markdown set, same format as the scanned pipeline.
    """
    doc = fitz.open(pdf_path)

    # Pass 1: collect raw block dicts for header/footer detection + font sizing
    all_blocks = [
        page.get_text("dict", sort=True)["blocks"]
        for page in doc
    ]

    repeated = _find_repeated_text(all_blocks, len(doc))
    body_size = _estimate_body_font_size(all_blocks)

    # Pass 2: build markdown per page
    pages = []
    for i, (page, blocks) in enumerate(zip(doc, all_blocks)):
        md = _blocks_to_markdown(blocks, repeated, body_size)
        md = _merge_broken_lines(md)
        md = _remove_duplicate_blank_lines(md)
        pages.append(PageData(
            page_number=i + 1,
            raw_text=page.get_text(),
            markdown=md.strip(),
        ))

    doc.close()
    return pages


# ---------------------------------------------------------------------------
# Header / footer detection
# ---------------------------------------------------------------------------

def _find_repeated_text(all_blocks: list, total_pages: int) -> set[str]:
    """Return text strings that appear on ≥40% of pages (min 2).

    Only the first and last text block of each page are checked — the positions
    where headers and footers typically live.
    """
    counts: Counter = Counter()

    for blocks in all_blocks:
        text_blocks = [b for b in blocks if b["type"] == 0]
        if not text_blocks:
            continue

        candidates = [text_blocks[0]]
        if len(text_blocks) > 1:
            candidates.append(text_blocks[-1])

        seen = set()
        for block in candidates:
            text = _block_text(block).strip()
            if text and text not in seen:
                counts[text] += 1
                seen.add(text)

    threshold = max(2, int(total_pages * 0.4))
    return {t for t, n in counts.items() if n >= threshold}


# ---------------------------------------------------------------------------
# Font size analysis
# ---------------------------------------------------------------------------

def _estimate_body_font_size(all_blocks: list) -> float:
    """Return the most common font size (weighted by character count) = body size."""
    size_counts: Counter = Counter()

    for blocks in all_blocks:
        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    size = round(span.get("size", 0))
                    chars = len(span.get("text", "").strip())
                    if size > 0 and chars > 0:
                        size_counts[size] += chars

    return float(size_counts.most_common(1)[0][0]) if size_counts else 12.0


def _block_max_font_size(block: dict) -> float:
    """Return the maximum font size found in any span of the block."""
    max_size = 0.0
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            max_size = max(max_size, span.get("size", 0.0))
    return max_size


def _block_is_bold(block: dict) -> bool:
    """Return True if any span in the block uses a bold font (PyMuPDF flag bit 4)."""
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            if span.get("flags", 0) & 16:
                return True
    return False


# ---------------------------------------------------------------------------
# Block → Markdown conversion
# ---------------------------------------------------------------------------

def _block_text(block: dict) -> str:
    """Concatenate all span text in a block, preserving intra-block line breaks."""
    lines = []
    for line in block.get("lines", []):
        line_text = "".join(span.get("text", "") for span in line.get("spans", []))
        lines.append(line_text)
    return "\n".join(lines)


def _blocks_to_markdown(blocks: list, repeated: set[str], body_size: float) -> str:
    """Convert a page's block list to Markdown.

    Heading rules (compared to body_size):
      ≥ 1.5× body_size          → # (h1)
      ≥ 1.2× body_size OR bold  → ## (h2)
      otherwise                  → plain paragraph
    """
    parts = []

    for block in blocks:
        if block["type"] != 0:   # skip image blocks
            continue

        text = _block_text(block).strip()
        if not text:
            continue

        # Drop detected headers/footers
        if text in repeated:
            continue

        # Drop standalone page numbers
        if re.fullmatch(r"[-–—]?\s*\d+\s*[-–—]?", text):
            continue

        max_size = _block_max_font_size(block)
        bold = _block_is_bold(block)

        if max_size >= body_size * 1.5:
            parts.append(f"# {text}")
        elif max_size >= body_size * 1.2 or (bold and max_size >= body_size):
            parts.append(f"## {text}")
        else:
            parts.append(text)

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Text cleaning (mirrors text_cleaner.py logic, applied to raw extracted text)
# ---------------------------------------------------------------------------

def _merge_broken_lines(text: str) -> str:
    """Merge mid-sentence line breaks (English and Chinese)."""
    # English: lowercase/comma end → lowercase start
    text = re.sub(r"(?<=[a-z,;])\n(?=[a-z])", " ", text)
    # Chinese: non-sentence-ending char → Chinese char
    text = re.sub(r"(?<=[^\n。！？；」）】\s])\n(?=[\u4e00-\u9fff])", "", text)
    return text


def _remove_duplicate_blank_lines(text: str) -> str:
    """Collapse 3+ consecutive newlines to two."""
    return re.sub(r"\n{3,}", "\n\n", text)


# ---------------------------------------------------------------------------
# CLI test entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m core.text_pipeline <path/to/file.pdf>")
        sys.exit(1)

    path = sys.argv[1]
    pages = extract_text_pdf(path)
    print(f"Extracted {len(pages)} pages\n")

    for p in pages[:5]:          # preview first 5 pages
        print(f"--- Page {p.page_number} ---")
        preview = p.markdown[:400] if p.markdown else "(empty)"
        print(preview)
        print()
