import asyncio
import io
import httpx
import logging
from typing import Any
from pypdf import PdfReader
from api.config import DATALAB_API_KEY, MARKER_API_URL

logger = logging.getLogger(__name__)

POLL_INTERVAL = 5
POLL_TIMEOUT  = 600

SCANNED_HINTS = (
    "image document",
    "scanned image",
    "no text layer",
)
SCANNED_PDF_ERROR = (
    "PaperFlow could not extract readable text from this PDF. "
    "It appears to be a scanned/image-only document, and OCR did not return usable text."
)

async def parse_pdf(pdf_bytes: bytes) -> dict:
    return await parse_pdf_with_api_key(pdf_bytes, api_key=DATALAB_API_KEY)


async def parse_pdf_with_api_key(pdf_bytes: bytes, api_key: str | None) -> dict:
    api_key = (api_key or "").strip()
    if not api_key:
        raise EnvironmentError("DATALAB_API_KEY is not set")

    logger.info(f"Starting PDF parse, size: {len(pdf_bytes)} bytes")

    # If the PDF likely has no text layer, skip directly to OCR.
    if _likely_no_text_layer(pdf_bytes):
        logger.info("No text layer detected in sampled pages; running OCR-first")
        ocr_result = await _parse_pdf_once(pdf_bytes, force_ocr=True, api_key=api_key)
        if _looks_like_scanned_output(ocr_result) or not (ocr_result.get("markdown") or "").strip():
            raise RuntimeError(SCANNED_PDF_ERROR)
        return ocr_result

    # Fast pass first for text-layer PDFs.
    result = await _parse_pdf_once(pdf_bytes, force_ocr=False, api_key=api_key)

    # Retry with OCR only when the response explicitly indicates image-only content.
    if _looks_like_scanned_output(result):
        logger.info("Detected scan/image-only output; retrying Marker with force_ocr=true")
        ocr_result = await _parse_pdf_once(pdf_bytes, force_ocr=True, api_key=api_key)
        if _looks_like_scanned_output(ocr_result) or not (ocr_result.get("markdown") or "").strip():
            raise RuntimeError(SCANNED_PDF_ERROR)
        return ocr_result

    return result


async def _parse_pdf_once(pdf_bytes: bytes, force_ocr: bool, api_key: str) -> dict:
    mode = "OCR" if force_ocr else "non-OCR"
    async with httpx.AsyncClient(timeout=60) as client:
        logger.info(f"Uploading PDF to Marker API ({mode})...")
        resp = await client.post(
            MARKER_API_URL,
            headers={"X-API-Key": api_key},
            files={"file": ("upload.pdf", pdf_bytes, "application/pdf")},
            data={
                "output_format": "markdown",
                "force_ocr": "true" if force_ocr else "false",
                "extract_images": "true",
            },
        )
        resp.raise_for_status()
        upload = resp.json()

    check_url = upload.get("request_check_url")
    if not check_url:
        raise RuntimeError(f"No request_check_url in Marker response: {upload}")

    logger.info(f"Polling status at: {check_url} ({mode})")

    deadline = asyncio.get_event_loop().time() + POLL_TIMEOUT
    poll_count = 0
    async with httpx.AsyncClient(timeout=60) as client:
        while asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(POLL_INTERVAL)
            poll_count += 1
            r = await client.get(check_url, headers={"X-API-Key": api_key})
            r.raise_for_status()
            data = r.json()
            status = data.get("status", "")
            logger.info(f"Poll #{poll_count} ({mode}): status={status}")

            if status == "complete":
                markdown = data.get("markdown") or ""
                images = data.get("images") or {}
                metadata = data.get("metadata") or {}
                logger.info(
                    f"Marker complete ({mode}): markdown_length={len(markdown)}, "
                    f"images={len(images)}, metadata_keys={list(metadata.keys())}"
                )
                return {
                    "markdown": markdown,
                    "images": images,
                    "metadata": metadata,
                }

            if status == "error":
                error_msg = data.get("error", "Unknown error")
                logger.error(f"Marker API error ({mode}): {error_msg}")
                raise RuntimeError(f"Marker API error: {data}")

    logger.error(f"Marker API timed out after {POLL_TIMEOUT}s ({poll_count} polls, {mode})")
    raise RuntimeError(f"Marker API timed out after {POLL_TIMEOUT}s")


def _looks_like_scanned_output(result: dict[str, Any]) -> bool:
    markdown = (result.get("markdown") or "").strip().lower()
    if not markdown:
        return True
    return any(hint in markdown for hint in SCANNED_HINTS)


def _likely_no_text_layer(pdf_bytes: bytes) -> bool:
    """
    Heuristic: sample up to 3 pages with pypdf text extraction.
    If almost no extractable text is found, treat as scanned/image-only.
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        sample_pages = min(len(reader.pages), 3)
        if sample_pages == 0:
            return False

        extracted_chars = 0
        for idx in range(sample_pages):
            text = reader.pages[idx].extract_text() or ""
            extracted_chars += len(text.strip())

        return extracted_chars < 40
    except Exception:
        return False
