[![PyPI version](https://img.shields.io/pypi/v/paperflow-postprocess)](https://pypi.org/project/paperflow-postprocess/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

# PaperFlow

**Turn academic PDFs into structured, knowledge-ready Markdown — 
with working footnotes, LaTeX equations, figure links, and metadata.**

PaperFlow is an open-source post-processing engine for PDF→Markdown 
pipelines. It takes raw Markdown from any PDF parser (Marker, MinerU, 
PyMuPDF, Docling, LlamaParse) and upgrades it into structured output 
that works in Obsidian, Notion, Logseq, or any RAG pipeline.

### What it fixes

| Problem in raw parser output | After PaperFlow |
|-----|-----|
| `[1]` dead text — can't click | `[^1]` standard footnote — hover to preview |
| `\[ E=mc^2 \]` wrong delimiters | `$$ E=mc^2 $$` renders everywhere |
| `[Fig. 3]` plain string | `[[#^fig-3\|Fig. 3]]` clickable internal link |
| No metadata | YAML frontmatter: title, authors, date, tags |
| Repeated headers/footers | Cleaned automatically |

### Visual comparison

| Source PDF | Generic converter | PaperFlow output |
|---|---|---|
| ![Source](https://raw.githubusercontent.com/TylerMorrison21/paperflow/master/docs/compare/original_pdf.png) | ![Generic](https://raw.githubusercontent.com/TylerMorrison21/paperflow/master/docs/compare/pymupdf_converted.png) | ![PaperFlow](https://raw.githubusercontent.com/TylerMorrison21/paperflow/master/docs/compare/paperflow_converted.png) |

> **77K views on Reddit** · 810 upvotes · 98% upvote ratio · 
> 10,000+ pages processed · Used by researchers in 40+ countries

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
# Optional: add DATALAB_API_KEY to .env for Marker API
uvicorn api.main:app --port 8000
```

Then open the local UI:

```text
http://localhost:8000/
```

The local UI auto-detects which parsers are ready on your machine.

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
  -F "parser=marker_api"
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

- `PyMuPDF` is the default. It is free, local, and fastest.
- `Marker API (Datalab)` gives the best output quality. Add `DATALAB_API_KEY` and it is ready.
- `Marker self-hosted` works if you have the official `marker_single` CLI installed locally.
- `MinerU` works if you already have the official `mineru` CLI installed locally.

Recommended order:

1. Start with `PyMuPDF` if you want the easiest free local conversion.
2. Switch to `Marker API` when you want the best markdown quality.
3. Use `Marker self-hosted` or `MinerU` when you want your own local parser stack.

Datalab has a free credit tier, so most users can try the higher-quality path without paying first.

## Local Parser Setup

### PyMuPDF

Nothing extra is required beyond the Python dependencies in `requirements.txt`.

### Marker API (Datalab)

Set this in `.env`:

```env
DATALAB_API_KEY=your_datalab_api_key_here
```

### Marker self-hosted

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

### MinerU

Install MinerU locally so `mineru` is available on your `PATH`.
If you use a custom command path or want extra flags, set:

```env
MINERU_CMD=mineru
MINERU_ARGS=
```

PaperFlow runs the local CLI in this shape:

```bash
mineru -p input.pdf -o output
```

## Parser Compatibility

| Parser | Status | Notes |
|--------|--------|-------|
| PyMuPDF | Fast local fallback | Free, fastest, easiest setup, but lower quality |
| Marker API (Datalab) | Fully tested | Recommended. Sign up at datalab.to |
| Marker (self-hosted) | Fully tested | Uses the official `marker_single` CLI locally |
| MinerU | Partial | Uses the official `mineru` CLI locally |
| Docling | Partial | Basic cleanup works, links untested |
| LlamaParse | Partial | Output format differs, YMMV |
| Others | Unknown | PRs welcome to add parser adapters |

For the easiest local path, start with PyMuPDF.  
For the best output quality, use Marker API or self-hosted Marker.

PaperFlow is still built and tested most deeply against Marker's output format.
Other parsers may work well for basic features (LaTeX normalization, header cleanup), but footnote conversion and figure linking are strongest on Marker-style formatting.

## Visual Comparison

| Source PDF | Generic converter output | PaperFlow output |
|---|---|---|
| ![Source PDF](https://raw.githubusercontent.com/TylerMorrison21/paperflow/master/docs/compare/original_pdf.png) | ![Generic converter output](https://raw.githubusercontent.com/TylerMorrison21/paperflow/master/docs/compare/pymupdf_converted.png) | ![PaperFlow output](https://raw.githubusercontent.com/TylerMorrison21/paperflow/master/docs/compare/paperflow_converted.png) |

Additional example:

![Calligraphy comparison](https://raw.githubusercontent.com/TylerMorrison21/paperflow/master/docs/compare/caligraphy.jpg)

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

1. `marker_single --help` or `mineru --help` works in your terminal
2. The parser shows as `Configured` in the local UI
3. The parser can produce a `.md` file when run directly on one sample PDF
4. If needed, set `MARKER_SINGLE_CMD`, `MARKER_SINGLE_ARGS`, `MINERU_CMD`, or `MINERU_ARGS` in `.env`

## Enterprise & Commercial Use

PaperFlow is MIT licensed — free for personal and commercial use.

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
