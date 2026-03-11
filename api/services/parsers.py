from __future__ import annotations

from api.config import DATALAB_API_KEY
from api.services import marker, pymupdf_parser


def list_parsers() -> list[dict]:
    parser_rows = [
        {
            "id": "pymupdf",
            "label": "PyMuPDF Local",
            "configured": pymupdf_parser.parser_available(),
            "recommended": True,
            "speed": "Fastest",
            "quality": "Lower",
            "setup": "No API key needed",
            "description": "Fastest and simplest local option. Best for quick free conversions.",
        },
        {
            "id": "marker_api",
            "label": "Marker API (Datalab)",
            "configured": bool(DATALAB_API_KEY),
            "recommended": True,
            "speed": "Medium",
            "quality": "Best",
            "setup": "Requires DATALAB_API_KEY",
            "description": "Best overall quality for footnotes, figures, equations, and metadata.",
        },
        {
            "id": "marker_local",
            "label": "Marker Self-Hosted",
            "configured": False,
            "recommended": False,
            "speed": "Depends",
            "quality": "Best",
            "setup": "Not wired yet",
            "description": "Bring your own local Marker deployment and adapter.",
        },
        {
            "id": "mineru",
            "label": "MinerU",
            "configured": False,
            "recommended": False,
            "speed": "Depends",
            "quality": "Mixed",
            "setup": "Not wired yet",
            "description": "Possible future adapter for users who already run MinerU.",
        },
    ]

    default_id = "pymupdf"
    if not parser_rows[0]["configured"] and parser_rows[1]["configured"]:
        default_id = "marker_api"

    for row in parser_rows:
        row["default"] = row["id"] == default_id

    return parser_rows


async def parse_pdf_with_parser(pdf_bytes: bytes, parser_id: str) -> dict:
    parser_id = (parser_id or "").strip().lower() or "pymupdf"

    if parser_id == "pymupdf":
        return await pymupdf_parser.parse_pdf(pdf_bytes)

    if parser_id == "marker_api":
        return await marker.parse_pdf(pdf_bytes)

    if parser_id in {"marker_local", "mineru"}:
        raise RuntimeError(
            f"{parser_id} is not wired into this local instance yet. "
            "Use PyMuPDF for the easiest local path or Marker API for the best quality."
        )

    raise RuntimeError(
        f"Unknown parser '{parser_id}'. "
        "Use one of: pymupdf, marker_api, marker_local, mineru."
    )
