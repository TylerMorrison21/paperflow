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
- KaTeX math, TOC sidebar, page markers, dark mode

### Step 2.5: Debug & Polish [x] Done (2026-02-22)
### Step 3: Deploy [x] Done (2026-02-23)
- Backend → Railway (`uvicorn api.main:app --workers 1`) + railway.toml
- Frontend → Vercel + vercel.json
- railway login → railway init → railway up → set DATALAB_API_KEY + CORS_ORIGINS
- vercel login → vercel --prod → set NEXT_PUBLIC_API_URL
- **Live URLs:**
  - Frontend: https://frontend-9kvi1cyc6-tylermorrison21s-projects.vercel.app
  - Backend: https://pdfreflow-production.up.railway.app

### Step 4: Market Validation [~] In progress (2026-02-23)
- [x] End-to-end test complete — upload → processing → reader page working
- [ ] Test with 5 PDFs (arXiv ML, survey, CV, Chinese, scanned)
- [ ] Take before/after screenshots
- [ ] Post to r/GradSchool, r/MachineLearning, HN Show HN
- [ ] Track: 50 uploads, 10 repeat users, 5 "I'd pay for this"

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
