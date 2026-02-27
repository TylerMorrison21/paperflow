import re
import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def postprocess(raw_markdown: str, images: dict, metadata: dict) -> str:
    """
    Enhance raw Markdown from Marker API for Obsidian consumption.
    This is THE product - the quality of this output defines PaperFlow.
    """
    md = raw_markdown
    md = fix_latex_delimiters(md)
    md = clean_headers_footers(md)
    md = convert_to_footnotes(md)       # [1] / [[#Reference 1]] → [^1] footnotes
    md = linkify_figures(md)            # Fig. 3 → [[#^fig-3|Fig. 3]]
    md = linkify_tables(md)             # Table 2 → [[#^tab-2|Table 2]]
    md = inject_frontmatter(md, metadata)
    return md


def fix_latex_delimiters(md: str) -> str:
    """
    Normalize LaTeX delimiters to Obsidian-friendly format.
    \[ ... \] → $$ ... $$
    \( ... \) → $ ... $
    \begin{equation} ... \end{equation} → $$ ... $$
    """
    md = re.sub(r'\\\[(.*?)\\\]', r'$$ \1 $$', md, flags=re.DOTALL)
    md = re.sub(r'\\\((.*?)\\\)', r'$ \1 $', md, flags=re.DOTALL)

    for env in ['equation', 'align', 'align*', 'gather', 'gather*']:
        md = re.sub(
            rf'\\begin\{{{env}\}}(.*?)\\end\{{{env}\}}',
            r'$$ \1 $$',
            md,
            flags=re.DOTALL
        )

    return md


def clean_headers_footers(md: str) -> str:
    """
    Remove repeated header/footer lines and standalone page numbers.
    """
    lines = md.split('\n')
    line_counts = {}

    for line in lines:
        stripped = line.strip()
        if stripped:
            line_counts[stripped] = line_counts.get(stripped, 0) + 1

    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped or line_counts.get(stripped, 0) <= 3:
            cleaned.append(line)
        elif not re.match(r'^\d+$', stripped):
            cleaned.append(line)

    return '\n'.join(cleaned)


# ---------------------------------------------------------------------------
# Footnote-based reference system
# ---------------------------------------------------------------------------

def _protect_blocks(text: str) -> tuple[str, list[str]]:
    """Replace LaTeX and code blocks with placeholders to prevent regex mangling."""
    blocks = []

    def save(m):
        blocks.append(m.group(0))
        return f"%%BLOCK_{len(blocks) - 1}%%"

    # Code blocks ```...``` first
    text = re.sub(r'```.*?```', save, text, flags=re.DOTALL)
    # Inline code `...`
    text = re.sub(r'`[^`]+?`', save, text)
    # Display math $$...$$
    text = re.sub(r'\$\$.*?\$\$', save, text, flags=re.DOTALL)
    # Inline math $...$
    text = re.sub(r'\$[^\$\n]+?\$', save, text)
    return text, blocks


def _restore_blocks(text: str, blocks: list[str]) -> str:
    """Restore protected blocks from placeholders."""
    for i, block in enumerate(blocks):
        text = text.replace(f"%%BLOCK_{i}%%", block)
    return text


def _parse_ref_entries(ref_text: str) -> dict[str, str]:
    """
    Parse reference entries from the references section.
    Handles:
    - [N] Author... (traditional)
    - - [[#Reference N]] Author... (Marker wiki-link format)
    - - [N] Author... (bullet list)
    """
    entries = {}

    # Normalize Marker wiki-link format: [[#Reference N]] → [N]
    normalized = re.sub(
        r'\[\[#Reference\s+(\d+)\]\]',
        lambda m: f'[{m.group(1)}]',
        ref_text
    )

    # Split into lines and accumulate multi-line entries
    lines = normalized.split('\n')
    current_num = None
    current_text = []

    for line in lines:
        # Match start of a new entry: optional bullet, then [N]
        match = re.match(r'^\s*-?\s*\[(\d+)\]\s*(.*)', line)
        if match:
            # Save previous entry
            if current_num is not None:
                entries[current_num] = ' '.join(current_text).strip()
            current_num = match.group(1)
            current_text = [match.group(2)] if match.group(2) else []
        elif current_num is not None and line.strip():
            # Continuation line of current entry
            current_text.append(line.strip())

    # Save last entry
    if current_num is not None:
        entries[current_num] = ' '.join(current_text).strip()

    return entries


def convert_to_footnotes(md: str) -> str:
    """
    Convert citations to standard Markdown footnotes.
    Body: [1] or [[#Reference 1]] → [^1]
    References section → [^1]: Author, Title, etc.

    Obsidian natively renders footnotes with hover preview, click-to-scroll,
    and back-navigation — no plugins needed.
    """
    # Find the References section — handle heading, bold, plain text, and headingless variants
    ref_pattern = re.compile(
        r'^(?:#{1,6}\s*)?(?:\*\*)?(?:References|Bibliography|Works Cited|Reference List)(?:\*\*)?\s*$',
        re.MULTILINE | re.IGNORECASE
    )
    ref_match = ref_pattern.search(md)

    if ref_match:
        body = md[:ref_match.start()]
        ref_section = md[ref_match.end():]
    else:
        # Fallback: detect headingless reference lists (e.g. PRL/physics papers).
        # Look for "[1] Word..." or "- [1] Word..." or "- [[#Reference 1]]"
        bare_ref = re.compile(
            r'^(?:-\s*)?(?:\[\[#Reference 1\]\]|\[1\]\s+\S)',
            re.MULTILINE
        )
        bare_match = bare_ref.search(md)
        if bare_match:
            logger.info("convert_to_footnotes: No heading found — using bare reference list fallback")
            body = md[:bare_match.start()]
            ref_section = md[bare_match.start():]  # Include the [1] entry itself
        else:
            logger.warning("convert_to_footnotes: No References section found — skipping footnote conversion")
            return md

    # Parse reference entries
    ref_entries = _parse_ref_entries(ref_section)

    if not ref_entries:
        logger.warning("convert_to_footnotes: References section found but no entries parsed — skipping")
        return md

    logger.info(f"convert_to_footnotes: Found {len(ref_entries)} reference entries")

    # Protect LaTeX and code blocks in body
    body, blocks = _protect_blocks(body)

    # Replace Marker wiki-link format first: [[#Reference N]] → [^N]
    def replace_wikilink(m):
        num = int(m.group(1))
        if num == 0:
            return m.group(0)
        return f'[^{num}]'

    body = re.sub(r'\[\[#Reference\s+(\d+)\]\]', replace_wikilink, body)

    # Replace comma-separated citations: [1, 2, 3] → [^1][^2][^3]
    def replace_multi(m):
        nums = [n.strip() for n in re.findall(r'\d+', m.group(1))]
        if all(int(n) > 0 for n in nums):
            return ''.join(f'[^{n}]' for n in nums)
        return m.group(0)

    body = re.sub(
        r'(?<![!\[\w])\[((\d{1,3})(?:\s*,\s*\d{1,3})+)\](?!\()',
        replace_multi,
        body
    )

    # Replace ranges: [1-3] → [^1][^2][^3]
    def replace_range(m):
        start, end = int(m.group(1)), int(m.group(2))
        if start == 0 or end == 0 or end - start > 20:
            return m.group(0)
        return ''.join(f'[^{n}]' for n in range(start, end + 1))

    body = re.sub(
        r'(?<![!\[\w])\[(\d{1,3})\s*[-–]\s*(\d{1,3})\](?!\()',
        replace_range,
        body
    )

    # Replace single citations: [N] → [^N]
    def replace_single(m):
        num = int(m.group(1))
        if num == 0:
            return m.group(0)
        return f'[^{num}]'

    body = re.sub(
        r'(?<![!\[\w^])\[(\d{1,3})\](?!\()',
        replace_single,
        body
    )

    # Restore protected blocks
    body = _restore_blocks(body, blocks)

    # Build footnote definitions
    footnotes = "\n## References\n\n"
    for num in sorted(ref_entries.keys(), key=int):
        footnotes += f"[^{num}]: {ref_entries[num]}\n\n"

    return body.rstrip() + "\n\n" + footnotes


# ---------------------------------------------------------------------------
# Figure / Table linking (unchanged)
# ---------------------------------------------------------------------------

def _add_fig_anchors(md: str) -> str:
    """
    Append ^fig-N block IDs to figure caption lines.
    """
    def add_anchor(m):
        prefix = m.group(0).rstrip()
        num = m.group(1)
        prefix = re.sub(r'\s*\^fig-\d+$', '', prefix)
        return f"{prefix} ^fig-{num}"

    # Match "Figure N:" or "Fig. N:" or "Figure N." at start of line, capture full line
    md = re.sub(
        r'^(?:Figure|Fig\.)\s+(\d+)\s*[:.].+',
        add_anchor,
        md,
        flags=re.MULTILINE | re.IGNORECASE
    )
    return md


def linkify_figures(md: str) -> str:
    """
    Convert figure references to Obsidian block reference links.
    Body: [Fig. 3] → [[#^fig-3|Fig. 3]]
    Captions: Figure 3: description → Figure 3: description ^fig-3
    """
    md = _add_fig_anchors(md)

    # Replace references in text
    md = re.sub(
        r'\[Fig\.\s*(\d+)\]',
        lambda m: f'[[#^fig-{m.group(1)}|Fig. {m.group(1)}]]',
        md, flags=re.IGNORECASE
    )
    md = re.sub(
        r'\[Figure\s*(\d+)\]',
        lambda m: f'[[#^fig-{m.group(1)}|Figure {m.group(1)}]]',
        md, flags=re.IGNORECASE
    )
    md = re.sub(
        r'\(Fig\.\s*(\d+)\)',
        lambda m: f'[[#^fig-{m.group(1)}|Fig. {m.group(1)}]]',
        md, flags=re.IGNORECASE
    )
    md = re.sub(
        r'\(Figure\s*(\d+)\)',
        lambda m: f'[[#^fig-{m.group(1)}|Figure {m.group(1)}]]',
        md, flags=re.IGNORECASE
    )

    return md


def _add_tab_anchors(md: str) -> str:
    """
    Append ^tab-N block IDs to table caption lines.
    """
    def add_anchor(m):
        prefix = m.group(0).rstrip()
        num = m.group(1)
        prefix = re.sub(r'\s*\^tab-\d+$', '', prefix)
        return f"{prefix} ^tab-{num}"

    md = re.sub(
        r'^Table\s+(\d+)\s*[:.].+',
        add_anchor,
        md,
        flags=re.MULTILINE | re.IGNORECASE
    )
    return md


def linkify_tables(md: str) -> str:
    """
    Convert table references to Obsidian block reference links.
    Body: [Table 2] → [[#^tab-2|Table 2]]
    Captions: Table 2: description → Table 2: description ^tab-2
    """
    md = _add_tab_anchors(md)

    md = re.sub(
        r'\[Table\s*(\d+)\]',
        lambda m: f'[[#^tab-{m.group(1)}|Table {m.group(1)}]]',
        md, flags=re.IGNORECASE
    )
    md = re.sub(
        r'\(Table\s*(\d+)\)',
        lambda m: f'[[#^tab-{m.group(1)}|Table {m.group(1)}]]',
        md, flags=re.IGNORECASE
    )

    return md


def inject_frontmatter(md: str, metadata: dict) -> str:
    """
    Prepend YAML frontmatter with paper metadata.
    """
    title = metadata.get('title', 'Untitled Paper')
    authors = metadata.get('authors', [])
    source = metadata.get('source', '')

    content_hash = hashlib.md5(md.encode()).hexdigest()[:8]
    extracted = datetime.now().strftime('%Y-%m-%d')

    frontmatter = f"""---
title: "{title}"
authors: {authors}
source: "{source}"
extracted: "{extracted}"
hash: "{content_hash}"
tags: [paperflow, academic]
---

"""

    return frontmatter + md
