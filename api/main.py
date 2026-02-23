from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.parse import router as parse_router
from api.routes.feedback import router as feedback_router
from api.config import CORS_ORIGINS

app = FastAPI(title="PaperFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if CORS_ORIGINS == "*" else CORS_ORIGINS.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parse_router)
app.include_router(feedback_router)

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
