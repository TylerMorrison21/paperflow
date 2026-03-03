import io
import uuid
import hashlib
import logging
import re
import zipfile
from pathlib import Path
from pypdf import PdfReader
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from api.models import SubmitResponse
from api.config import DATA_DIR, MAX_FILE_SIZE_MB, MAX_PAGES, CONTACT_EMAIL, MCP_EMAIL_PREFIX
from api.services.marker import parse_pdf
from api.services.postprocess import postprocess
from api.services.packager import build_zip
from api.services.emailer import send_paper_email, send_page_limit_email, send_failure_email
from api.services.ratelimit import check_daily_limit, check_monthly_pages, check_email_limit, record_submission

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory hash → job_dir mapping for dedup
_hash_cache: dict[str, str] = {}


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


def extract_title(metadata: dict, raw_markdown: str, original_filename: str) -> str:
    """
    Resolve paper title with three fallbacks:
    1. Marker API metadata.title
    2. First H1 heading in returned markdown
    3. Uploaded filename stem (spaces cleaned)
    """
    title = metadata.get("title", "").strip()
    if title and "untitled" not in title.lower():
        return title

    # First H1 in markdown
    for line in raw_markdown.splitlines():
        if line.startswith("# "):
            candidate = line[2:].strip()
            if candidate:
                return candidate

    # Filename fallback
    return Path(original_filename).stem.replace("_", " ").replace("-", " ")


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
            with zipfile.ZipFile(cached_zip, 'r') as zf:
                for name in zf.namelist():
                    if name.endswith('.md'):
                        md_content = zf.read(name).decode('utf-8', errors='ignore')
                        has_footnotes = re.search(r'\[\^\d+\]:', md_content) is not None
                        title = _extract_cached_title(md_content)
                        break

            if title and has_footnotes and 'untitled' not in title.lower():
                logger.info(f"Job {job_id}: Cache hit for {file_hash[:12]}…")
                if not email.startswith(MCP_EMAIL_PREFIX):
                    await send_paper_email(email, title, cached_zip)
                    logger.info(f"Job {job_id}: Cached result emailed to {email}")
                return
            else:
                # Stale cache — evict and reprocess
                logger.info(f"Job {job_id}: Stale cache evicted for {file_hash[:12]}…")
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

        record_submission(page_count, email=email)
        logger.info(f"Job {job_id}: Recorded {page_count} pages")

        # 3. Resolve title before postprocessing so frontmatter gets the real title
        title = extract_title(metadata, raw_markdown, original_filename)
        metadata["title"] = title
        logger.info(f"Job {job_id}: Resolved title: {title!r}")

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

        # 6. Send email (skipped for MCP submissions)
        if email.startswith(MCP_EMAIL_PREFIX):
            logger.info(f"Job {job_id}: MCP submission — skipping email")
        else:
            logger.info(f"Job {job_id}: Sending email to {email}")
            await send_paper_email(email, title, zip_path)
            logger.info(f"Job {job_id}: Email sent successfully")

    except Exception as e:
        logger.error(f"Job {job_id}: Failed with error: {e}", exc_info=True)
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
    email: str = Form(...)
):
    """
    Accept PDF + email, start async processing, return immediately.
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
        background_tasks.add_task(send_page_limit_email, email, file.filename, page_count)
        raise HTTPException(
            status_code=400,
            detail=f"Free playground is limited to {MAX_PAGES} pages for quality testing. For full documents, batch processing, or API access, contact {CONTACT_EMAIL}"
        )

    file_hash = hashlib.sha256(pdf_bytes).hexdigest()
    cached_zip = _find_cached_zip(file_hash)

    # Only enforce rate limits for new PDFs (not cached duplicates)
    if not cached_zip:
        allowed, _ = check_email_limit(email)
        if not allowed:
            raise HTTPException(status_code=429, detail="You've reached your daily limit of 3 papers. Come back tomorrow for more!")

        allowed, _ = check_daily_limit()
        if not allowed:
            raise HTTPException(status_code=429, detail="PaperFlow is experiencing high demand right now. Please try again in a few hours — we'll be ready for you!")

        allowed, _ = check_monthly_pages(page_count)
        if not allowed:
            raise HTTPException(status_code=429, detail="PaperFlow is experiencing high demand right now. Please try again in a few hours — we'll be ready for you!")

    logger.info(f"Job {job_id}: Received PDF ({len(pdf_bytes)} bytes) for {email} [cached={cached_zip is not None}]")

    # Start background processing
    background_tasks.add_task(process_job, job_id, pdf_bytes, email, file.filename, file_hash)

    return SubmitResponse(
        job_id=job_id,
        message="Processing. Check your inbox in 1-2 minutes."
    )
