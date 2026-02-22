import uuid
import asyncio
import tempfile
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from api.services import marker, storage
from api.services.postprocess import postprocess_markdown
from api.models import UploadResponse, PaperStatus, PaperData

router = APIRouter()

@router.post("/api/parse", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    paper_id = str(uuid.uuid4())
    pdf_bytes = await file.read()
    storage.save_task(paper_id, {"paper_id": paper_id, "status": "processing"})
    asyncio.create_task(_process(paper_id, pdf_bytes))
    return {"paper_id": paper_id, "status": "processing"}

@router.get("/api/parse/{paper_id}", response_model=PaperStatus)
async def get_status(paper_id: str):
    task = storage.load_task(paper_id)
    if not task:
        raise HTTPException(404, "Not found")
    return {"paper_id": paper_id, "status": task["status"], "error": task.get("error")}

@router.get("/api/paper/{paper_id}", response_model=PaperData)
async def get_paper(paper_id: str):
    task = storage.load_task(paper_id)
    if not task:
        raise HTTPException(404, "Not found")
    if task["status"] != "complete":
        raise HTTPException(400, f"Status is '{task['status']}'")
    return task["data"]

async def _process(paper_id: str, pdf_bytes: bytes):
    try:
        result = await marker.parse_pdf(pdf_bytes)
        data   = postprocess_markdown(result["markdown"], result["images"], result["metadata"])
        storage.update_task(paper_id, {"status": "complete", "data": data})
    except Exception as e:
        storage.update_task(paper_id, {"status": "error", "error": str(e)})
