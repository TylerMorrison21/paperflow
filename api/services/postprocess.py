import re
from collections import Counter

def fix_latex_delimiters(md: str) -> str:
    md = re.sub(r'(?<!\\)\\\[(.*?)\\\]', r'$$\1$$', md, flags=re.DOTALL)
    md = re.sub(r'(?<!\\)\\\((.*?)\\\)', r'$\1$',   md, flags=re.DOTALL)
    for env in ['equation', 'align', 'align*', 'gather', 'gather*']:
        md = re.sub(rf'\\begin\{{{env}\}}(.*?)\\end\{{{env}\}}', r'$$\1$$', md, flags=re.DOTALL)
    return md

def inject_page_markers(md: str, page_stats: list) -> str:
    """Page markers removed - unreliable without exact PDF page breaks."""
    return md

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

def make_references_clickable(md: str) -> str:
    """Convert citation/figure/table references into clickable anchor links."""

    # First, add IDs to figures and tables so they can be targeted
    # Match figure blocks: ![caption](image) or <img> tags
    figure_count = 0
    def add_figure_id(match):
        nonlocal figure_count
        figure_count += 1
        # Wrap in a div with an ID
        return f'<div id="fig-{figure_count}">\n\n{match.group(0)}\n\n</div>'

    # Match markdown images
    md = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', add_figure_id, md)

    # Add IDs to markdown tables
    table_count = 0
    def add_table_id(match):
        nonlocal table_count
        table_count += 1
        return f'<div id="table-{table_count}">\n\n{match.group(0)}\n\n</div>'

    # Match markdown tables (lines with | and ---)
    md = re.sub(r'(\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n)*)', add_table_id, md)

    # Now make references clickable
    # Figure references: Fig. 3, Figure 2, (Fig. 1)
    md = re.sub(
        r'\(?(Fig\.?|Figure)\s*\.?\s*(\d+[a-z]?)\)?',
        r'[\1 \2](#fig-\2)',
        md,
        flags=re.IGNORECASE
    )

    # Table references: Table 2, (Table 1)
    md = re.sub(
        r'\(?(Table)\s+(\d+[a-z]?)\)?',
        r'[\1 \2](#table-\2)',
        md,
        flags=re.IGNORECASE
    )

    # Numbered citations: [1], [2-5], [10,15]
    # Be careful not to match markdown links
    md = re.sub(
        r'(?<!\])\[(\d+(?:\s*[-–,]\s*\d+)*)\](?!\()',
        r'[\[\1\]](#ref-\1)',
        md
    )

    # Author-year citations: (Smith et al., 2020)
    # More conservative pattern to avoid false positives
    md = re.sub(
        r'\(([A-Z][a-z]+(?:\s+(?:et\s+al\.?|&|and)\s+[A-Z][a-z]+)?,?\s+\d{4}[a-z]?)\)',
        r'[(\1)](#cite-\1)',
        md
    )

    return md

def postprocess_markdown(raw_md: str, images: dict, metadata: dict) -> dict:
    if not raw_md or raw_md is None:
        raise ValueError("Marker API returned empty or None markdown. The PDF may be invalid, corrupted, or unsupported.")

    md = fix_latex_delimiters(raw_md)
    page_stats = metadata.get("page_stats", [])
    md = inject_page_markers(md, page_stats)
    md = clean_headers_footers(md)
    md = make_references_clickable(md)
    toc      = extract_toc(md)
    sections = split_into_sections(md)
    title    = toc[0]["title"] if toc else "Untitled"

    # Count actual page markers in the markdown
    page_count = len(re.findall(r'<span class="page-marker"', md))

    return {
        "title": title,
        "toc": toc,
        "sections": sections,
        "images": images,
        "metadata": {
            "page_count":    page_count,
            "has_equations": "$" in md,
            "has_tables":    "|" in md and "---" in md,
            "word_count":    len(md.split()),
        },
    }
