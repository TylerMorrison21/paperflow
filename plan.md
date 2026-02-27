# plan.md — PaperFlow Execution Plan

## Current State: MVP Live ✓
**Async PDF→Markdown pipeline with footnotes, rate limiting, and dedup.**

Frontend: https://www.paperflowing.com (Vercel)
Backend: https://paperflow-production-daf5.up.railway.app (Railway)

---

## Step 1: Backend Pipeline [✓] DONE

### 1a. API Structure [✓]

```
api/
├── main.py              # FastAPI, CORS, /health, mount submit route
├── config.py            # Env vars + rate limit configs
├── models.py            # SubmitResponse(job_id, message)
├── routes/
│   └── submit.py        # POST /api/submit — PDF + email, dedup, rate limits, background task
└── services/
    ├── marker.py         # Async Marker API (httpx polling)
    ├── postprocess.py    # THE product — Markdown enhancement
    ├── packager.py       # Build flat ZIP: paper.md + images/
    ├── emailer.py        # Send ZIP via Resend API
    └── ratelimit.py      # Per-email (3/day) + global (300/day) + monthly pages (50k)
```

### 1b. POST /api/submit [✓]

```
POST /api/submit
Content-Type: multipart/form-data
Fields: file (PDF), email (string)

→ 200 {"job_id": "xxx", "message": "Processing. Check your inbox in 1-2 minutes."}

Background task:
1. SHA-256 hash → check dedup cache
2. If cache hit (valid footnotes + title) → re-email cached ZIP, skip Marker API
3. If stale cache → evict, reprocess
4. Save PDF to data/jobs/{job_id}/input.pdf
5. Call Marker API → get markdown + images
6. extract_title() — metadata → H1 → filename fallback
7. Run postprocess pipeline (LaTeX, footnotes, figures, tables, frontmatter)
8. Package flat ZIP (paper.md + images/)
9. Send email with ZIP via Resend
10. Register hash in dedup cache
```

### 1c. postprocess.py — The Product [✓]

```python
def postprocess(raw_markdown, images, metadata):
    md = fix_latex_delimiters(md)       # \[..\] → $$..$$
    md = clean_headers_footers(md)      # Remove repeated lines + page numbers
    md = convert_to_footnotes(md)       # [N] / [[#Reference N]] → [^N] footnotes
    md = linkify_figures(md)            # [Fig. 3] → [[#^fig-3|Fig. 3]]
    md = linkify_tables(md)             # [Table 2] → [[#^tab-2|Table 2]]
    md = inject_frontmatter(md, metadata)
    return md
```

Key features:
- **Footnotes**: Standard Markdown `[^N]` / `[^N]:` — native Obsidian hover preview, click-to-scroll, ↩ back-nav
- **LaTeX protection**: Citations inside $...$ and $$...$$ never touched
- **[0] skip**: Array indices never converted to citations
- **Marker format support**: Both `[N]` and `[[#Reference N]]` wiki-link formats handled
- **Multi-citation**: `[1, 2, 3]` → `[^1][^2][^3]`, `[1-3]` → `[^1][^2][^3]`

### 1d. packager.py [✓]

- Flat ZIP structure (no wrapper folder): paper.md + images/
- ZIP filename = sanitized paper title
- Base64 image decoding with data URI prefix handling
- Robust image path rewriting (handles Marker's various reference formats)

### 1e. emailer.py [✓]

- Subject: "Your paper is ready: {title}"
- Attachment: `{sanitized_title}.zip`
- HTML branded template with PaperFlow header + feature checklist

### 1f. Rate Limiting & Anti-Abuse [✓]

- Per-email: 3/day
- Global: 300/day, 50k pages/month
- Graceful 429 messages (no "Error" shown)
- Frontend: yellow for rate limits, red for real errors
- Cached/dedup submissions bypass rate limits

### 1g. Dedup Cache [✓]

- SHA-256 hash of PDF bytes
- In-memory dict, rebuilt from disk on startup
- Stale cache eviction: must have footnotes + valid title
- Cache hit → skip Marker API + rate limits, re-email immediately

---

## Step 2: Minimal Frontend [✓] DONE

One static `frontend/index.html` file. No React, no Next.js, no build step.
Deployed on Vercel at https://www.paperflowing.com
API calls go to Railway backend.

Design:
- Dark background (#0a0a0a), mono font (JetBrains Mono)
- Drag & drop zone + email input + submit button
- Success message after 200
- Graceful rate limit messages in yellow, errors in red

---

## Step 3: Deploy + Validate [~] In progress

### Backend: Railway ✓
- Project: paperflow (b0dfdf32-ea1d-4089-aece-a553b68a605b)
- URL: https://paperflow-production-daf5.up.railway.app
- Health: /health → {"status": "ok"}

### Frontend: Vercel ✓
- URL: https://www.paperflowing.com

### Validate [~] Testing
- [✓] Graph ODEs survey paper — footnotes working, hover preview confirmed
- [✓] LIGO GW paper (PRL format, headingless references) — footnotes working after bug fix
- [ ] Test 3 more PDFs (image-heavy, Chinese, scanned)
- [ ] Screenshot: Obsidian with rendered LaTeX + working footnote hover
- [ ] Post to r/ObsidianMD and r/GradSchool
- [ ] Success metric: 50 submissions, 10 repeat users, 5 "I'd pay"

### Bug Fixes
- [✓] 2026-02-27: `convert_to_footnotes` failed silently on PRL/physics papers — those have no
  "References" heading; Marker outputs a bare `- [1] Author...` list. Fixed by adding a fallback
  that detects `^(?:-\s*)?(?:\[\[#Reference 1\]\]|\[1\]\s+\S)` as the section start.

---

## Phase 2 Roadmap (only after validation)

| Priority | Feature | Purpose |
|----------|---------|---------|
| P0 | Notion API integration ("Save to Notion" button in email) | Workflow penetration |
| P1 | Batch upload (multiple PDFs at once) | Power user retention |
| P1 | YAML frontmatter with Dataview-compatible fields | Obsidian power users |
| P2 | MCP Server endpoint | AI agent integration |
| P2 | Stripe payment ($5/month or $0.50/paper) | Revenue |

---

## Legacy (PDFReflow — complete, archived)

Pipeline: PDF → Marker API → Pandoc 3.9 → EPUB3
Status: Done, deprioritized. Code in core/ kept for reference.

---

## Deprecated

- Old PaperFlow Web Reader (Next.js) — killed 2026-02-25
- [[#^ref-N]] block reference links — replaced by standard footnotes 2026-02-26
