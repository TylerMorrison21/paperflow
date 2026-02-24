# Plan

## Current State (2026-02-22 — Pivoting to PaperFlow)
**PDFReflow MVP is complete. Project is pivoting to PaperFlow (PDF→web reader).**
Full plan: `D:/projects/plan.md` | Architecture: `D:/projects/PaperFlow_Architecture.md`

### PDFReflow (legacy, complete)
Pipeline: **PDF → Datalab Marker API → Pandoc 3.9 → EPUB3**
UI: Streamlit at `streamlit run app.py` → http://localhost:8501
Env: `DATALAB_API_KEY` in `.env` (active key saved)

## Active Files (what matters now)
```
app.py                   — Streamlit UI (upload → convert → download)
core/
  converter.py           — orchestrator: Marker → epub_builder → EPUB
  marker_client.py       — Datalab API client (upload + poll)
  epub_builder.py        — Markdown → Pandoc → EPUB3 (build_epub_from_markdown)
  epub_style.css         — minimal typography CSS for Pandoc
web/
  payment.py             — future (not wired up)
  storage.py             — future (not wired up)
.env                     — DATALAB_API_KEY (real key)
```

## Deleted (legacy — no longer in repo)
```
core/pandoc_builder.py   — replaced by Pandoc subprocess in epub_builder
core/layout_analyzer.py  — old OpenRouter vision OCR
core/pdf_detector.py     — old text/scanned/mixed detector
core/text_pipeline.py    — old zero-cost text extractor
core/text_cleaner.py     — utility, never called in pipeline
core/gongjiyun.py        — old GPU cloud deploy scripts
core/ai_enhance.py       — old Claude Vision OCR pass
core/epub.css            — replaced by epub_style.css
```

---

## PaperFlow — Next Steps (active)

### Step 1: Backend API [x] Done (2026-02-22)
FastAPI at `D:/projects/pdfreflow/api/` (or new `D:/projects/paperflow/backend/`)
- POST /api/parse — upload PDF, async background task, return paper_id
- GET /api/parse/{id} — poll status
- GET /api/paper/{id} — return full rendered data (title, toc, sections, images, metadata)
- Reuse `core/marker_client.py` → adapt to httpx async
- File-based JSON storage (`./data/papers/{paper_id}.json`)

### Step 2: Frontend Reader [x] Done (2026-02-22)
Next.js 14 (App Router) — Medium-style reading experience
- Upload page → processing poll → reader page
- KaTeX math, TOC sidebar, dark mode
- **Note:** Page numbers not guaranteed; users navigate by section headings + deep links

### Step 2.5: Debug & Polish [x] Done (2026-02-22)
### Step 3: Deploy [x] Done (2026-02-23)
- Backend → Railway (`uvicorn api.main:app --workers 1`) + railway.toml
- Frontend → Vercel + vercel.json
- railway login → railway init → railway up → set DATALAB_API_KEY + CORS_ORIGINS
- vercel login → vercel --prod → set NEXT_PUBLIC_API_URL
- **Live URLs:**
  - Frontend: https://frontend-9kvi1cyc6-tylermorrison21s-projects.vercel.app
  - Backend: https://pdfreflow-production.up.railway.app

### Step 4: Market Validation [x] Complete (2026-02-24)
- [x] End-to-end test complete — upload → processing → reader page working
- [x] Dark mode text visibility fixed (CSS variables for all components)
- [x] Page markers removed — Datalab API doesn't support `paginate_output`, estimation was unreliable for citations
  - Backend: `inject_page_markers()` returns markdown unchanged
  - Frontend: `stripPageMarkers()` filters out old markers from cached documents
  - Removed: `api/services/page_extractor.py`, page-marker CSS
  - **Navigation:** Users reference by section headings + deep links instead of page numbers
- [x] P0 Market-ready base (Checklist):
  - [x] Analytics: PostHog event tracking (visit_home / upload_start / parse_success / parse_failed / reader_view / share_copy_link / feedback_submit / export_markdown / inline_popover / text_highlight / export_highlights)
  - [x] Shareable link: /read/[paper_id] direct access + 🔗 Share button in SettingsBar with copy-to-clipboard
  - [x] Failure UX: Error handling with error_code conventions (RATE_LIMITED, FILE_TOO_LARGE, PARSE_FAILED, INVALID_PDF)
  - [x] Rate limit & file size: In-memory rate limiter (10 req/60s per IP, 429 error) + MAX_PDF_MB env var (default 50MB, 413 error)
  - [x] Feedback: POST /api/feedback endpoint + saved to data/feedback/{timestamp}.json
  - [x] Landing page: New hero section, "How it works", FAQ, footer with Privacy/Terms/Contact links
  - [x] Privacy/Terms/Contact: All pages live with proper content
  - [x] Markdown export: 📥 Export MD button in reader for Obsidian/Notion workflow
  - [x] Trust signal: 🔒 "Private & secure. We never use your data to train AI." below upload box
  - [x] Inline popovers: Click citations/figures/tables to view inline without scroll-back hell (THE SOUL OF THE MVP)
  - [x] Text highlighting + export: Select text → color picker → localStorage → one-click export (ULTIMATE LEAN STARTUP)
- [ ] Test with 5 PDFs (arXiv ML, survey, CV, Chinese, scanned)
- [ ] Take before/after screenshots
- [ ] Post to r/GradSchool, r/MachineLearning, HN Show HN
- [ ] Track: 50 uploads, 10 repeat users, 5 "I'd pay for this"

**Design Decision (2026-02-23):** Removed page markers entirely. Marker API's hosted version doesn't return page breaks, and estimation was too inaccurate for academic citations. Users reference by section headings + deep links instead, which is more reliable for web articles.

**Task Memory (2026-02-24):**
- Modified files:
  - Backend: `api/main.py`, `api/routes/parse.py`, `api/routes/feedback.py`, `api/middleware/rate_limit.py`, `api/errors.py`, `api/config.py`
  - Frontend: `frontend/src/app/page.tsx`, `frontend/src/app/privacy/page.tsx`, `frontend/src/app/terms/page.tsx`, `frontend/src/app/contact/page.tsx`, `frontend/src/lib/analytics.ts`, `frontend/src/components/Reader/SettingsBar.tsx`, `frontend/src/components/Reader/ReaderLayout.tsx`, `frontend/src/components/Reader/ArticleBody.tsx`, `frontend/src/components/Reader/InlinePopover.tsx` (new), `frontend/src/components/Reader/HighlightToolbar.tsx` (new), `frontend/src/components/UploadZone.tsx`, `frontend/src/hooks/useHighlights.ts` (new)
  - Docs: `LANDING_PAGE_UPDATE.md` (new), `CLAUDE.md`, `plan.md`
- Key features completed:
  - Inline popovers for citations/figures/tables (eliminates scroll-back hell)
  - Text highlighting with localStorage + one-click export (zero-friction knowledge capture)
  - Markdown export for Obsidian/Notion
  - Privacy trust signal at upload point
  - Full compliance pages
- Next step: Test with 5 diverse PDFs, take screenshots, prepare for market launch

---

## PDFReflow — Completed Work

### 2026-02-20 Session — All Done ✓

### Switched epub_builder to Pandoc
- Replaced ebooklib + custom HTML/CSS (~440 lines) with Pandoc subprocess (~110 lines)
- `build_epub_from_markdown(markdown, images, output_path, title)` signature unchanged
- Images saved to same temp dir as `input.md` so Pandoc resolves relative paths
- Output path resolved to absolute before subprocess (fixes `cwd=tmp` bug)
- YAML front matter prepended to markdown for title metadata

### _unwrap_lines overhaul
- **Silver bullet**: purge invisible chars (`\u200b`, `\u200c`, `\u200d`, `\u00ad`) first
- **Pass 0 — NLP smart_merge**: regex `([a-zA-Z]+) *\n *([a-zA-Z]+)` + pyspellchecker
  - combined is known word AND a fragment is unknown → join without space ("advanc"+"ing" → "advancing")
  - both halves are known words OR combined unknown → join with space
- **Pass 1 — buffer approach**: structural guard (headings, lists, tables pass through unchanged)
- Installed: `pyspellchecker 0.8.4`

### CSS simplified (epub_style.css)
- Removed all `word-break`, `hyphens`, `overflow-wrap`, `!important` overrides
- Word-break issues were caused by WPS reader, not our code
- Minimal clean typography: `margin: 5%`, `font-family: serif`, `line-height: 1.8`

### XHTML compliance fix (_fix_epub_xhtml)
- Pandoc 3.9 emits bare `<br>` inside table cells (XHTML-invalid)
- Pre-pass: replace `<br>` / `<hr>` in raw Marker markdown before Pandoc
- Post-pass: `_fix_epub_xhtml()` rewrites the EPUB zip after Pandoc, patches all `.xhtml` files
- Verified: 0 unclosed void tags remaining in output EPUB

---

## PDFReflow — Deferred (not priority)
- Error handling — friendly UI error if Marker API fails
- Progress feedback — show elapsed time
- Payment / storage — `web/payment.py` and `web/storage.py` not wired up

## Test Command
```bash
cd /d/projects/pdfreflow
streamlit run app.py
# open http://localhost:8501
# upload a PDF, click Convert, download EPUB
# check outputs/<stem>.md for raw Marker output
```
