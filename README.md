# PaperFlow

PaperFlow is an open-source post-processing layer for PDF-to-Markdown workflows.

It does not try to be the parser. It takes raw markdown from a parser you choose and upgrades it into structured, knowledge-ready markdown with:

- normalized LaTeX delimiters
- linked citations as standard footnotes
- figure and table jump links
- YAML frontmatter
- cleaned repeated headers and footers

PyPI package: https://pypi.org/project/paperflow-postprocess/  
GitHub: https://github.com/TylerMorrison21/paperflow  
Project page: https://www.paperflowing.com

## Install

```bash
pip install paperflow-postprocess
```

## Recommended workflow

If you want the best results with the least setup, use the self-hosted API with Datalab Marker.

- Sign up at `datalab.to`
- Add your `DATALAB_API_KEY` to `.env`
- Run the backend locally
- Send a PDF to the API
- Download the processed markdown or zip package

Datalab has a free credit tier, so most users can try this path without paying first.

```bash
git clone https://github.com/TylerMorrison21/paperflow
cd paperflow
cp .env.example .env
# Add DATALAB_API_KEY to .env
uvicorn api.main:app --port 8000
```

Submit a PDF:

```bash
curl -X POST http://localhost:8000/api/submit \
  -F "file=@paper.pdf"
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

## Python package only

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

## PDF Parser compatibility

| Parser | Status | Notes |
|--------|--------|-------|
| Marker API (Datalab) | ✅ Fully tested | Recommended. Sign up at datalab.to |
| Marker (self-hosted) | ✅ Fully tested | Same output format as API |
| MinerU | ⚠️ Partial | LaTeX fixing works, footnotes may need tuning |
| Docling | ⚠️ Partial | Basic cleanup works, links untested |
| LlamaParse | ⚠️ Partial | Output format differs, YMMV |
| Others | ❓ Unknown | PRs welcome to add parser adapters |

PaperFlow is built and tested against Marker's output format.
Other parsers may work for basic features (LaTeX normalization,
header cleanup) but footnote conversion and figure linking
depend on Marker-specific formatting patterns.

If you use another parser and the output looks wrong, debug in this order:

1. Check whether citations look like `[1]`, `[2]`, `[1-3]`
2. Check whether figure captions look like `Fig. 3:` or `Figure 3:`
3. Check whether table captions look like `Table 2:`
4. Run the individual helpers one by one instead of `enhance()`

```python
from paperflow_postprocess import (
    fix_latex_delimiters,
    clean_headers_footers,
    convert_to_footnotes,
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

## Visual Comparison

| Source PDF | Generic converter output | PaperFlow output |
|---|---|---|
| ![Source PDF](https://raw.githubusercontent.com/TylerMorrison21/paperflow/master/docs/compare/sample-paper.jpg) | ![Generic converter output](https://raw.githubusercontent.com/TylerMorrison21/paperflow/master/docs/compare/pydoc-converted-online-pdf-converter.jpg) | ![PaperFlow output](https://raw.githubusercontent.com/TylerMorrison21/paperflow/master/docs/compare/paperflow-converted.jpg) |

Additional example:

![Calligraphy comparison](https://raw.githubusercontent.com/TylerMorrison21/paperflow/master/docs/compare/caligraphy.jpg)

## What `enhance()` does

`enhance()` upgrades parser output into structured markdown with:

- standard footnotes `[^N]` from inline citations like `[1]`, `[1, 2]`, or `[1-3]`
- normalized LaTeX delimiters using `$...$` and `$$...$$`
- figure links like `[[#^fig-3|Fig. 3]]`
- table links like `[[#^tab-2|Table 2]]`
- YAML frontmatter with title, authors, source, date, and extraction hash
- cleaned repeated headers, footers, and page number lines

## API

- `enhance(raw_markdown, images=None, metadata=None)`
- `postprocess(raw_markdown, images=None, metadata=None)` for backward compatibility
- `fix_latex_delimiters(md)`
- `clean_headers_footers(md)`
- `convert_to_footnotes(md)`
- `linkify_figures(md)`
- `linkify_tables(md)`
- `inject_frontmatter(md, metadata)`
