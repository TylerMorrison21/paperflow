import asyncio
import httpx
from api.config import DATALAB_API_KEY, MARKER_API_URL

POLL_INTERVAL = 5
POLL_TIMEOUT  = 600

async def parse_pdf(pdf_bytes: bytes) -> dict:
    if not DATALAB_API_KEY:
        raise EnvironmentError("DATALAB_API_KEY is not set")

    async with httpx.AsyncClient(timeout=60) as client:
        # 1. Upload
        resp = await client.post(
            MARKER_API_URL,
            headers={"X-API-Key": DATALAB_API_KEY},
            files={"file": ("upload.pdf", pdf_bytes, "application/pdf")},
            data={"output_format": "markdown", "force_ocr": "false", "extract_images": "true"},
        )
        resp.raise_for_status()
        upload = resp.json()

    check_url = upload.get("request_check_url")
    if not check_url:
        raise RuntimeError(f"No request_check_url in response: {upload}")

    # 2. Poll
    deadline = asyncio.get_event_loop().time() + POLL_TIMEOUT
    async with httpx.AsyncClient(timeout=60) as client:
        while asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(POLL_INTERVAL)
            r = await client.get(check_url, headers={"X-API-Key": DATALAB_API_KEY})
            r.raise_for_status()
            data = r.json()
            status = data.get("status", "")
            if status == "complete":
                return {
                    "markdown": data.get("markdown", ""),
                    "images":   data.get("images", {}),
                    "metadata": data.get("metadata", {}),
                }
            if status == "error":
                raise RuntimeError(f"Marker API error: {data}")

    raise RuntimeError(f"Marker API timed out after {POLL_TIMEOUT}s")
