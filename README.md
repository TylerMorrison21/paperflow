[![PyPI version](https://img.shields.io/pypi/v/paperflow-postprocess)](https://pypi.org/project/paperflow-postprocess/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

# PaperFlow

**Turn academic PDFs into structured, knowledge-ready Markdown - 
with working footnotes, LaTeX equations, figure links, and metadata.**

PaperFlow is an open-source post-processing engine for PDF->Markdown 
pipelines. It takes raw Markdown from any PDF parser (Marker, PaddleOCR-VL, 
PyMuPDF, Docling, LlamaParse) and upgrades it into structured output 
that works in Obsidian, Notion, Logseq, or any RAG pipeline.

### What it fixes

| Problem in raw parser output | After PaperFlow |
|-----|-----|
| `[1]` dead text - can't click | `[^1]` standard footnote - hover to preview |
| `\[ E=mc^2 \]` wrong delimiters | `$$ E=mc^2 $$` renders everywhere |
| `[Fig. 3]` plain string | `[[#^fig-3\|Fig. 3]]` clickable internal link |
| No metadata | YAML frontmatter: title, authors, date, tags |
| Repeated headers/footers | Cleaned automatically |

### Visual comparison

| Source PDF | Generic converter | PaperFlow output |
|---|---|---|
| ![Source](https://raw.githubusercontent.com/TylerMorrison21/paperflow/master/docs/compare/original_pdf.png) | ![Generic](https://raw.githubusercontent.com/TylerMorrison21/paperflow/master/docs/compare/pymupdf_converted.png) | ![PaperFlow](https://raw.githubusercontent.com/TylerMorrison21/paperflow/master/docs/compare/paperflow_converted.png) |

> **77K views on Reddit** - 810 upvotes - 98% upvote ratio - 
> 10,000+ pages processed - Used by researchers in 40+ countries

---

PyPI package: https://pypi.org/project/paperflow-postprocess/  
GitHub: https://github.com/TylerMorrison21/paperflow  
Project page: https://www.paperflowing.com

## Install

```bash
pip install paperflow-postprocess
```

## Quick Start

### Option A: Local Web UI (recommended for most users)

```bash
git clone https://github.com/TylerMorrison21/paperflow
cd paperflow
cp .env.example .env
pip install -r requirements.txt
uvicorn api.main:app --port 8000
```

Then open the local UI:

```text
http://localhost:8000/
```

The local UI shows a quick decision guide, checks which parsers are actually ready on your machine, and displays exact setup commands for each parser option.

### Option A2: Docker / Unraid

PaperFlow can also run as a single container because the FastAPI backend serves the local Web UI.

Pull the prebuilt image:

```bash
docker run --name paperflow \
  -p 8000:8000 \
  -e DATA_DIR=/data/jobs \
  -v $(pwd)/data:/data \
  --restart unless-stopped \
  ghcr.io/tylermorrison21/paperflow:latest
```

Or build locally from this repo:

```bash
docker build -t paperflow .
docker run --name paperflow \
  -p 8000:8000 \
  -e DATA_DIR=/data/jobs \
  -v $(pwd)/data:/data \
  --restart unless-stopped \
  paperflow
```

Then open:

```text
http://localhost:8000/
```

For Unraid, map `/data` to your appdata share, for example `/mnt/user/appdata/paperflow`.
The repo also includes an Unraid app template at `unraid/paperflow.xml`.

The stock container is best for:

- `PyMuPDF Local` as the default free local parser
- `Marker API (Datalab.to)` if you provide your own API key

The heavier local parsers are not bundled in the default image:

- `PaddleOCR-VL-0.9B`
- `Enterprise Marker Self-Hosted`

Those require a custom image with extra dependencies.

See [docs/unraid.md](docs/unraid.md) for the Unraid-specific notes and Compose example.

### Option B: Python package only

Use the pip package when you already have raw markdown from another parser and only want PaperFlow's post-processing layer.

```python
from paperflow_postprocess import enhance

raw_markdown = """
Text with citation [1].

## References

[1] Example Author. Example Paper.
"""

markdown = enhance(
    raw_markdown=raw_markdown,
    images={},
    metadata={
        "title": "Example Paper",
        "authors": ["Example Author"],
        "source": "https://example.com/paper",
        "date": "2026-03-11",
    },
)

print(markdown)
```

### Option C: API calls

Submit a PDF by API:

```bash
curl -X POST http://localhost:8000/api/submit \
  -F "file=@paper.pdf"
```

Use Marker API instead of the default PyMuPDF parser:

```bash
curl -X POST http://localhost:8000/api/submit \
  -F "file=@paper.pdf" \
  -F "parser=marker_api" \
  -F "marker_api_key=your_datalab_api_key"
```

Use PaddleOCR-VL for scanned PDFs or more complex layouts:

```bash
curl -X POST http://localhost:8000/api/submit \
  -F "file=@paper.pdf" \
  -F "parser=paddleocr_vl"
```

Poll for completion:

```bash
curl http://localhost:8000/api/jobs/<job_id>/status
```

Download the processed markdown:

```bash
curl http://localhost:8000/api/jobs/<job_id>/result -o paper.md
```

Download the markdown plus images package:

```bash
curl http://localhost:8000/api/jobs/<job_id>/package -o paperflow.zip
```

## Choosing a Parser

If you want the simplest path from PDF to usable markdown, run the local UI and pick the parser that matches your needs.

- `PyMuPDF Local` is the default. It is free, local, and fastest for standard digital PDFs.
- `PaddleOCR-VL-0.9B` is the best free local choice for scanned PDFs, formulas, and complex layouts.
- `Marker API (Datalab.to)` is the easiest premium-quality path. The UI requires the user's own `marker_api_key`.
- `Enterprise Marker Self-Hosted` works if you have the official `marker_single` CLI installed locally.

Recommended order:

1. Start with `PyMuPDF Local` for standard digital PDFs and the fastest free local conversion.
2. Switch to `PaddleOCR-VL-0.9B` for scans, tables, formulas, and harder layouts.
3. Use `Marker API (Datalab.to)` when you want the easiest premium-quality setup.
4. Use `Enterprise Marker Self-Hosted` when privacy, compliance, and private infrastructure matter most.

Datalab usually offers trial or free credits, so most users can try the premium cloud path without committing first.

## Local Parser Setup

### PyMuPDF

Nothing extra is required beyond the Python dependencies in `requirements.txt`.

### Marker API (Datalab.to)

For the local UI, paste your own API key into the Marker API key field.

For direct API calls, send:

```bash
-F "parser=marker_api" -F "marker_api_key=your_datalab_api_key"
```

If you want a server-side default for custom integrations, you can still set:

```env
DATALAB_API_KEY=your_datalab_api_key_here
```

### Enterprise Marker Self-Hosted

Install Marker locally so `marker_single` is available on your `PATH`.
If you use a custom command path or want extra flags, set:

```env
MARKER_SINGLE_CMD=marker_single
MARKER_SINGLE_ARGS=
```

PaperFlow runs the local CLI in this shape:

```bash
marker_single input.pdf --output_dir output --output_format markdown
```

### PaddleOCR-VL-0.9B

Install PaddleOCR locally so `paddleocr` is available on your `PATH`.
If you use a custom command path or want extra flags, set:

```env
PADDLEOCR_VL_CMD=paddleocr
PADDLEOCR_VL_ARGS=
```

PaperFlow runs the local CLI in this shape:

```bash
paddleocr doc_parser -i input.pdf --device cpu --save_path output
```

## Parser Compatibility

| Parser | Status | Notes |
|--------|--------|-------|
| PyMuPDF Local | Default local path | Free, fastest, easiest setup for text-layer PDFs |
| PaddleOCR-VL-0.9B | Local AI path | Best free local option for scans, formulas, and harder layouts |
| Marker API (Datalab.to) | Premium cloud path | Easiest premium-quality setup, requires `marker_api_key` |
| Enterprise Marker Self-Hosted | Private deployment path | Uses the official `marker_single` CLI locally |
| Docling | Partial | Basic cleanup works, links untested |
| LlamaParse | Partial | Output format differs, YMMV |
| Others | Unknown | PRs welcome to add parser adapters |

For the fastest local path, start with PyMuPDF.  
For the best free local quality, use PaddleOCR-VL.  
For the easiest premium-quality path, use Marker API.  
For private enterprise infrastructure, use self-hosted Marker.

PaperFlow is still built and tested most deeply against Marker's output format.
Other parsers may work well for basic features (LaTeX normalization, header cleanup), but footnote conversion and figure linking are strongest on Marker-style formatting.

## What `enhance()` Does

`enhance()` upgrades parser output into structured markdown with:

- standard footnotes `[^N]` from inline citations like `[1]`, `[1, 2]`, or `[1-3]`
- normalized LaTeX delimiters using `$...$` and `$$...$$`
- figure links like `[[#^fig-3|Fig. 3]]`
- table links like `[[#^tab-2|Table 2]]`
- YAML frontmatter with title, authors, source, date, and extraction hash
- cleaned repeated headers, footers, and page number lines

## Debugging

If you use another parser and the output looks wrong, debug in this order:

1. Check whether citations look like `[1]`, `[2]`, `[1-3]`
2. Check whether figure captions look like `Fig. 3:` or `Figure 3:`
3. Check whether table captions look like `Table 2:`
4. Run the individual helpers one by one instead of `enhance()`

```python
from paperflow_postprocess import (
    clean_headers_footers,
    convert_to_footnotes,
    fix_latex_delimiters,
    linkify_figures,
    linkify_tables,
)

md = open("raw.md", encoding="utf-8").read()
md = fix_latex_delimiters(md)
md = clean_headers_footers(md)
md = convert_to_footnotes(md)
md = linkify_figures(md)
md = linkify_tables(md)
```

For local parser debugging, check these first:

1. `marker_single --help` or `paddleocr doc_parser -h` works in your terminal
2. The parser shows as `Configured` in the local UI
3. The parser can produce a `.md` file when run directly on one sample PDF
4. If needed, set `MARKER_SINGLE_CMD`, `MARKER_SINGLE_ARGS`, `PADDLEOCR_VL_CMD`, or `PADDLEOCR_VL_ARGS` in `.env`

## Enterprise & Commercial Use

PaperFlow is MIT licensed - free for personal and commercial use.

For organizations that need:
- **Private deployment** on your infrastructure (Docker, air-gapped)
- **Commercial API** with SLA and support
- **Custom integrations** (iManage, SharePoint, NetDocuments, Notion)
- **Custom post-processing rules** for your document types

Contact: support@paperflowing.com

---

## API Reference

- `enhance(raw_markdown, images=None, metadata=None)`
- `postprocess(raw_markdown, images=None, metadata=None)` for backward compatibility
- `fix_latex_delimiters(md)`
- `clean_headers_footers(md)`
- `convert_to_footnotes(md)`
- `linkify_figures(md)`
- `linkify_tables(md)`
- `inject_frontmatter(md, metadata)`
