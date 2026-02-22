import re
from collections import Counter

def fix_latex_delimiters(md: str) -> str:
    md = re.sub(r'(?<!\\)\\\[(.*?)\\\]', r'$$\1$$', md, flags=re.DOTALL)
    md = re.sub(r'(?<!\\)\\\((.*?)\\\)', r'$\1$',   md, flags=re.DOTALL)
    for env in ['equation', 'align', 'align*', 'gather', 'gather*']:
        md = re.sub(rf'\\begin\{{{env}\}}(.*?)\\end\{{{env}\}}', r'$$\1$$', md, flags=re.DOTALL)
    return md

def inject_page_markers(md: str, page_stats: list) -> str:
    if not page_stats:
        return md
    lines = md.split('\n')
    # page_stats is a list of dicts with 'page' and approximate char positions
    # Marker doesn't give line numbers, so insert markers at heading boundaries per page
    result = []
    page = 1
    for line in lines:
        if line.startswith('#') and page < len(page_stats):
            page += 1
            result.append(f'<span class="page-marker" data-page="{page}">p.{page}</span>')
        result.append(line)
    return '\n'.join(result)

def clean_headers_footers(md: str) -> str:
    lines = md.split('\n')
    counts = Counter(l.strip() for l in lines if l.strip() and len(l.strip()) < 80)
    repeated = {t for t, c in counts.items() if c >= 3}
    return '\n'.join(l for l in lines if l.strip() not in repeated)

def _slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def extract_toc(md: str) -> list:
    toc = []
    for i, line in enumerate(md.split('\n')):
        m = re.match(r'^(#{1,4})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            anchor = _slugify(title)
            toc.append({"id": f"sec-{i}", "title": title, "level": level, "anchor": anchor})
    return toc

def split_into_sections(md: str) -> list:
    MAX = 1500
    heading_re = re.compile(r'^(#{1,4})\s+(.*)', re.MULTILINE)
    matches = list(heading_re.finditer(md))

    if not matches:
        # fallback: split by double newlines
        chunks = [c.strip() for c in re.split(r'\n\n+', md) if c.strip()]
        sections = []
        buf = ""
        for chunk in chunks:
            if len(buf) + len(chunk) > MAX and buf:
                sections.append(buf.strip())
                buf = chunk
            else:
                buf = (buf + "\n\n" + chunk).strip()
        if buf:
            sections.append(buf)
        return [
            {"id": f"sec-{i}", "heading": "", "level": 0, "markdown": s}
            for i, s in enumerate(sections)
        ]

    sections = []
    for idx, m in enumerate(matches):
        start = m.start()
        end   = matches[idx + 1].start() if idx + 1 < len(matches) else len(md)
        body  = md[start:end].strip()
        level = len(m.group(1))
        heading = m.group(2).strip()

        # force-split oversized sections at paragraph boundary
        while len(body) > MAX:
            split_at = body.rfind('\n\n', 0, MAX)
            if split_at == -1:
                split_at = MAX
            sections.append({
                "id": f"sec-{len(sections)}",
                "heading": heading if not sections or sections[-1]["heading"] != heading else "",
                "level": level,
                "markdown": body[:split_at].strip(),
            })
            body = body[split_at:].strip()
            heading = ""

        sections.append({"id": f"sec-{len(sections)}", "heading": heading, "level": level, "markdown": body})

    return sections

def postprocess_markdown(raw_md: str, images: dict, metadata: dict) -> dict:
    md = fix_latex_delimiters(raw_md)
    page_stats = metadata.get("page_stats", [])
    md = inject_page_markers(md, page_stats)
    md = clean_headers_footers(md)
    toc      = extract_toc(md)
    sections = split_into_sections(md)
    title    = toc[0]["title"] if toc else "Untitled"
    return {
        "title": title,
        "toc": toc,
        "sections": sections,
        "images": images,
        "metadata": {
            "page_count":    len(page_stats),
            "has_equations": "$" in md,
            "has_tables":    "|" in md and "---" in md,
            "word_count":    len(md.split()),
        },
    }
