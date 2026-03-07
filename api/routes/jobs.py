import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse

from api.config import DATA_DIR

router = APIRouter()


def _safe_job_dir(job_id: str) -> Path:
    """Resolve job directory, rejecting path traversal attempts."""
    if ".." in job_id or "/" in job_id or "\\" in job_id:
        raise HTTPException(status_code=400, detail="Invalid job_id")
    return Path(DATA_DIR) / job_id


def _read_job_error(job_dir: Path) -> str | None:
    error_path = job_dir / "error.json"
    if not error_path.exists():
        return None

    try:
        payload = json.loads(error_path.read_text(encoding="utf-8"))
    except Exception:
        return "PaperFlow failed to convert this PDF."

    message = payload.get("error")
    if isinstance(message, str) and message.strip():
        return message.strip()
    return "PaperFlow failed to convert this PDF."


@router.get("/api/jobs/{job_id}/status")
def job_status(job_id: str):
    """
    - 404 {"status": "not_found"}              directory does not exist
    - 200 {"status": "processing"}             dir exists, no paper/error file yet
    - 200 {"status": "done"}                   dir exists, paper.md present
    - 200 {"status": "failed", "error": "..."} dir exists, error.json present
    """
    job_dir = _safe_job_dir(job_id)

    if not job_dir.is_dir():
        return JSONResponse(status_code=404, content={"status": "not_found"})

    error_message = _read_job_error(job_dir)
    if error_message:
        return {"status": "failed", "error": error_message}

    if (job_dir / "paper.md").exists():
        return {"status": "done"}

    return {"status": "processing"}


@router.get("/api/jobs/{job_id}/result")
def job_result(job_id: str):
    """
    - 200 text/markdown                paper.md exists, returns content
    - 422 {"status":"failed", ...}     conversion failed, see error
    - 404 {"status":"not_ready"}       still processing
    """
    job_dir = _safe_job_dir(job_id)
    paper_md = job_dir / "paper.md"

    error_message = _read_job_error(job_dir)
    if error_message:
        return JSONResponse(
            status_code=422,
            content={"status": "failed", "error": error_message},
        )

    if not paper_md.exists():
        return JSONResponse(status_code=404, content={"status": "not_ready"})

    return PlainTextResponse(
        content=paper_md.read_text(encoding="utf-8"),
        media_type="text/markdown",
    )
