"""File upload, download, and cleanup utilities."""

import os
import time
import uuid
from pathlib import Path

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_AGE_HOURS = 24


def save_upload(uploaded_file) -> str:
    """Save a Streamlit UploadedFile to the uploads directory.

    Args:
        uploaded_file: Streamlit UploadedFile object.

    Returns:
        Absolute path to the saved file.
    """
    filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
    path = UPLOAD_DIR / filename
    path.write_bytes(uploaded_file.getbuffer())
    return str(path)


def get_output_path(pdf_path: str) -> str:
    """Derive the EPUB output path from a PDF upload path.

    Args:
        pdf_path: Path to the uploaded PDF.

    Returns:
        Corresponding output path with .epub extension.
    """
    name = Path(pdf_path).stem + ".epub"
    return str(OUTPUT_DIR / name)


def cleanup_old_files() -> None:
    """Delete files older than MAX_AGE_HOURS from uploads/ and outputs/."""
    cutoff = time.time() - MAX_AGE_HOURS * 3600
    for directory in (UPLOAD_DIR, OUTPUT_DIR):
        for file in directory.iterdir():
            if file.is_file() and file.stat().st_mtime < cutoff:
                file.unlink()
