from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.parse import router
from api.config import CORS_ORIGINS

app = FastAPI(title="PaperFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if CORS_ORIGINS == "*" else CORS_ORIGINS.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
