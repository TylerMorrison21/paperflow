import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from api.routes.submit import router as submit_router
from api.routes.jobs import router as jobs_router
from api.config import CORS_ORIGINS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="PaperFlow API - Async Markdown Pipeline")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if CORS_ORIGINS == "*" else CORS_ORIGINS.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(submit_router)
app.include_router(jobs_router)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

@app.get("/")
def root():
    return FileResponse(FRONTEND_DIR / "app.html")


@app.get("/project")
def project_page():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/favicon.svg")
def favicon():
    return FileResponse(FRONTEND_DIR / "favicon.svg")

@app.get("/health")
def health():
    return {"status": "ok"}
