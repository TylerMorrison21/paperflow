from fastapi import APIRouter, Request
from pydantic import BaseModel
import json
import os
from datetime import datetime

router = APIRouter()

FEEDBACK_DIR = os.environ.get("FEEDBACK_DIR", "./data/feedback")
os.makedirs(FEEDBACK_DIR, exist_ok=True)

class FeedbackRequest(BaseModel):
    type: str  # "bug", "feature", "general"
    message: str
    paper_id: str | None = None
    user_agent: str | None = None

@router.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest, request: Request):
    """Save user feedback to JSON file"""
    timestamp = datetime.now().isoformat()
    feedback_data = {
        "timestamp": timestamp,
        "type": feedback.type,
        "message": feedback.message,
        "paper_id": feedback.paper_id,
        "user_agent": feedback.user_agent or request.headers.get("user-agent"),
        "ip": request.client.host
    }

    # Save to file
    filename = f"{timestamp.replace(':', '-')}.json"
    filepath = os.path.join(FEEDBACK_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(feedback_data, f, indent=2, ensure_ascii=False)

    return {"success": True, "message": "Feedback received. Thank you!"}
