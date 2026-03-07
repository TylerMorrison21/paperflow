# PaperFlow – Working Rules

## Goal
Help me ship the MVP fast with small, safe steps.

## Project Summary
**PaperFlow is an async PDF→Markdown pipeline for researchers.**

User drops a PDF + enters email → backend processes via Marker API → delivers a clean
Markdown ZIP (with images, LaTeX, Obsidian footnotes) to their inbox via Resend.

The product IS the Markdown quality. There is NO web reader, NO annotation system,
NO chat. Users consume the output in their own tools (Obsidian, Notion, Zotero).

Stack: Minimal frontend (upload box) + FastAPI backend + Marker API + Resend email.

## What We Killed (do NOT rebuild)
- ❌ Web reader UI (no React article rendering, no KaTeX in browser)
- ❌ TOC sidebar, scroll-spy, settings bar, dark mode, font controls
- ❌ Frontend polling / progress bars / WebSocket
- ❌ User registration / login / auth
- ❌ Highlight & annotation system
- ❌ Any UI beyond a drag-drop box + email input + "check your inbox" confirmation
- ❌ [[#^ref-N]] block reference links (replaced by standard footnotes)
- ❌ Generous free tier (playground capped at 15 pages + 3 conversions/day — demo only)

## Architecture
```
Browser (minimal HTML)           FastAPI backend              External
┌─────────────────┐     POST    ┌──────────────────┐        ┌────────────┐
│ Drag-drop PDF   │────────────▶│ /api/submit      │───────▶│ Marker API │
│ + email input   │  200 OK     │                  │◀───────│ (Datalab)  │
│ "Check inbox"   │◀────────────│ Background task: │        └────────────┘
└─────────────────┘             │ 1. Marker parse  │
                                │ 2. postprocess   │        ┌────────────┐
                                │ 3. build ZIP     │───────▶│ Resend API │
                                │ 4. send email    │        │ (email)    │
                                └──────────────────┘        └────────────┘
```

## Project Structure
```
D:/Projects/pdfreflow/
├── CLAUDE.md                    # This file
├── plan.md                      # Execution plan
├── .env                         # DATALAB_API_KEY, RESEND_API_KEY
│
├── api/                         # FastAPI backend
│   ├── main.py                  # App entry, CORS, /health
│   ├── config.py                # Env vars (incl. rate limits)
│   ├── models.py                # Pydantic schemas
│   ├── routes/
│   │   ├── submit.py            # POST /api/submit (PDF + email, dedup, rate limits)
│   │   └── jobs.py              # GET /api/jobs/{job_id}/status + /result
│   └── services/
│       ├── marker.py            # Async Marker API client (httpx)
│       ├── postprocess.py       # Markdown enhancement (THE product)
│       ├── packager.py          # Build ZIP (markdown + images/)
│       ├── emailer.py           # Send ZIP via Resend API
│       └── ratelimit.py         # Per-email + global rate limiting
│
├── frontend/                    # ONE static HTML page
│   └── index.html               # Funnel layout: Hero → Before/After → MCP → Enterprise CTA
│
├── mcp-server/                  # MCP Server (paperflow-mcp on npm)
│   ├── package.json
│   ├── README.md
│   └── src/
│       └── index.js             # StdioServerTransport, convert_pdf tool
│
├── core/                        # Legacy PDFReflow code
│   └── marker_client.py         # Datalab API client — logic reused in api/services/marker.py
│
└── data/                        # Temp storage (gitignored)
    └── jobs/{job_id}/           # Per-job dir: input.pdf, paper.md, images/, {title}.zip
```

## Core Pipeline (postprocess.py — this IS the product)
```python
def postprocess(raw_markdown: str, images: dict, metadata: dict) -> str:
    md = raw_markdown
    md = fix_latex_delimiters(md)       # \[..\] → $$..$$, \(..\) → $..$
    md = clean_headers_footers(md)      # Remove repeated header/footer lines
    md = convert_to_footnotes(md)       # [N] / [[#Reference N]] → [^N] footnotes
    md = linkify_figures(md)            # [Fig. 3] → [[#^fig-3|Fig. 3]]
    md = linkify_tables(md)             # [Table 2] → [[#^tab-2|Table 2]]
    md = inject_frontmatter(md, metadata)  # YAML header: title, authors, date, hash
    return md
```

### postprocess.py — Detailed Spec

**fix_latex_delimiters(md)**:
- `\[ ... \]` → `$$ ... $$`
- `\( ... \)` → `$ ... $`
- `\begin{equation}...\end{equation}` → `$$ ... $$`
- `\begin{align}...\end{align}` → `$$ ... $$`
- Do NOT touch already-correct `$...$` or `$$...$$`

**convert_to_footnotes(md)** (replaces old linkify_references):
- Finds the references section using a 3-level fallback:
  1. Heading: `## References`, `# Bibliography`, `**Works Cited**`, plain `References`, etc.
  2. Bare list (PRL/physics papers with no heading): `- [1] Author...` or `[1] Author...`
  3. Marker wiki-link format: `- [[#Reference 1]] Author...`
- Parses reference entries (handles `[N]`, `- [N]`, and `- [[#Reference N]]` formats)
- Protects LaTeX ($...$, $$...$$) and code blocks from citation replacement
- Body: `[N]` → `[^N]`, `[[#Reference N]]` → `[^N]`, `[1, 2, 3]` → `[^1][^2][^3]`, `[1-3]` → `[^1][^2][^3]`, `[1–3]` (en-dash) → `[^1][^2][^3]`
- Never replaces `[0]` (array index, not citation)
- References section: `[^N]: Author, Title, Journal, Year.`
- Obsidian natively supports footnote hover preview, click-to-scroll, and ↩ back-navigation

**linkify_figures(md)**:
- Find `[Fig. N]`, `[Figure N]`, `(Fig. N)`, `(Figure N)` in text
- Replace with `[[#^fig-N|Fig. N]]` (Obsidian block reference link)
- Add `^fig-N` anchor to figure caption lines

**linkify_tables(md)**:
- Same pattern: `[Table N]` → `[[#^tab-N|Table N]]`
- Add `^tab-N` anchor to table caption lines

**inject_frontmatter(md, metadata)**:
- Prepend YAML front-matter block with title, authors, source, extracted date, hash, tags

**clean_headers_footers(md)**:
- Find lines that repeat identically across the document (>3 times) — remove them
- Remove standalone page number lines

## ZIP Structure (packager.py)
```
{title}.zip (flat — no wrapper folder)
├── paper.md          # Enhanced Markdown with frontmatter + footnotes
└── images/
    ├── fig1.jpg
    ├── fig2.png
    └── ...
```
- ZIP filename = sanitized paper title
- No wrapper folder inside ZIP — unzips directly to paper.md + images/
- Image references in markdown point to `images/filename.jpg` (relative path)
- Handles Marker's base64 images including data URI prefix stripping
- User drags contents into Obsidian vault → everything just works

## Rate Limiting & Anti-Abuse
- **Page limit**: 15 pages max per PDF (playground is a quality demo, not free conversion)
- **Per-email**: 3 conversions/day per email address
- **Global daily**: 300 submissions/day (handles Reddit-scale traffic spikes)
- **Monthly pages**: 8,000 pages/month
- **Graceful degradation**: 429 responses show friendly messages, not error codes
  - Per-email: "You've reached your free daily limit of 3 conversions. Upgrade to Pro for higher limits."
  - Global: "PaperFlow is experiencing high demand. Please try again in a few hours!"
- **Frontend**: 429s shown in warm yellow (#c9a227), other errors in red

## Dedup (SHA-256 Hash Cache)
- PDF bytes → SHA-256 hash → check in-memory cache
- Cache hit with valid output (has footnotes + valid title) → skip Marker API, re-email cached ZIP
- Stale cache (no footnotes or "Untitled" title) → evict and reprocess
- Cache rebuilt from disk on startup by scanning existing job dirs
- Cached submissions skip rate limit counting

## Title Extraction (3 fallbacks)
1. Marker API metadata.title (skip if contains "untitled")
2. First H1 heading (`# ...`) in raw markdown
3. Uploaded filename stem (spaces cleaned)

## Email (emailer.py)
- Subject: "Your paper is ready: {title}"
- Attachment: `{sanitized_title}.zip`
- HTML body: PaperFlow branded template with paper title + feature checklist
- Sent via Resend API

## Key Technical Rules
1. **All processing is async** — POST /api/submit returns 200 immediately
2. **File-based job storage** — `data/jobs/{job_id}/` per job
3. **Single worker** — `uvicorn --workers 1` on Railway
4. **Email via Resend** — free tier: 100 emails/day (resend.com, Python SDK)
5. **No database** — file system + JSON for rate limiting
6. **No user accounts** — email is the only identifier

## Deployment
- **Backend**: Railway (https://paperflow-production-daf5.up.railway.app)
  - Deploy: `cd D:/projects/pdfreflow && railway up --detach`
- **Frontend**: Vercel (https://www.paperflowing.com)
  - Deploy: `cd D:/projects/pdfreflow/frontend && vercel --prod`

## Product Positioning
- **Playground** (paperflowing.com) = free demo, max 15 pages and 3 conversions/day
- **MCP Server** (paperflow-mcp) = primary distribution channel, integrates into Claude Desktop workflow
- **API** (future) = batch processing for enterprise
- Target customers: EdTech, academic tool builders, research infrastructure teams
- All messaging funnels heavy users to support@paperflowing.com

## MCP Server
- Location: `mcp-server/` directory
- NPM package: `paperflow-mcp` (current: v0.1.5)
- Tool: `convert_pdf` — accepts PDF URL, base64, or absolute local PDF path; returns Markdown with metadata header
- v0.1.5 adds truncated/malformed attachment detection with user-facing recovery steps (retry via local path or URL)
- Calls backend `POST /api/submit` + `GET /api/jobs/{job_id}/status` + `/result`
- Email field always set to `mcp@paperflowing.com` — backend detects `MCP_EMAIL_PREFIX = "mcp@"` and skips Resend
- No auth required (rate limited by backend)
- Stdout is JSON-RPC only; all logs via `console.error()`
- `jobs.py` rejects `job_id` containing `..`, `/`, or `\` (path traversal protection)

## Environment Variables
```bash
DATALAB_API_KEY=<marker api key>
MARKER_API_URL=https://www.datalab.to/api/v1/marker
RESEND_API_KEY=<resend api key>
FROM_EMAIL=delivery@paperflowing.com
CORS_ORIGINS=*
DATA_DIR=./data/jobs
DAILY_SUBMISSION_LIMIT=300
MONTHLY_PAGE_LIMIT=8000
PER_EMAIL_DAILY_LIMIT=3
```

## Legacy (PDFReflow — kept for reference, do not modify)
```
app.py                      Streamlit UI
core/converter.py           Orchestrator
core/marker_client.py       Datalab API client (reuse logic)
core/epub_builder.py        Pandoc → EPUB3
core/epub_style.css         Minimal CSS
```

## Before Editing
1. Say what you plan to change (max 5 bullet points)
2. Ask which file(s) to open if you are unsure

## Output Format
- Prefer showing the exact edit (old → new)
- Keep explanations short (max 6 lines)

## Code Style
- Python 3.10 (Windows, CPython)
- httpx (async) for HTTP
- Small functions, minimal refactors

## Task Memory
When a task is done or stuck, update `plan.md`:
- status (Done / Blocked)
- modified files
- next step (1 line)

## Recent Task Memory (2026-03-04)
- Published `paperflow-mcp@0.1.5` with:
  - malformed/truncated attachment detection
  - clear user-facing retry instructions
  - local file-path bypass in `convert_pdf` source
- Updated user-facing MCP install snippets to pin `paperflow-mcp@0.1.5`:
  - `frontend/index.html`
  - `mcp-server/README.md`
- Production deploys completed:
  - Vercel: `https://www.paperflowing.com`
  - Railway: deployment `443391c2-68a1-4984-80f8-fed31745c3da` status `SUCCESS`
