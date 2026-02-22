"""Marker API client — Datalab hosted API (datalab.to).

Endpoint  : POST https://www.datalab.to/api/v1/marker
Auth      : header X-API-Key: {DATALAB_API_KEY}
Transport : multipart/form-data, field ``file`` (PDF bytes)
            optional fields: output_format, force_ocr, extract_images

Flow      : 1. Upload PDF → receive {request_id, request_check_url}
            2. Poll request_check_url every 5 s until status == "complete"
            3. Return (markdown, images)

Docs      : https://www.datalab.to/app/marker
"""

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

POLL_INTERVAL   = 5          # seconds between status checks
POLL_TIMEOUT    = 600        # give up after 10 minutes
REQUEST_TIMEOUT = 60         # HTTP connect/read timeout per request

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def convert_pdf(pdf_path: str, paginate_output: bool = False) -> tuple[str, dict[str, str]]:
    """Upload *pdf_path* to the Datalab Marker API and return ``(markdown, images)``.

    Args:
        pdf_path:        Local path to the PDF file.
        paginate_output: Unused (kept for API compatibility with old client).

    Returns:
        A 2-tuple:
          - **markdown** – full-document Markdown string produced by Marker.
          - **images**   – dict mapping filename (e.g. ``"img_0.png"``) to
                           its raw base64-encoded bytes string.

    Raises:
        EnvironmentError: ``DATALAB_API_KEY`` is not set.
        RuntimeError:     Upload failed, polling timed out, or API returned an error.
    """
    api_key = os.environ.get("DATALAB_API_KEY", "").strip()
    if not api_key:
        raise EnvironmentError("DATALAB_API_KEY is not set")

    pdf_bytes = Path(pdf_path).read_bytes()

    # ── 1. Upload PDF ──────────────────────────────────────────────────────────
    upload_url = "https://www.datalab.to/api/v1/marker"
    boundary   = "----DatalabBoundary" + str(int(time.time() * 1000))

    def _field(name: str, value: str) -> bytes:
        return (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n"
        ).encode("utf-8")

    body = (
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="upload.pdf"\r\n'
            f"Content-Type: application/pdf\r\n\r\n"
        ).encode("ascii")
        + pdf_bytes + b"\r\n"
        + _field("output_format",  "markdown")
        + _field("force_ocr",      "false")
        + _field("extract_images", "true")
        + f"--{boundary}--\r\n".encode("ascii")
    )

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "X-API-Key":    api_key,
        "User-Agent":   _UA,
    }

    req = urllib.request.Request(upload_url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            upload_data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Upload HTTP {e.code}: {body_text}") from e

    request_check_url = upload_data.get("request_check_url")
    if not request_check_url:
        raise RuntimeError(f"Upload failed — no request_check_url in response: {upload_data}")

    print(f"[marker_client] submitted request_id={upload_data.get('request_id')}, polling…")

    # ── 2. Poll until complete ─────────────────────────────────────────────────
    deadline     = time.time() + POLL_TIMEOUT
    poll_headers = {"X-API-Key": api_key, "User-Agent": _UA}

    while time.time() < deadline:
        time.sleep(POLL_INTERVAL)

        poll_req = urllib.request.Request(request_check_url, headers=poll_headers, method="GET")
        with urllib.request.urlopen(poll_req, timeout=REQUEST_TIMEOUT) as resp:
            status_data = json.loads(resp.read())

        status = status_data.get("status", "")
        print(f"[marker_client] status={status}")

        if status == "complete":
            markdown = status_data.get("markdown", "")
            images   = status_data.get("images", {})
            # Save raw markdown alongside the PDF for inspection
            md_path = Path(pdf_path).with_suffix(".md")
            md_path.write_text(markdown, encoding="utf-8")
            print(f"[marker_client] done — {len(markdown)} chars, {len(images)} images")
            print(f"[marker_client] Markdown saved → {md_path}")
            return markdown, images

        if status == "error":
            raise RuntimeError(f"Marker API returned error: {status_data}")

    raise RuntimeError(
        f"Marker API polling timed out after {POLL_TIMEOUT}s "
        f"(request_check_url={request_check_url})"
    )
