"""Layout analysis: SiliconFlow / PaddleOCR-VL-1.5 (primary) + optional Claude Vision.

Primary path  — SiliconFlow OpenAI-compatible API (SILICONFLOW_API_KEY)
                model: PaddlePaddle/PaddleOCR-VL-1.5
Enhancement   — Claude Vision text cleanup (ANTHROPIC_API_KEY, opt-in via ai_enhance=True)

Chunking: 5 pages per chunk, 2 s delay between chunks.
Retry:    up to 5 attempts per page, exponential backoff (5 s, 10 s, 20 s, 40 s, 80 s).
Checkpoint: results cached to <pdf>.checkpoint.json so a crashed run can resume.
"""

import base64
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF

# ── constants ──────────────────────────────────────────────────────────────────
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
PADDLE_MODEL        = "PaddlePaddle/PaddleOCR-VL-1.5"
CHUNK_SIZE          = 5      # pages per chunk before rate-limit sleep
CHUNK_DELAY         = 2.0    # seconds between chunks
MAX_RETRIES         = 5      # retry attempts per page
REQUEST_TIMEOUT     = 120    # seconds per HTTP request

EXTRACT_PROMPT = (
    "Extract all text from this page image. "
    "Preserve the layout structure as Markdown: "
    "use headings (#, ##, etc.), bullet lists, tables, and paragraphs as appropriate. "
    "Return ONLY the Markdown text, no commentary."
)

ENHANCE_PROMPT = (
    "Below is OCR-extracted text from one page of a PDF. "
    "Fix OCR errors, merge broken lines into proper paragraphs, "
    "and return clean Markdown. "
    "Remove any headers or footers if the OCR missed them. "
    "Return ONLY the corrected Markdown, no commentary.\n\n"
    "OCR text:\n{ocr_text}"
)


# ── data model (shared by converter, text_pipeline, epub_builder) ──────────────
@dataclass
class PageData:
    """Represents extracted data for a single PDF page."""

    page_number: int
    image_bytes: bytes       = b""
    text_blocks: list[dict]  = field(default_factory=list)
    raw_text:    str         = ""
    markdown:    str         = ""


# ── SiliconFlow / PaddleOCR API ────────────────────────────────────────────────

def _ocr_page(image_bytes: bytes, api_key: str) -> str:
    """Send one page image to SiliconFlow PaddleOCR-VL-1.5 and return Markdown."""
    b64 = base64.standard_b64encode(image_bytes).decode("ascii")
    payload = json.dumps({
        "model": PADDLE_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url",
                 "image_url": {"url": f"data:image/png;base64,{b64}"}},
                {"type": "text", "text": EXTRACT_PROMPT},
            ],
        }],
        "max_tokens": 4096,
    }).encode("utf-8")

    headers = {
        "Authorization":  f"Bearer {api_key}",
        "Content-Type":   "application/json",
    }

    req = urllib.request.Request(
        SILICONFLOW_API_URL, data=payload, headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        data = json.loads(resp.read())

    return data["choices"][0]["message"]["content"]


def _ocr_page_with_retry(image_bytes: bytes, api_key: str, page_num: int) -> str:
    """Call _ocr_page with exponential backoff on failure."""
    for attempt in range(MAX_RETRIES):
        try:
            return _ocr_page(image_bytes, api_key)
        except Exception as exc:
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(
                    f"Page {page_num}: SiliconFlow API failed after "
                    f"{MAX_RETRIES} attempts: {exc}"
                ) from exc
            wait = (2 ** attempt) * 5
            print(f"    [retry {attempt + 1}/{MAX_RETRIES - 1}] "
                  f"page {page_num}, waiting {wait}s — {exc}")
            time.sleep(wait)
    return ""  # unreachable


# ── optional Claude Vision enhancement ────────────────────────────────────────

def _enhance_with_claude(ocr_text: str, api_key: str) -> str:
    """Pass OCR text through Claude to fix errors and reformat as clean Markdown."""
    import anthropic  # deferred: only loaded when ai_enhance=True

    client = anthropic.Anthropic(api_key=api_key)
    resp   = client.messages.create(
        model      = "claude-sonnet-4-6",
        max_tokens = 4096,
        messages   = [{"role": "user",
                       "content": ENHANCE_PROMPT.format(ocr_text=ocr_text)}],
    )
    return resp.content[0].text


# ── checkpoint helpers ─────────────────────────────────────────────────────────

def _checkpoint_path(pdf_path: str) -> Path:
    return Path(pdf_path).with_suffix(".checkpoint.json")


def _load_checkpoint(pdf_path: str) -> dict[int, str]:
    path = _checkpoint_path(pdf_path)
    if path.exists():
        return {int(k): v for k, v in json.loads(
            path.read_text(encoding="utf-8")).items()}
    return {}


def _save_checkpoint(pdf_path: str, completed: dict[int, str]) -> None:
    _checkpoint_path(pdf_path).write_text(
        json.dumps(completed, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ── public API ─────────────────────────────────────────────────────────────────

def analyze_layout(
    pdf_path:   str,
    two_column: bool = False,
    ai_enhance: bool = False,
) -> list[PageData]:
    """Extract page content via SiliconFlow PaddleOCR-VL-1.5 with chunking and checkpoints.

    Args:
        pdf_path:   Path to the PDF file.
        two_column: Informational only (PaddleOCR auto-detects columns).
        ai_enhance: If True, pipe OCR output through Claude to fix errors.
                    Requires ANTHROPIC_API_KEY env var.

    Returns:
        List of PageData objects (one per page), same format as text_pipeline.
    """
    api_key = os.environ["SILICONFLOW_API_KEY"]

    anthropic_key = ""
    if ai_enhance:
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not anthropic_key:
            raise EnvironmentError("ANTHROPIC_API_KEY required when ai_enhance=True")

    doc         = fitz.open(pdf_path)
    total_pages = len(doc)

    # ── resume from checkpoint ────────────────────────────────────────────────
    completed: dict[int, str] = _load_checkpoint(pdf_path)
    pending   = [i for i in range(total_pages) if (i + 1) not in completed]
    chunks    = [pending[i:i + CHUNK_SIZE] for i in range(0, len(pending), CHUNK_SIZE)]

    print(f"[analyze_layout] {total_pages} pages total, "
          f"{len(completed)} cached, {len(chunks)} chunks to process")

    # ── process chunks ────────────────────────────────────────────────────────
    for chunk_idx, chunk in enumerate(chunks):
        print(f"  chunk {chunk_idx + 1}/{len(chunks)}: "
              f"pages {[i + 1 for i in chunk]}")

        for page_idx in chunk:
            page_num  = page_idx + 1
            pix       = doc[page_idx].get_pixmap()
            img_bytes = pix.tobytes("png")

            md = _ocr_page_with_retry(img_bytes, api_key, page_num)

            if ai_enhance and md.strip():
                md = _enhance_with_claude(md, anthropic_key)

            completed[page_num] = md
            print(f"    page {page_num}: {len(md)} chars")

        _save_checkpoint(pdf_path, completed)

        if chunk_idx < len(chunks) - 1:
            time.sleep(CHUNK_DELAY)

    # ── assemble PageData in page order ──────────────────────────────────────
    pages = [
        PageData(
            page_number = i + 1,
            raw_text    = doc[i].get_text(),
            markdown    = completed.get(i + 1, ""),
        )
        for i in range(total_pages)
    ]
    doc.close()
    return pages
