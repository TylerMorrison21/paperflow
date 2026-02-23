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
    raise HTTPException(
        status_code=status_code,
        detail={
            "error_code": error_code.value,
            "message": message
        }
    )
