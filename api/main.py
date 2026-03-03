import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/")
def root():
    return {
        "service": "paperflow",
        "ok": True,
        "health": "/health",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "ok"}
