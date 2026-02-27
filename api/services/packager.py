import base64
import logging
import re
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)


def sanitize_filename(title: str) -> str:
    """Convert paper title to safe folder name."""
    safe = re.sub(r'[^\w\s-]', '', title)
    safe = re.sub(r'\s+', '_', safe)
    return safe[:100] if safe else "paper"


def build_zip(job_dir: Path, title: str, markdown: str, images: dict) -> Path:
    """
    Create ZIP file with structure:
    Paper_Title/
    ├── paper.md
    └── images/
        ├── fig1.jpg
        └── ...
    """
    folder_name = sanitize_filename(title)
    zip_path = job_dir / f"{folder_name}.zip"

    images_dir = job_dir / "images"
    images_dir.mkdir(exist_ok=True)

    logger.info(f"Image keys from Marker: {list(images.keys())}")

    # Find all image references in the markdown before rewriting
    md_image_refs = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', markdown)
    logger.info(f"Image refs in markdown: {md_image_refs}")

    # Save images and build rewrite map
    for img_name, img_base64 in images.items():
        # Marker may return base64 with or without data URI prefix
        if ',' in img_base64 and img_base64.startswith('data:'):
            img_base64 = img_base64.split(',', 1)[1]

        img_data = base64.b64decode(img_base64)
        img_path = images_dir / img_name
        img_path.write_bytes(img_data)
        logger.info(f"Saved image: {img_name} ({len(img_data)} bytes)")

    # Rewrite all image references to images/filename
    # Marker markdown may reference images as just the key name, or with a path
    for img_name in images.keys():
        target = f"images/{img_name}"
        # Replace exact filename references: (filename) or (./filename)
        markdown = markdown.replace(f"({img_name})", f"({target})")
        markdown = markdown.replace(f"(./{img_name})", f"({target})")
        # Also handle if already has a path prefix that's not images/
        # e.g. (some/path/filename) → (images/filename)
        markdown = re.sub(
            rf'\((?:[^)]*[/\\])?{re.escape(img_name)}\)',
            f'({target})',
            markdown
        )

    # Create ZIP — flat structure, no wrapper folder
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("paper.md", markdown)
        for img_file in images_dir.glob("*"):
            if img_file.is_file():
                zf.write(img_file, f"images/{img_file.name}")

    logger.info(f"ZIP created: {zip_path}")
    return zip_path
