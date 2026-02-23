# PaperFlow – Working Rules

## Goal
Help me ship the MVP fast with small, safe steps.

## Project Summary
**PaperFlow is LIVE and working end-to-end (2026-02-23).**

PaperFlow converts academic PDFs into beautiful, readable web articles — like Medium for research papers.
Stack: Next.js 14 (Vercel) + FastAPI (Railway) + Marker API (Datalab).

**Live URLs:**
- Frontend: https://frontend-9kvi1cyc6-tylermorrison21s-projects.vercel.app
- Backend: https://pdfreflow-production.up.railway.app

See `D:/projects/CLAUDE.md` and `D:/projects/plan.md` for full architecture and execution plan.

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
