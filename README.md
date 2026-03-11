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

## Quick Start

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

## PDF Parsers - bring your own

PaperFlow is a **post-processing** layer. It enhances raw Markdown from any upstream PDF parser. You need to choose a parser:

### Option 1: Datalab Marker API (recommended, easiest)

- Sign up at [datalab.to](https://www.datalab.to) - $25/month free credits
- Cloud API, no GPU needed
- Set `DATALAB_API_KEY` in your `.env`
- PaperFlow's built-in `api/services/marker.py` calls this automatically

### Option 2: Marker (self-hosted, free)

- [github.com/datalab-to/marker](https://github.com/datalab-to/marker)
- Run locally with GPU (CUDA) or CPU
- Free for orgs under $5M revenue
- You'll need to modify `api/services/marker.py` to call your local endpoint

### Option 3: MinerU (self-hosted, free)

- [github.com/opendatalab/MinerU](https://github.com/opendatalab/MinerU)
- Strong on Chinese docs, scientific papers, complex tables
- Outputs Markdown + LaTeX - compatible with PaperFlow's postprocess
- Needs GPU (~6GB VRAM minimum)
- Replace `marker.py` with a MinerU client

### Option 4: Docling, PyMuPDF4LLM, or any other parser

- Any tool that outputs Markdown will work
- Feed the raw Markdown into `paperflow_postprocess.enhance()` or save it and run it through the API pipeline

### Using the pip package with any parser

```python
from paperflow_postprocess import enhance

# Get raw markdown from ANY parser
raw_md = my_parser.convert("paper.pdf")

# Enhance with PaperFlow
result = enhance(raw_md, images={}, metadata={"title": "My Paper"})

# result has footnotes, fixed LaTeX, figure links, YAML frontmatter
```

The whole point of PaperFlow is that **parsing is commoditized**. Marker, MinerU, LlamaParse, Docling, and PyMuPDF4LLM can all produce decent raw output. The post-processing layer is where the value is, and that is what PaperFlow does.

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
