from fastapi import Request
from collections import defaultdict
from datetime import datetime, timedelta
from api.errors import error_response, ErrorCode

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
        error_response(
            429,
            ErrorCode.RATE_LIMITED,
            f"Rate limit exceeded. Maximum {RATE_LIMIT_MAX} requests per {RATE_LIMIT_WINDOW} seconds."
        )

    # Log this request
    request_log[client_ip].append(now)
