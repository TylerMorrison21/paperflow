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

## P0 Market Readiness (Complete 2026-02-24)

**Environment Variables:**
- `DATALAB_API_KEY` — Marker API key (required)
- `CORS_ORIGINS` — Allowed origins for CORS (Railway)
- `NEXT_PUBLIC_API_URL` — Backend API URL (Vercel)
- `NEXT_PUBLIC_POSTHOG_KEY` — PostHog analytics key (optional, for event tracking)
- `NEXT_PUBLIC_POSTHOG_HOST` — PostHog host (default: https://app.posthog.com)
- `MAX_PDF_MB` — Max PDF file size in MB (default: 50)
- `FEEDBACK_DIR` — Feedback storage directory (default: ./data/feedback)

**API Error Codes:**
- `429` — Rate limit exceeded (10 requests per 60 seconds per IP)
- `413` — File too large (exceeds MAX_PDF_MB)
- `error_code` conventions: `RATE_LIMITED`, `FILE_TOO_LARGE`, `PARSE_FAILED`, `INVALID_PDF`

**Key Endpoints:**
- `POST /api/parse` — Upload PDF, returns `{paper_id, status: "processing"}` (rate limited)
- `GET /api/parse/{id}` — Poll status, returns `{status: "processing|complete|error", error_code?}`
- `GET /api/paper/{id}` — Get rendered data (title, toc, sections, images, metadata)
- `POST /api/feedback` — Submit user feedback (type: bug/feature/general), saves to `data/feedback/{timestamp}.json`
- `GET /health` — Health check endpoint

**Analytics Events (Frontend - PostHog):**
- `visit_home` — User lands on homepage
- `upload_start` — User initiates PDF upload (includes filename, sizeKB)
- `parse_success` — PDF processing completes successfully (includes paperId, durationSec)
- `parse_failed` — PDF processing fails (includes errorCode, errorMessage)
- `reader_view` — User views reader page (includes paperId)
- `share_copy_link` — User copies shareable link via 🔗 Share button (includes paperId)
- `feedback_submit` — User submits feedback (includes type, message)
- `export_markdown` — User exports paper to Markdown (includes paperId)
- `inline_popover` — User clicks citation/figure/table link (includes paperId, targetType)
- `text_highlight` — User highlights text (includes paperId, color)
- `export_highlights` — User exports highlights (includes paperId, count)
- `copy_with_citation` — User copies text with auto-citation (includes paperId) - tracks viral spread

**Landing Page Features (2026-02-24):**
- Hero section: "Read papers without scroll-back hell" + 2 CTAs (Upload PDF / View demo)
- 4 key benefits: Inline citation/figure popovers, copy with auto-citation (viral), text highlighting + export, shareable links
- "How it works" section (3 steps with emoji icons)
- Mini FAQ (3 questions: scanned PDFs, storage, pricing)
- Footer with Privacy/Terms/Contact links (pages live)
- Trust signal: 🔒 "Private & secure. We never use your data to train AI." below upload box

**Reader Features (The Soul of the MVP):**
- **Inline popovers**: Click any citation/figure/table link to view inline without losing your place
  - Smooth 0.15s fade-in animation, no delay
  - Auto-positions to avoid viewport edges
  - Close via click outside, Escape key, or X button
  - Detects targets by ID patterns (fig-, table-, ref-) or HTML tags
  - Section headings still scroll normally
  - Transforms static PDFs into interactive semantic networks
- **Copy with Citation** (Viral PLG growth hack):
  - Every copy operation automatically appends: "—\nExtracted via PaperFlow.app\n[Title]\n[Link]"
  - Silent attribution spreads product virally in Slack/Discord/email
  - Solves real pain: professionals need to cite sources anyway
  - Highly targeted exposure: reaches other researchers/professionals
  - Zero friction: users don't need to do anything
  - Classic legal tech/academic tool feature
- **Text highlighting + export** (Ultimate lean startup feature):
  - Select text → color picker toolbar (4 colors: yellow, green, blue, pink)
  - Highlights stored in localStorage (no auth/database/sync needed)
  - One-click export: "💡 Export N Highlights" button appears when highlights exist
  - Downloads clean Markdown with quotes + context
  - Zero-friction onboarding: no registration required
  - Perfect for Obsidian/Notion workflow
  - Irresistible retention hook for hardcore productivity users
- Markdown export: 📥 Export MD button downloads clean .md file for Obsidian/Notion
- Shareable links: `/read/{paper_id}` with copy-to-clipboard button in SettingsBar
- Dark mode toggle (persists across page)
- Font size controls (16/18/20px)
- TOC sidebar (desktop) + hamburger drawer (mobile)
- Inline math rendering (KaTeX)
- Section deep linking with intersection observer

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
