# Plan

## Current Task
None — ready to pick up next task.

---

## Done (continued)
- Add `core/pdf_detector.py` — detects text/scanned/mixed via PyMuPDF char count (>50 chars/page = text)
  - Modified: core/pdf_detector.py (new)
  - Tested on uploads/ sample PDFs → correctly returns "scanned" (0 chars/page)
- Add `core/text_pipeline.py` — zero-API-cost text extraction for text-based PDFs
  - Two-pass: pass 1 detects repeated header/footer text (≥40% pages) + body font size; pass 2 builds Markdown
  - Heading detection: ≥1.5× body size → `#`, ≥1.2× or bold → `##`
  - Modified: core/text_pipeline.py (new); uploads/test_text_based.pdf (test fixture)
  - Tested: 3-page PDF → headers removed, page numbers removed, h1 headings detected, body merged correctly
- Wire pdf_detector into converter.py
  - Modified: core/converter.py
  - text → extract_text_pdf (zero API cost); scanned/mixed → analyze_layout + clean_text (unchanged)
  - End-to-end test: test_text_based.pdf → outputs/test_text_based.epub (3 093 bytes), no API call
- Refactor `core/layout_analyzer.py` — switch primary OCR from Claude Vision to PaddleOCR cloud API
  - Modified: core/layout_analyzer.py
  - Chunks 5 pages/request as sub-PDFs; 2 s delay between chunks
  - Retry: up to 5 attempts, backoff 5/10/20/40/80 s
  - Checkpoint: {pdf}.checkpoint.json, resumes after crash
  - Claude Vision kept as ai_enhance=True flag (uses ANTHROPIC_API_KEY, deferred import)
  - openai/OpenRouter dependency removed; uses stdlib urllib.request
  - Imports and text-PDF end-to-end verified OK

---

## Done
- Initial scaffold commit
- Integrate PaddleOCR into core/layout_analyzer.py — Replaced with Claude Vision
  - Switched to Claude Vision API via OpenRouter (openai SDK)
  - Model: anthropic/claude-sonnet-4
  - Modified: core/layout_analyzer.py
  - Tested on 11-page Chinese PDF — works, returns Markdown
- Wire layout_analyzer into converter pipeline
  - `core/text_cleaner.py` — now cleans `page.markdown` instead of `page.raw_text`; added Chinese line-merge support; duplicate blank line removal
  - `core/epub_builder.py` — replaced placeholder with `markdown.markdown()` (tables extension); chapter splitting by `# ` headings with fallback to per-page; auto-detect `zh`/`en` language for EPUB metadata
  - `core/converter.py` — removed `enhance_page` step (redundant with Claude Vision); extracts title from PDF filename; auto-creates `outputs/` directory
  - Installed `markdown` dependency
  - Verified end-to-end: 11-page Chinese PDF → 13-chapter EPUB (16 KB), language auto-detected as `zh`

---

- Refine converter.py routing + clean scanned pipeline output
  - Modified: core/converter.py, core/text_cleaner.py
  - converter: fixed docstring, added ai_enhance param, routing log line
  - text_cleaner: added strip_loc_tokens() for <|LOC_*|> PaddleOCR artifacts; added _is_hallucination() (blanks pages where one token >40% of output — catches diagram hallucinations)
  - Tested: text PDF → 0.1s (free); scanned PDF → 0.3s (checkpoint hit, no API call)
  - Pages 2,3,10 blanked (hallucination); pages 3,7,11 LOC-stripped

## Next
- Improve title extraction (current hash-based filenames produce poor titles; consider extracting from first `# ` heading in content)
- Add CSS styling to EPUB (basic typography, margins, fonts)
- Error handling & retries for OpenRouter API calls
- Progress reporting / logging during conversion
- Web UI integration (Gradio/Streamlit front-end)
