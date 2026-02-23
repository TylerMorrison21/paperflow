import asyncio
import httpx
import logging
from api.config import DATALAB_API_KEY, MARKER_API_URL

logger = logging.getLogger(__name__)

POLL_INTERVAL = 5
POLL_TIMEOUT  = 600

async def parse_pdf(pdf_bytes: bytes) -> dict:
    if not DATALAB_API_KEY:
        raise EnvironmentError("DATALAB_API_KEY is not set")

    logger.info(f"Starting PDF parse, size: {len(pdf_bytes)} bytes")

    async with httpx.AsyncClient(timeout=60) as client:
        # 1. Upload
        logger.info("Uploading PDF to Marker API...")
        resp = await client.post(
            MARKER_API_URL,
            headers={"X-API-Key": DATALAB_API_KEY},
            files={"file": ("upload.pdf", pdf_bytes, "application/pdf")},
            data={"output_format": "markdown", "force_ocr": "false", "extract_images": "true"},
        )
        resp.raise_for_status()
        upload = resp.json()
        logger.info(f"Upload response: {upload}")

    check_url = upload.get("request_check_url")
    if not check_url:
        raise RuntimeError(f"No request_check_url in response: {upload}")

    logger.info(f"Polling status at: {check_url}")

    # 2. Poll
    deadline = asyncio.get_event_loop().time() + POLL_TIMEOUT
    poll_count = 0
    async with httpx.AsyncClient(timeout=60) as client:
        while asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(POLL_INTERVAL)
            poll_count += 1
            r = await client.get(check_url, headers={"X-API-Key": DATALAB_API_KEY})
            r.raise_for_status()
            data = r.json()
            status = data.get("status", "")
            logger.info(f"Poll #{poll_count}: status={status}")

            if status == "complete":
                logger.info("Marker API processing complete")
                markdown = data.get("markdown", "")
                images = data.get("images", {})
                metadata = data.get("metadata", {})
                logger.info(f"Result: markdown_length={len(markdown) if markdown else 0}, images={len(images)}, metadata_keys={list(metadata.keys())}")
                return {
                    "markdown": markdown,
                    "images": images,
                    "metadata": metadata,
                }
            if status == "error":
                error_msg = data.get("error", "Unknown error")
                logger.error(f"Marker API error: {error_msg}")
                raise RuntimeError(f"Marker API error: {data}")

    logger.error(f"Marker API timed out after {POLL_TIMEOUT}s ({poll_count} polls)")
    raise RuntimeError(f"Marker API timed out after {POLL_TIMEOUT}s")
