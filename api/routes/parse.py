import uuid
import asyncio
import tempfile
import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from api.services import marker, storage
from api.services.postprocess import postprocess_markdown
from api.models import UploadResponse, PaperStatus, PaperData
from api.errors import error_response, ErrorCode
from api.middleware.rate_limit import check_rate_limit

router = APIRouter()

MAX_PDF_MB = int(os.environ.get("MAX_PDF_MB", "50"))
MAX_PDF_BYTES = MAX_PDF_MB * 1024 * 1024

@router.post("/api/parse", response_model=UploadResponse)
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    # Rate limiting
    check_rate_limit(request)

    # Validate file type
    if not file.filename.endswith('.pdf'):
        error_response(400, ErrorCode.INVALID_PDF, "Only PDF files are supported")

    # Read file and check size
    pdf_bytes = await file.read()
    if len(pdf_bytes) > MAX_PDF_BYTES:
        error_response(
            413,
            ErrorCode.FILE_TOO_LARGE,
            f"PDF file exceeds maximum size of {MAX_PDF_MB}MB"
        )

    paper_id = str(uuid.uuid4())
    storage.save_task(paper_id, {"paper_id": paper_id, "status": "processing"})
    asyncio.create_task(_process(paper_id, pdf_bytes))
    return {"paper_id": paper_id, "status": "processing"}

@router.get("/api/parse/{paper_id}", response_model=PaperStatus)
async def get_status(paper_id: str):
    task = storage.load_task(paper_id)
    if not task:
        error_response(404, ErrorCode.NOT_FOUND, "Paper not found")
    return {
        "paper_id": paper_id,
        "status": task["status"],
        "error": task.get("error"),
        "error_code": task.get("error_code")
    }

@router.get("/api/paper/{paper_id}", response_model=PaperData)
async def get_paper(paper_id: str):
    task = storage.load_task(paper_id)
    if not task:
        error_response(404, ErrorCode.NOT_FOUND, "Paper not found")
    if task["status"] != "complete":
        raise HTTPException(400, f"Status is '{task['status']}'")
    return task["data"]

async def _process(paper_id: str, pdf_bytes: bytes):
    try:
        result = await marker.parse_pdf(pdf_bytes)
        data   = postprocess_markdown(result["markdown"], result["images"], result["metadata"])
        storage.update_task(paper_id, {"status": "complete", "data": data})
    except Exception as e:
        storage.update_task(paper_id, {
            "status": "error",
            "error": str(e),
            "error_code": ErrorCode.PARSE_FAILED.value
        })
