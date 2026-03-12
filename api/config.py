import os
from dotenv import load_dotenv

load_dotenv()

DATALAB_API_KEY = os.environ.get("DATALAB_API_KEY", "")
MARKER_API_URL  = os.environ.get("MARKER_API_URL", "https://www.datalab.to/api/v1/marker")
MARKER_SINGLE_CMD = os.environ.get("MARKER_SINGLE_CMD", "marker_single")
MARKER_SINGLE_ARGS = os.environ.get("MARKER_SINGLE_ARGS", "")
PADDLEOCR_VL_CMD = os.environ.get("PADDLEOCR_VL_CMD", os.environ.get("MINERU_CMD", "paddleocr"))
PADDLEOCR_VL_ARGS = os.environ.get("PADDLEOCR_VL_ARGS", os.environ.get("MINERU_ARGS", ""))
MINERU_CMD = os.environ.get("MINERU_CMD", "mineru")
MINERU_ARGS = os.environ.get("MINERU_ARGS", "")
RESEND_API_KEY  = os.environ.get("RESEND_API_KEY", "")
FROM_EMAIL      = os.environ.get("FROM_EMAIL", "delivery@paperflowing.com")
CORS_ORIGINS    = os.environ.get("CORS_ORIGINS", "*")
DATA_DIR        = os.environ.get("DATA_DIR", "./data/jobs")
DAILY_SUBMISSION_LIMIT = int(os.environ.get("DAILY_SUBMISSION_LIMIT", "300"))
MONTHLY_PAGE_LIMIT     = int(os.environ.get("MONTHLY_PAGE_LIMIT", "8000"))
PER_EMAIL_DAILY_LIMIT  = int(os.environ.get("PER_EMAIL_DAILY_LIMIT", "3"))
PER_USER_TRIAL_PAGE_LIMIT = int(os.environ.get("PER_USER_TRIAL_PAGE_LIMIT", "100"))
MAX_FILE_SIZE_MB       = int(os.environ.get("MAX_FILE_SIZE_MB", "15"))
MAX_PAGES              = int(os.environ.get("MAX_PAGES", "15"))
CONTACT_EMAIL          = os.environ.get("CONTACT_EMAIL", "support@paperflowing.com")
MCP_EMAIL_PREFIX       = os.environ.get("MCP_EMAIL_PREFIX", "mcp@")
PRO_EMAILS = {
    email.strip().lower()
    for email in os.environ.get("PRO_EMAILS", "").split(",")
    if email.strip()
}
