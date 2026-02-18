"""Conversion orchestrator: detect PDF type → route to correct pipeline → build EPUB.

Text-based PDF  → text_pipeline   (PyMuPDF, zero API cost)
Scanned / mixed → layout_analyzer (SiliconFlow PaddleOCR-VL-1.5, paid API)
Both paths produce list[PageData] consumed by epub_builder.
"""

from pathlib import Path

from core.pdf_detector import detect_pdf_type
from core.text_pipeline import extract_text_pdf
from core.layout_analyzer import analyze_layout
from core.text_cleaner import clean_text
from core.epub_builder import build_epub


def convert_pdf_to_epub(
    pdf_path:   str,
    col_type:   str  = "Single column",
    ai_enhance: bool = False,
) -> str:
    """Convert a PDF file to EPUB and return the output path.

    Args:
        pdf_path:   Path to the uploaded PDF.
        col_type:   "Single column" or "Two columns" (hint for layout analysis).
        ai_enhance: If True, pass PaddleOCR output through Claude to fix errors.
                    Only used for scanned/mixed PDFs. Requires ANTHROPIC_API_KEY.

    Returns:
        Path to the generated .epub file.
    """
    two_column = col_type == "Two columns"

    # ── Step 1: detect and route ───────────────────────────────────────────────
    pdf_type = detect_pdf_type(pdf_path)
    print(f"[converter] PDF type: {pdf_type!r}  →  ", end="")

    if pdf_type == "text":
        print("text_pipeline (free)")
        # PyMuPDF direct extraction — no API call.
        # text_pipeline handles its own line-merging and header/footer removal.
        pages = extract_text_pdf(pdf_path)
    else:
        print(f"scanned_pipeline (PaddleOCR, ai_enhance={ai_enhance})")
        # SiliconFlow PaddleOCR-VL-1.5 — sends page images, returns Markdown.
        # clean_text strips <|LOC_*|> tokens, merges lines, drops hallucinations.
        raw_pages = analyze_layout(pdf_path, two_column=two_column,
                                   ai_enhance=ai_enhance)
        pages = [clean_text(p) for p in raw_pages]

    # ── Step 2: build EPUB ─────────────────────────────────────────────────────
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    title       = Path(pdf_path).stem.rsplit("_", 1)[0]
    output_path = str(output_dir / (Path(pdf_path).stem + ".epub"))
    build_epub(pages, output_path, title=title)

    return output_path
