import io
import json
import shutil
import uuid
import hashlib
import logging
import re
import zipfile
from datetime import datetime
from pathlib import Path
from pypdf import PdfReader
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from api.models import SubmitResponse
from api.config import DATA_DIR, MAX_FILE_SIZE_MB, MAX_PAGES, MCP_EMAIL_PREFIX
from api.services.marker import parse_pdf
from api.services.postprocess import postprocess
from api.services.packager import build_zip
from api.services.emailer import send_paper_email, send_page_limit_email, send_failure_email
from api.services.ratelimit import check_daily_limit, check_monthly_pages, check_email_limit, record_submission

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory hash 鈫?job_dir mapping for dedup
_hash_cache: dict[str, str] = {}

_TITLE_BLACKLIST = {
    "abstract",
    "introduction",
    "references",
    "bibliography",
    "contents",
    "table of contents",
}

_AFFILIATION_HINTS = (
    "university",
    "institute",
    "department",
    "school",
    "college",
    "laboratory",
    "laboratoire",
    "lab",
    "hospital",
    "faculty",
    "research center",
)


def _build_hash_cache():
    """Scan existing job dirs on startup to populate hash cache."""
    data_dir = Path(DATA_DIR)
    if not data_dir.exists():
        return
    for job_dir in data_dir.iterdir():
        if not job_dir.is_dir():
            continue
        pdf_path = job_dir / "input.pdf"
        zip_files = list(job_dir.glob("*.zip"))
        if pdf_path.exists() and zip_files:
            file_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
            _hash_cache[file_hash] = str(job_dir)


# Build cache on module load
_build_hash_cache()


def _find_cached_zip(file_hash: str) -> Path | None:
    """Return cached ZIP path if this PDF was already processed."""
    job_dir_str = _hash_cache.get(file_hash)
    if not job_dir_str:
        return None
    job_dir = Path(job_dir_str)
    zip_files = list(job_dir.glob("*.zip"))
    if zip_files and zip_files[0].exists():
        return zip_files[0]
    return None


def _extract_cached_title(md_content: str) -> str | None:
    """Extract title from YAML frontmatter first, then fallback to first H1."""
    if md_content.startswith("---"):
        lines = md_content.splitlines()
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if line.lower().startswith("title:"):
                value = line.split(":", 1)[1].strip().strip('"').strip("'")
                if value:
                    return value

    for line in md_content.splitlines():
        if line.startswith("# "):
            candidate = line[2:].strip()
            if candidate:
                return candidate
    return None


def _clean_inline_markdown(text: str) -> str:
    cleaned = re.sub(r"<sup>.*?</sup>", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = cleaned.replace("*", "").replace("`", "").replace("_", "")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip().strip('"').strip("'")


def _is_valid_title_candidate(candidate: str) -> bool:
    if not candidate:
        return False
    lowered = candidate.lower()
    if "untitled" in lowered:
        return False
    if lowered in _TITLE_BLACKLIST:
        return False
    if len(candidate) < 6 or len(candidate) > 240:
        return False
    if "@" in candidate:
        return False
    return True


def _extract_title_from_markdown(raw_markdown: str) -> str | None:
    lines = raw_markdown.splitlines()

    for line in lines[:120]:
        match = re.match(r"^\s{0,3}#{1,3}\s+(.+?)\s*$", line)
        if not match:
            continue
        candidate = _clean_inline_markdown(match.group(1))
        if _is_valid_title_candidate(candidate):
            return candidate

    for line in lines[:60]:
        candidate = _clean_inline_markdown(line)
        if not candidate:
            continue
        lowered = candidate.lower()
        if lowered.startswith(("abstract", "keywords", "introduction")):
            break
        if re.match(r"^\d+(\.\d+)*\s", candidate):
            continue
        if any(hint in lowered for hint in _AFFILIATION_HINTS):
            continue
        if _is_valid_title_candidate(candidate):
            return candidate

    return None


def _coerce_author_items(value) -> list[str]:
    if value is None:
        return []

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []
        if "," in raw or ";" in raw or " and " in raw.lower():
            normalized = re.sub(r"\s+and\s+", ",", raw, flags=re.IGNORECASE)
            return [part.strip() for part in re.split(r"[;,]", normalized) if part.strip()]
        return [raw]

    if isinstance(value, (list, tuple, set)):
        items: list[str] = []
        for entry in value:
            if isinstance(entry, str):
                items.extend(_coerce_author_items(entry))
                continue
            if isinstance(entry, dict):
                for key in ("name", "full_name", "author", "display_name"):
                    raw_name = entry.get(key)
                    if isinstance(raw_name, str) and raw_name.strip():
                        items.append(raw_name.strip())
                        break
        return items

    return []


def _normalize_author_name(raw: str) -> str:
    cleaned = _clean_inline_markdown(raw)
    cleaned = re.sub(r"\([^)]*\)", "", cleaned)
    cleaned = re.sub(r"\b\d{1,2}\b", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,;:")
    return cleaned


def _looks_like_author_name(name: str) -> bool:
    if not name:
        return False
    if "@" in name:
        return False
    lowered = name.lower()
    if any(hint in lowered for hint in _AFFILIATION_HINTS):
        return False
    if re.search(r"https?://|www\.", lowered):
        return False
    if len(name) < 3 or len(name) > 80:
        return False

    tokens = name.split()
    if len(tokens) > 6:
        return False
    if not re.search(r"[A-Za-z]", name):
        return False
    if name.isupper() and len(tokens) > 2:
        return False
    return True


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen = set()
    out = []
    for value in values:
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


def extract_authors(metadata: dict, raw_markdown: str, title: str) -> list[str]:
    for key in ("authors", "author_names", "author", "creators"):
        if key not in metadata:
            continue
        raw_items = _coerce_author_items(metadata.get(key))
        normalized = [_normalize_author_name(item) for item in raw_items]
        filtered = [name for name in normalized if _looks_like_author_name(name)]
        filtered = _dedupe_preserve_order(filtered)
        if filtered:
            return filtered[:20]

    lines = raw_markdown.splitlines()
    title_idx = None

    title_norm = _clean_inline_markdown(title).casefold()
    for idx, line in enumerate(lines[:140]):
        line_norm = _clean_inline_markdown(line).casefold()
        if line_norm and line_norm == title_norm:
            title_idx = idx
            break

    if title_idx is None:
        for idx, line in enumerate(lines[:140]):
            if re.match(r"^\s{0,3}#{1,3}\s+.+", line):
                title_idx = idx
                break

    if title_idx is None:
        return []

    candidates: list[str] = []
    blank_streak = 0
    for line in lines[title_idx + 1:title_idx + 45]:
        stripped = line.strip()
        if not stripped:
            blank_streak += 1
            if blank_streak >= 2 and candidates:
                break
            continue

        blank_streak = 0
        if re.match(r"^\s*#{1,6}\s+", stripped):
            break

        cleaned = _clean_inline_markdown(stripped)
        lowered = cleaned.lower()
        if lowered.startswith(("abstract", "keywords", "introduction")):
            break
        if "@" in cleaned:
            continue
        if any(hint in lowered for hint in _AFFILIATION_HINTS):
            continue

        parts = _coerce_author_items(cleaned)
        for part in parts:
            name = _normalize_author_name(part)
            if _looks_like_author_name(name):
                candidates.append(name)

    return _dedupe_preserve_order(candidates)[:20]


def _normalize_date_value(value) -> str | None:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        year = int(value)
        if 1900 <= year <= 2100:
            return f"{year}-01-01"
        return None

    if not isinstance(value, str):
        return None

    raw = value.strip()
    if not raw:
        return None

    if re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
        return raw
    if re.match(r"^\d{4}/\d{2}/\d{2}$", raw):
        return raw.replace("/", "-")
    if re.match(r"^\d{4}$", raw):
        return f"{raw}-01-01"

    for fmt in ("%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass

    match = re.search(r"\b(19|20)\d{2}[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b", raw)
    if match:
        return match.group(0).replace("/", "-")

    month_match = re.search(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+(19|20)\d{2}\b",
        raw,
        flags=re.IGNORECASE,
    )
    if month_match:
        try:
            return datetime.strptime(month_match.group(0), "%B %d, %Y").strftime("%Y-%m-%d")
        except ValueError:
            pass

    return None


def extract_date(metadata: dict, raw_markdown: str) -> str | None:
    for key in ("date", "published", "publication_date", "published_date", "issued", "created", "year"):
        normalized = _normalize_date_value(metadata.get(key))
        if normalized:
            return normalized

    top_block = "\n".join(raw_markdown.splitlines()[:100])
    return _normalize_date_value(top_block)


def extract_title(metadata: dict, raw_markdown: str, original_filename: str) -> str:
    """
    Resolve paper title with fallbacks:
    1. Marker metadata title-like keys
    2. Heading/lead-line extraction from markdown
    3. Uploaded filename stem
    """
    for key in ("title", "document_title", "paper_title"):
        title = metadata.get(key, "")
        if isinstance(title, str):
            candidate = _clean_inline_markdown(title)
            if _is_valid_title_candidate(candidate):
                return candidate

    markdown_title = _extract_title_from_markdown(raw_markdown)
    if markdown_title:
        return markdown_title

    fallback = Path(original_filename).stem.replace("_", " ").replace("-", " ")
    fallback = re.sub(r"\s+", " ", fallback).strip()
    return fallback or "Untitled Paper"


async def process_job(job_id: str, pdf_bytes: bytes, email: str, original_filename: str, file_hash: str):
    """
    Background task: process PDF and email result.
    """
    job_dir = Path(DATA_DIR) / job_id

    try:
        # Check for cached result (duplicate PDF)
        cached_zip = _find_cached_zip(file_hash)
        if cached_zip:
            # Validate cache: must have footnotes and valid title
            title = None
            has_footnotes = False
            md_content = None
            with zipfile.ZipFile(cached_zip, 'r') as zf:
                for name in zf.namelist():
                    if name.endswith('.md'):
                        md_content = zf.read(name).decode('utf-8', errors='ignore')
                        has_footnotes = re.search(r'\[\^\d+\]:', md_content) is not None
                        title = _extract_cached_title(md_content)
                        break

            if title and has_footnotes and md_content and 'untitled' not in title.lower():
                logger.info(f"Job {job_id}: Cache hit for {file_hash[:12]}")
                cached_copy = job_dir / cached_zip.name
                shutil.copy2(cached_zip, cached_copy)
                (job_dir / "paper.md").write_text(md_content, encoding="utf-8")
                if not email.startswith(MCP_EMAIL_PREFIX):
                    await send_paper_email(email, title, cached_copy)
                    logger.info(f"Job {job_id}: Cached result emailed to {email}")
                return

            logger.info(f"Job {job_id}: Stale cache evicted for {file_hash[:12]}")
            _hash_cache.pop(file_hash, None)

        logger.info(f"Job {job_id}: Starting processing for {email}")

        # 1. Save PDF
        pdf_path = job_dir / "input.pdf"
        pdf_path.write_bytes(pdf_bytes)
        logger.info(f"Job {job_id}: PDF saved")

        # 2. Call Marker API
        logger.info(f"Job {job_id}: Calling Marker API")
        result = await parse_pdf(pdf_bytes)
        raw_markdown = result["markdown"]
        images = result["images"]
        metadata = result["metadata"]
        logger.info(f"Job {job_id}: Marker API complete")

        # Record usage (page count from metadata, fallback to 1)
        raw_page_count = metadata.get("pages", 1)
        try:
            page_count = max(int(raw_page_count), 1)
        except (TypeError, ValueError):
            page_count = 1

        record_submission(
            page_count,
            email="" if email.startswith(MCP_EMAIL_PREFIX) else email,
        )
        logger.info(f"Job {job_id}: Recorded {page_count} pages")

        # 3. Resolve metadata quality before postprocessing/frontmatter
        title = extract_title(metadata, raw_markdown, original_filename)
        authors = extract_authors(metadata, raw_markdown, title)
        published_date = extract_date(metadata, raw_markdown)
        source = metadata.get("source") or original_filename

        metadata["title"] = title
        metadata["authors"] = authors
        metadata["date"] = published_date
        metadata["source"] = source
        logger.info(
            f"Job {job_id}: Resolved metadata title={title!r}, "
            f"authors={len(authors)}, date={published_date!r}"
        )

        # 4. Postprocess markdown
        logger.info(f"Job {job_id}: Postprocessing markdown")
        enhanced_md = postprocess(raw_markdown, images, metadata)

        # Save enhanced markdown
        md_path = job_dir / "paper.md"
        md_path.write_text(enhanced_md, encoding="utf-8")
        logger.info(f"Job {job_id}: Markdown saved")

        # 5. Build ZIP
        logger.info(f"Job {job_id}: Building ZIP")
        zip_path = build_zip(job_dir, title, enhanced_md, images)
        logger.info(f"Job {job_id}: ZIP created at {zip_path}")

        # Register in hash cache
        _hash_cache[file_hash] = str(job_dir)
        # 6. Send email (skipped for local/MCP submissions)
        if email.startswith(MCP_EMAIL_PREFIX):
            logger.info(f"Job {job_id}: local/MCP submission, skipping email")
        else:
            logger.info(f"Job {job_id}: Sending email to {email}")
            await send_paper_email(email, title, zip_path)
            logger.info(f"Job {job_id}: Email sent successfully")

    except Exception as e:
        logger.error(f"Job {job_id}: Failed with error: {e}", exc_info=True)
        (job_dir / "error.json").write_text(
            json.dumps({"error": str(e)}, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )
        if not email.startswith(MCP_EMAIL_PREFIX):
            try:
                await send_failure_email(email, original_filename)
            except Exception:
                logger.error(f"Job {job_id}: Failed to send failure email to {email}", exc_info=True)
        return


@router.post("/api/submit", response_model=SubmitResponse)
async def submit_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    email: str = Form("mcp@paperflow.local")
):
    """
    Accept a PDF, start async processing, and return a job ID immediately.
    Email is optional for self-hosted/local use.
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Create job directory
    job_dir = Path(DATA_DIR) / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    # Read PDF bytes and check file size
    pdf_bytes = await file.read()
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if len(pdf_bytes) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB.")

    # Count pages before calling Marker API
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        page_count = len(reader.pages)
    except Exception:
        page_count = 0  # let Marker handle corrupt PDFs

    if page_count > MAX_PAGES:
        logger.info(f"Job {job_id}: {page_count} pages exceeds limit of {MAX_PAGES}, sending limit email")
        if not email.startswith(MCP_EMAIL_PREFIX):
            background_tasks.add_task(send_page_limit_email, email, file.filename, page_count)
        raise HTTPException(
            status_code=400,
            detail=(
                f"This PaperFlow instance is configured with a {MAX_PAGES}-page limit. "
                f"Increase MAX_PAGES in your .env if you want to process larger PDFs."
            )
        )

    file_hash = hashlib.sha256(pdf_bytes).hexdigest()
    cached_zip = _find_cached_zip(file_hash)

    # Only enforce rate limits for new PDFs (not cached duplicates)
    if not cached_zip:
        if not email.startswith(MCP_EMAIL_PREFIX):
            allowed, _ = check_email_limit(email)
            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail=(
                        "This PaperFlow instance has reached its configured per-email daily limit. "
                        "Increase PER_EMAIL_DAILY_LIMIT in your .env if needed."
                    ),
                )

        allowed, _ = check_daily_limit()
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=(
                    "This PaperFlow instance has reached its configured daily submission limit. "
                    "Increase DAILY_SUBMISSION_LIMIT in your .env if needed."
                ),
            )

        allowed, _ = check_monthly_pages(page_count)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=(
                    "This PaperFlow instance has reached its configured monthly page limit. "
                    "Increase MONTHLY_PAGE_LIMIT in your .env if needed."
                ),
            )

    logger.info(f"Job {job_id}: Received PDF ({len(pdf_bytes)} bytes) for {email} [cached={cached_zip is not None}]")

    # Start background processing
    background_tasks.add_task(process_job, job_id, pdf_bytes, email, file.filename, file_hash)

    return SubmitResponse(
        job_id=job_id,
        message=(f"Processing. Poll /api/jobs/{job_id}/status, then fetch /api/jobs/{job_id}/result or /api/jobs/{job_id}/package.")
    )

