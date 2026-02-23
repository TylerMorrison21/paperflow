# Task B: Backend P0 - Rate Limiting + File Size + Feedback + Error Codes

## Objectives
Implement rate limiting, file size validation, standardized error codes, and feedback API endpoint.

## 1. Error Code Conventions

Create `api/models/errors.py`:
```python
from enum import Enum
from fastapi import HTTPException

class ErrorCode(str, Enum):
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    RATE_LIMITED = "RATE_LIMITED"
    INVALID_PDF = "INVALID_PDF"
    PARSE_FAILED = "PARSE_FAILED"
    UPLOAD_FAILED = "UPLOAD_FAILED"
    NOT_FOUND = "NOT_FOUND"

def error_response(status_code: int, error_code: ErrorCode, message: str):
    """Standardized error response"""
    return HTTPException(
        status_code=status_code,
        detail={
            "error_code": error_code.value,
            "message": message
        }
    )
```

## 2. File Size Validation

Update `api/routes/parse.py`:
```python
import os
from fastapi import UploadFile, File
from api.models.errors import error_response, ErrorCode

MAX_PDF_MB = int(os.environ.get("MAX_PDF_MB", "50"))
MAX_PDF_BYTES = MAX_PDF_MB * 1024 * 1024

@router.post("/api/parse")
async def parse_pdf(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise error_response(400, ErrorCode.INVALID_PDF, "Only PDF files are supported")

    # Read file and check size
    contents = await file.read()
    if len(contents) > MAX_PDF_BYTES:
        raise error_response(
            413,
            ErrorCode.FILE_TOO_LARGE,
            f"PDF file exceeds maximum size of {MAX_PDF_MB}MB"
        )

    # Continue with processing...
```

## 3. Rate Limiting

Create `api/middleware/rate_limit.py`:
```python
from fastapi import Request
from collections import defaultdict
from datetime import datetime, timedelta
from api.models.errors import error_response, ErrorCode

# Simple in-memory rate limiter
# Format: {ip: [(timestamp1, timestamp2, ...)]}
request_log = defaultdict(list)

RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 10     # requests per window

def check_rate_limit(request: Request):
    """Check if IP has exceeded rate limit"""
    client_ip = request.client.host
    now = datetime.now()
    cutoff = now - timedelta(seconds=RATE_LIMIT_WINDOW)

    # Clean old requests
    request_log[client_ip] = [
        ts for ts in request_log[client_ip]
        if ts > cutoff
    ]

    # Check limit
    if len(request_log[client_ip]) >= RATE_LIMIT_MAX:
        raise error_response(
            429,
            ErrorCode.RATE_LIMITED,
            f"Rate limit exceeded. Maximum {RATE_LIMIT_MAX} requests per {RATE_LIMIT_WINDOW} seconds."
        )

    # Log this request
    request_log[client_ip].append(now)
```

Add to `api/routes/parse.py`:
```python
from api.middleware.rate_limit import check_rate_limit

@router.post("/api/parse")
async def parse_pdf(request: Request, file: UploadFile = File(...)):
    check_rate_limit(request)
    # ... rest of handler
```

## 4. Feedback API

Create `api/routes/feedback.py`:
```python
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
```

Register in `api/main.py`:
```python
from api.routes import parse, feedback

app.include_router(parse.router)
app.include_router(feedback.router)
```

## 5. Update Error Responses in Processing

Update `api/routes/parse.py` background task:
```python
async def process_paper_task(paper_id: str, pdf_bytes: bytes):
    try:
        # ... marker processing
        result = await parse_pdf_with_marker(pdf_bytes)
        # ... postprocessing
        save_task(paper_id, {
            "paper_id": paper_id,
            "status": "complete",
            "data": processed_data
        })
    except Exception as e:
        save_task(paper_id, {
            "paper_id": paper_id,
            "status": "error",
            "error_code": ErrorCode.PARSE_FAILED.value,
            "error": str(e)
        })
```

## 6. Environment Variables

Add to `api/.env`:
```
MAX_PDF_MB=50
FEEDBACK_DIR=./data/feedback
```

Add to Railway:
```bash
railway variables set MAX_PDF_MB=50
```

## 7. Update requirements.txt

No new dependencies needed - all using stdlib and existing packages.

## Testing

### File Size Limit
```bash
# Create a large dummy PDF (>50MB)
dd if=/dev/zero of=large.pdf bs=1M count=51

# Upload should return 413
curl -X POST -F "file=@large.pdf" http://localhost:8000/api/parse
# Expected: {"error_code": "FILE_TOO_LARGE", "message": "..."}
```

### Rate Limiting
```bash
# Send 11 requests rapidly
for i in {1..11}; do
  curl -X POST -F "file=@test.pdf" http://localhost:8000/api/parse
done
# 11th request should return 429
```

### Feedback API
```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"type": "bug", "message": "Test feedback", "paper_id": "123"}'
# Check data/feedback/ for JSON file
```

### Error Codes
```bash
# Invalid file type
curl -X POST -F "file=@test.txt" http://localhost:8000/api/parse
# Expected: {"error_code": "INVALID_PDF", ...}
```

## Success Criteria

✅ File size validation returns 413 with FILE_TOO_LARGE error code
✅ Rate limiting returns 429 with RATE_LIMITED error code
✅ Invalid PDF returns 400 with INVALID_PDF error code
✅ Processing errors return PARSE_FAILED error code
✅ Feedback API saves to data/feedback/{timestamp}.json
✅ All error responses follow standardized format
✅ Frontend receives error_code field for proper error handling
