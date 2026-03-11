# PaperFlow - Working Rules

## Goal
Keep PaperFlow maintainable as an open-source project with small, safe changes.

## Project Status
**Project is open-source, maintenance mode.**

PaperFlow is now primarily the markdown post-processing layer plus the MCP server.
The hosted playground is deprecated and should not be rebuilt. Users are expected to:

- run the Python package locally
- self-host the full pipeline if they want extraction plus post-processing
- use the MCP server against a backend they control

## Project Summary
**PaperFlow turns raw PDF-to-Markdown output into structured knowledge.**

The product is the quality of the post-processing:

- normalized LaTeX
- linked citations as footnotes
- figure and table references
- YAML frontmatter

PaperFlow works with any parser. Marker API is one option, not the product.

## What We Killed (do NOT rebuild)
- Web playground upload flow
- Email delivery workflow
- Hosted conversion funnel
- Web reader UI
- TOC sidebar, scroll-spy, settings bar, dark mode, font controls
- Frontend polling / progress bars / WebSocket
- User registration / login / auth
- Highlight & annotation system
- Any UI beyond the current static open-source project page
- `[[#^ref-N]]` block reference links (replaced by standard footnotes)

## Architecture
```text
Parser output -> PaperFlow postprocess -> structured markdown

Optional full pipeline:
PDF -> parser -> PaperFlow postprocess -> markdown/assets

Optional MCP flow:
Claude Desktop -> paperflow-mcp -> user-hosted backend -> parser -> PaperFlow postprocess
```

## Project Structure
```text
D:/Projects/pdfreflow/
|- CLAUDE.md                    # This file
|- plan.md                      # Execution plan / project status
|- .env.example                 # Example env vars for self-hosting
|
|- api/                         # Optional self-hosted FastAPI backend
|  |- main.py                   # App entry, CORS, /health
|  |- config.py                 # Env vars and limits
|  |- models.py                 # Pydantic schemas
|  |- routes/
|  |  |- submit.py             # Legacy hosted submit flow, deprecated
|  |  `- jobs.py               # Job status/result endpoints for self-hosters
|  `- services/
|     |- marker.py             # Parser integration
|     |- postprocess.py        # Compatibility wrapper
|     |- packager.py           # ZIP/export utilities
|     |- emailer.py            # Legacy, deprecated
|     `- ratelimit.py          # Legacy hosted limits
|
|- paperflow_postprocess/       # Published Python package
|  `- __init__.py              # Packaged post-processing logic
|
|- frontend/                    # Static project page
|  `- index.html               # Open-source landing page
|
|- mcp-server/                  # MCP Server (paperflow-mcp on npm)
|  |- package.json
|  |- README.md
|  `- src/
|     `- index.js              # Claude Desktop MCP server
|
`- data/                        # Local temp storage for self-hosting
```

## Core Product
```python
def postprocess(raw_markdown: str, images: dict, metadata: dict) -> str:
    md = raw_markdown
    md = fix_latex_delimiters(md)
    md = clean_headers_footers(md)
    md = convert_to_footnotes(md)
    md = linkify_figures(md)
    md = linkify_tables(md)
    md = inject_frontmatter(md, metadata)
    return md
```

## Core Technical Rules
1. Prefer improving the packaged post-processing logic, not legacy hosted flows.
2. Keep the landing page static and deployment-free where possible.
3. Do not reintroduce playground or email-driven product logic.
4. Preserve `GET /health` for optional self-hosted monitoring.
5. MCP server info stays relevant because users may self-host any compatible backend.

## MCP Server
- Location: `mcp-server/`
- NPM package: `paperflow-mcp`
- Purpose: connect Claude Desktop to a user-hosted PaperFlow-compatible backend
- Keep MCP docs and install snippets current
- Do not assume a PaperFlow-managed hosted backend exists

## Environment Variables
Only document self-hosting variables that are still relevant. Avoid assuming hosted services.

## Legacy
Hosted playground, email delivery, and managed backend flows are deprecated.
Keep legacy code only when it still helps self-hosters or preserves compatibility.

## Before Editing
1. Say what you plan to change.
2. If unsure which file owns a behavior, inspect the code first.

## Output Format
- Prefer showing the exact edit when useful
- Keep explanations short

## Code Style
- Python 3.10
- Small functions, minimal refactors
- Prefer ASCII when editing docs and code

## Task Memory
When a task is done or stuck, update `plan.md` with:
- status
- modified files
- next step
