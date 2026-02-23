# PaperFlow – Working Rules

## Goal
Help me ship the MVP fast with small, safe steps.

## Project Summary
**PaperFlow is LIVE and working end-to-end (2026-02-23).**

PaperFlow converts academic PDFs into beautiful, readable web articles — like Medium for research papers.
Stack: Next.js 14 (Vercel) + FastAPI (Railway) + Marker API (Datalab).

**Processing time:** Usually tens of seconds to several minutes, depending on PDF complexity and queue.

**Live URLs:**
- Frontend: https://frontend-9kvi1cyc6-tylermorrison21s-projects.vercel.app
- Backend: https://pdfreflow-production.up.railway.app

See `D:/projects/CLAUDE.md` and `D:/projects/plan.md` for full architecture and execution plan.

**After each deployable task:** Update `plan.md` with progress, modified files, and next step.

## Legacy Architecture (PDFReflow — kept for reference)
```
app.py                      Streamlit UI (upload → convert → download)
core/converter.py           Orchestrator — calls marker_client then epub_builder
core/marker_client.py       Datalab API: upload PDF, poll until complete  ← REUSE in PaperFlow
core/epub_builder.py        Markdown → Pandoc subprocess → EPUB3
core/epub_style.css         Minimal CSS for Pandoc (no word-break overrides)
.env                        DATALAB_API_KEY (required)
```

## What to Reuse in PaperFlow
- `core/marker_client.py` — Marker API client (upload + poll). Adapt to httpx (async) for FastAPI backend.

## Key Decisions (still relevant)
- All PDFs go through Marker API — no local text extraction
- `_unwrap_lines()`: purge invisible chars → NLP smart_merge → buffer
- Images saved flat in temp dir to match Marker's relative paths
- **Page markers removed (2026-02-23):** Datalab hosted API doesn't support `paginate_output`, estimation was unreliable for academic citations. Users navigate by section headings + deep links instead.

## P0 Market Readiness

**Environment Variables:**
- `DATALAB_API_KEY` — Marker API key (required)
- `CORS_ORIGINS` — Allowed origins for CORS (Railway)
- `NEXT_PUBLIC_API_URL` — Backend API URL (Vercel)
- `NEXT_PUBLIC_POSTHOG_KEY` — PostHog analytics key (optional, for event tracking)
- `MAX_PDF_MB` — Max PDF file size in MB (default: 50)

**API Error Codes:**
- `429` — Rate limit exceeded (too many requests from same IP)
- `413` — File too large (exceeds MAX_PDF_MB)
- `error_code` conventions: `RATE_LIMITED`, `FILE_TOO_LARGE`, `PARSE_FAILED`, `INVALID_PDF`

**Key Endpoints:**
- `POST /api/parse` — Upload PDF, returns `{paper_id, status: "processing"}`
- `GET /api/parse/{id}` — Poll status, returns `{status: "processing|complete|error", error_code?}`
- `GET /api/paper/{id}` — Get rendered data (title, toc, sections, images, metadata)
- `POST /api/feedback` — Submit user feedback, saves to `data/feedback/{timestamp}.json`

**Analytics Events (Frontend):**
- `visit_home` — User lands on homepage
- `upload_start` — User initiates PDF upload
- `parse_success` — PDF processing completes successfully
- `parse_failed` — PDF processing fails
- `reader_view` — User views reader page
- `share_copy_link` — User copies shareable link
- `feedback_submit` — User submits feedback

## Allowed Automation (with limits)
- You may run: `git status`, `git diff`, and ONE of: `rg`/`grep` with a narrow keyword
- You may read at most 3 files per task (ask before reading more)
- Do NOT run `ls -R`, `find`, `tree`, or `git log --all`

## Before Editing
1. Say what you plan to change (max 5 bullet points)
2. Ask which file(s) to open if you are unsure

## Output Format
- Prefer showing the exact edit (old → new)
- Keep explanations short (max 6 lines)

## Code Style (PaperFlow backend)
- Python 3.10 (Windows, CPython)
- httpx (async) for HTTP — NOT urllib.request (PaperFlow uses FastAPI async)
- Small functions, minimal refactors

## Task Memory
When a task is done or stuck, update `plan.md`:
- status (Done / Blocked)
- modified files
- next step (1 line)
