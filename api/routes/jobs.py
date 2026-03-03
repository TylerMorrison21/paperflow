from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from api.config import DATA_DIR

router = APIRouter()


def _safe_job_dir(job_id: str) -> Path:
    """Resolve job directory, rejecting path traversal attempts."""
    if '..' in job_id or '/' in job_id or '\\' in job_id:
        raise HTTPException(status_code=400, detail="Invalid job_id")
    return Path(DATA_DIR) / job_id


@router.get("/api/jobs/{job_id}/status")
def job_status(job_id: str):
    """
    - 404 {"status": "not_found"}   — directory does not exist
    - 200 {"status": "processing"}  — dir exists, paper.md missing
    - 200 {"status": "done"}        — dir exists, paper.md present
    """
    job_dir = _safe_job_dir(job_id)

    if not job_dir.is_dir():
        return JSONResponse(status_code=404, content={"status": "not_found"})

    if (job_dir / "paper.md").exists():
        return {"status": "done"}

    return {"status": "processing"}


@router.get("/api/jobs/{job_id}/result")
def job_result(job_id: str):
    """
    - 200 text/markdown  — paper.md exists, returns content
    - 404 {"status": "not_ready"}  — paper.md missing
    """
    job_dir = _safe_job_dir(job_id)
    paper_md = job_dir / "paper.md"

    if not paper_md.exists():
        return JSONResponse(status_code=404, content={"status": "not_ready"})

    return PlainTextResponse(
        content=paper_md.read_text(encoding="utf-8"),
        media_type="text/markdown",
    )
