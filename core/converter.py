"""Main conversion orchestrator: PDF -> analysed layout -> clean text -> EPUB."""

from pathlib import Path

from core.layout_analyzer import analyze_layout
from core.ai_enhance import enhance_page
from core.text_cleaner import clean_text
from core.epub_builder import build_epub


def convert_pdf_to_epub(pdf_path: str, col_type: str = "Single column") -> str:
    """Convert a PDF file to EPUB and return the output path.

    Args:
        pdf_path: Path to the uploaded PDF.
        col_type: "Single column" or "Two columns".

    Returns:
        Path to the generated EPUB file.
    """
    two_column = col_type == "Two columns"

    # Step 1: Analyse layout with PaddleOCR (page images + text blocks)
    pages = analyze_layout(pdf_path, two_column=two_column)

    # Step 2 (optional): Enhance with Claude Vision
    enhanced_pages = [enhance_page(page) for page in pages]

    # Step 3: Clean text (merge broken lines, remove headers/footers)
    cleaned_pages = [clean_text(page) for page in enhanced_pages]

    # Step 4: Build EPUB
    output_path = str(Path(pdf_path).with_suffix(".epub")).replace("uploads", "outputs")
    build_epub(cleaned_pages, output_path)

    return output_path
