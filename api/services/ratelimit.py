import json
import threading
from pathlib import Path
from datetime import datetime, date
from api.config import DATA_DIR, DAILY_SUBMISSION_LIMIT, MONTHLY_PAGE_LIMIT, PER_EMAIL_DAILY_LIMIT

_lock = threading.Lock()
_usage_file = Path(DATA_DIR) / "usage.json"


def _load() -> dict:
    if _usage_file.exists():
        return json.loads(_usage_file.read_text())
    return {"daily": {}, "monthly": {}, "email_daily": {}}


def _save(data: dict):
    _usage_file.parent.mkdir(parents=True, exist_ok=True)
    _usage_file.write_text(json.dumps(data, indent=2))


def check_daily_limit() -> tuple[bool, int]:
    """Check if global daily submission limit is reached."""
    today = date.today().isoformat()
    with _lock:
        data = _load()
        count = data.get("daily", {}).get(today, 0)
        remaining = DAILY_SUBMISSION_LIMIT - count
        return remaining > 0, max(remaining, 0)


def check_monthly_pages() -> tuple[bool, int]:
    """Check if monthly page limit is reached."""
    month = datetime.now().strftime("%Y-%m")
    with _lock:
        data = _load()
        count = data.get("monthly", {}).get(month, 0)
        remaining = MONTHLY_PAGE_LIMIT - count
        return remaining > 0, max(remaining, 0)


def check_email_limit(email: str) -> tuple[bool, int]:
    """Check if per-email daily limit is reached."""
    today = date.today().isoformat()
    key = f"{email}:{today}"
    with _lock:
        data = _load()
        count = data.get("email_daily", {}).get(key, 0)
        remaining = PER_EMAIL_DAILY_LIMIT - count
        return remaining > 0, max(remaining, 0)


def record_submission(page_count: int = 0, email: str = ""):
    """Record a submission: global daily count, monthly pages, and per-email count."""
    today = date.today().isoformat()
    month = datetime.now().strftime("%Y-%m")
    with _lock:
        data = _load()
        if "daily" not in data:
            data["daily"] = {}
        if "monthly" not in data:
            data["monthly"] = {}
        if "email_daily" not in data:
            data["email_daily"] = {}
        data["daily"][today] = data["daily"].get(today, 0) + 1
        data["monthly"][month] = data["monthly"].get(month, 0) + page_count
        if email:
            key = f"{email}:{today}"
            data["email_daily"][key] = data["email_daily"].get(key, 0) + 1
        _save(data)
