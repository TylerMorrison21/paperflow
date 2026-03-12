from __future__ import annotations

from api.config import DATALAB_API_KEY, MARKER_SINGLE_CMD, PADDLEOCR_VL_CMD
from api.services import marker, marker_local_parser, paddleocr_vl_parser, pymupdf_parser


def list_parsers() -> list[dict]:
    pymupdf_ready = pymupdf_parser.parser_available()
    paddleocr_vl_ready = paddleocr_vl_parser.parser_available(blocking=False)
    marker_local_ready = marker_local_parser.parser_available(blocking=False)

    parser_rows = [
        {
            "id": "pymupdf",
            "label": "PyMuPDF Local",
            "configured": pymupdf_ready,
            "recommended": True,
            "speed": "Free",
            "quality": "Fastest",
            "headline": "Ultra-fast local extraction for standard digital PDFs.",
            "best_for": "Best for contracts, reports, invoices, and other text-layer PDFs when speed and volume matter most.",
            "setup": "Ready after install. No API key and no parser-specific CLI required.",
            "description": "Default choice for everyday document pipelines: zero cost and near-zero latency.",
            "positioning": "Default choice for everyday document pipelines: zero cost and near-zero latency.",
            "facts": [
                {"label": "Cost", "value": "Completely free"},
                {"label": "Speed", "value": "Fastest option for text-layer PDFs"},
                {"label": "Runtime", "value": "Local CPU, fully offline"},
                {"label": "Best with", "value": "Digital PDFs with selectable text"},
                {"label": "Watch out", "value": "Not ideal for scans, dense formulas, or complex academic layouts"},
            ],
            "instructions": [
                "Install the project dependencies so PyMuPDF is available.",
                "Start PaperFlow on this machine.",
                "Choose PyMuPDF Local and upload a digital PDF.",
            ],
            "commands": [
                "python -m pip install -r requirements.txt",
                "python -c \"import fitz; print('PyMuPDF ready')\"",
                "python -m uvicorn api.main:app --reload",
            ],
        },
        {
            "id": "paddleocr_vl",
            "label": "PaddleOCR-VL-0.9B",
            "configured": paddleocr_vl_ready,
            "recommended": True,
            "speed": "Free",
            "quality": "Best quality",
            "headline": "Local AI for scans, research papers, formulas, and complex layouts.",
            "best_for": "Best for researchers, privacy-sensitive teams, and documents with tables, equations, dual-column layouts, or OCR needs.",
            "setup": (
                f"Detected local CLI: {PADDLEOCR_VL_CMD} doc_parser --device cpu"
                if paddleocr_vl_ready
                else "Install PaddleOCR, make sure the paddleocr command works, then keep this page open until PaperFlow detects it."
            ),
            "description": "Best local option when document quality matters and cloud upload is off the table.",
            "positioning": "Best local option when document quality matters and cloud upload is off the table.",
            "facts": [
                {"label": "Cost", "value": "Completely free"},
                {"label": "Strength", "value": "Handles OCR, formulas, tables, and harder layouts well"},
                {"label": "Runtime", "value": "Local CPU, data stays on-device"},
                {"label": "Best with", "value": "Scans, papers, technical PDFs, complex layouts"},
                {"label": "Watch out", "value": "First run needs a large model download and more setup time"},
            ],
            "instructions": [
                "Install PaddlePaddle and PaddleOCR on this machine.",
                "Verify that `paddleocr doc_parser -h` works, or point PaperFlow to the CLI with PADDLEOCR_VL_CMD.",
                "Keep this page open until PaperFlow marks the parser as ready.",
                "Use this when the PDF is scanned or layout recovery matters more than raw speed.",
            ],
            "commands": [
                "python -m pip install paddlepaddle paddleocr",
                "paddleocr doc_parser -h",
                "paddleocr doc_parser -i sample.pdf --device cpu --save_path output",
                "$env:PADDLEOCR_VL_CMD=\"paddleocr\"",
            ],
        },
        {
            "id": "marker_api",
            "label": "Marker API (Datalab.to)",
            "configured": True,
            "recommended": True,
            "speed": "Easy",
            "quality": "Best quality",
            "headline": "Highest-quality extraction with the lowest setup burden.",
            "best_for": "Best for developers and teams that want strong results immediately without managing local models.",
            "setup": "Paste your own Datalab.to API key below. No local parser CLI is required.",
            "description": "Fastest route to premium extraction when cloud processing is acceptable.",
            "positioning": "Fastest route to premium extraction when cloud processing is acceptable.",
            "facts": [
                {"label": "Cost", "value": "Usage-based, usually with trial or free credits"},
                {"label": "Quality", "value": "Highest quality, continuously upgraded"},
                {"label": "Integration", "value": "Easiest setup"},
                {"label": "Runtime", "value": "Cloud processing"},
                {"label": "Watch out", "value": "Documents are uploaded to Datalab servers"},
            ],
            "requires_user_key": True,
            "server_key_configured": bool(DATALAB_API_KEY),
            "instructions": [
                "Create or copy your personal Datalab.to API key.",
                "Select Marker API (Datalab.to).",
                "Paste the key into the API key field below.",
                "Upload only after this parser shows Ready.",
            ],
            "commands": [
                "Open https://www.datalab.to/ and create an API key",
                "Paste the key into the Datalab API key field below",
                "No local parser CLI is required",
            ],
        },
        {
            "id": "marker_local",
            "label": "Enterprise Marker Self-Hosted",
            "configured": marker_local_ready,
            "recommended": False,
            "speed": "Privacy",
            "quality": "Best quality",
            "headline": "Enterprise-grade extraction on your own infrastructure.",
            "best_for": "Best for finance, legal, healthcare, and internal platforms with strict compliance or data residency requirements.",
            "setup": (
                f"Detected local CLI: {MARKER_SINGLE_CMD}"
                if marker_local_ready
                else "Install Marker self-hosted, make sure marker_single works, then keep this page open until PaperFlow detects it."
            ),
            "description": "For teams that need top-tier quality without compromising privacy or control.",
            "positioning": "For teams that need top-tier quality without compromising privacy or control.",
            "facts": [
                {"label": "Cost", "value": "Enterprise or self-hosted infrastructure cost"},
                {"label": "Quality", "value": "Highest quality for private deployments"},
                {"label": "Security", "value": "Fully private, runs on your own infrastructure"},
                {"label": "Runtime", "value": "Your servers or private cloud"},
                {"label": "Watch out", "value": "Production use typically benefits from stronger hardware, often GPU-backed"},
            ],
            "instructions": [
                "Install Marker on the server or workstation you want PaperFlow to use.",
                "Make sure `marker_single --help` works, or point PaperFlow to the binary with MARKER_SINGLE_CMD.",
                "Keep this page open while PaperFlow checks whether the parser is available.",
                "Choose this when privacy and compliance outweigh convenience.",
            ],
            "commands": [
                "python -m pip install marker-pdf",
                "marker_single --help",
                "marker_single sample.pdf --output_dir output --output_format markdown",
                "$env:MARKER_SINGLE_CMD=\"marker_single\"",
            ],
        },
    ]

    default_id = "pymupdf"
    configured_ids = {row["id"] for row in parser_rows if row["configured"]}
    if default_id not in configured_ids and configured_ids:
        for candidate in ("paddleocr_vl", "marker_api", "marker_local"):
            if candidate in configured_ids:
                default_id = candidate
                break

    for row in parser_rows:
        row["default"] = row["id"] == default_id

    return parser_rows


async def parse_pdf_with_parser(pdf_bytes: bytes, parser_id: str, marker_api_key: str = "") -> dict:
    parser_id = (parser_id or "").strip().lower() or "pymupdf"

    if parser_id == "pymupdf":
        return await pymupdf_parser.parse_pdf(pdf_bytes)

    if parser_id in {"paddleocr_vl", "mineru"}:
        return await paddleocr_vl_parser.parse_pdf(pdf_bytes)

    if parser_id == "marker_api":
        api_key = (marker_api_key or "").strip()
        return await marker.parse_pdf_with_api_key(pdf_bytes, api_key=api_key)

    if parser_id == "marker_local":
        return await marker_local_parser.parse_pdf(pdf_bytes)

    raise RuntimeError(
        f"Unknown parser '{parser_id}'. "
        "Use one of: pymupdf, marker_api, marker_local, paddleocr_vl."
    )
