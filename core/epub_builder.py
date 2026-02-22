"""EPUB generation via Pandoc.

Pipeline:
  Marker Markdown + images
    → _unwrap_lines (fix soft-wraps & invisible chars)
    → temp directory (input.md + images/)
    → pandoc --epub-chapter-level=1 --toc --css=epub_style.css
    → EPUB3
"""

import base64
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from spellchecker import SpellChecker

_spell = SpellChecker()  # loaded once at import time

_CSS_PATH = Path(__file__).with_name("epub_style.css")


# ── markdown preprocessor ───────────────────────────────────────────────────────

def _unwrap_lines(text: str) -> str:
    """Join soft-wrapped lines in Marker markdown before passing to Pandoc.

    Silver bullet: purge invisible zero-width spaces and soft hyphens first.

    Pass 0 — NLP smart_merge:
      For each letter-block + newline + letter-block, decide whether to
      join with or without a space using a spell-checker dictionary:
        - combined is a known word AND at least one fragment is unknown
          → join without space  (e.g. "diff" + "erent" → "different")
        - both fragments are already known words, or combined is unknown
          → join with space     (e.g. "long" + "word" → "long word")

    Pass 1 — buffer approach:
      Protects structural markdown elements (headings, lists, tables, etc.)
      from being merged into surrounding paragraphs.
    """
    # Silver bullet: purge invisible zero-width spaces and soft hyphens
    text = re.sub(r'[\u200b\u200c\u200d\u00ad\xad]', '', text)

    # Pass 0 — NLP smart merge
    def smart_merge(m: re.Match) -> str:
        w1, w2 = m.group(1), m.group(2)
        combined = w1 + w2
        if _spell.known([combined.lower()]):
            if _spell.known([w1.lower()]) and _spell.known([w2.lower()]):
                return w1 + ' ' + w2   # both halves are real words → keep space
            else:
                return combined        # fragment join (e.g. "advanc" + "ing")
        else:
            return w1 + ' ' + w2       # combined not a word → two separate words

    text = re.sub(r'([a-zA-Z]+) *\n *([a-zA-Z]+)', smart_merge, text)

    # Pass 1 — buffer approach: structural markdown guard
    new_lines: list[str] = []
    buffer = ""
    for line in text.split('\n'):
        stripped = line.strip()

        # Blank line = paragraph boundary, flush buffer
        if not stripped:
            if buffer:
                new_lines.append(buffer)
                buffer = ""
            new_lines.append("")
            continue

        # Structural elements — flush buffer and pass through as-is
        if stripped.startswith(('#', '-', '*', '>', '!', '```', '|')) \
                or re.match(r'^\d+[\.\、]', stripped):
            if buffer:
                new_lines.append(buffer)
                buffer = ""
            new_lines.append(line)
            continue

        # Regular text — merge into buffer
        if buffer:
            if buffer.endswith('-'):
                buffer = buffer[:-1] + stripped   # rejoin hard-hyphenated word
            else:
                buffer += " " + stripped
        else:
            buffer = stripped

    if buffer:
        new_lines.append(buffer)

    return '\n'.join(new_lines)


# ── EPUB post-processor ─────────────────────────────────────────────────────────

def _fix_epub_xhtml(epub_path: str) -> None:
    """Rewrite the EPUB zip in-place, fixing non-XHTML-compliant void tags.

    Pandoc 3.x emits bare <br> and <hr> inside table cells even when targeting
    EPUB3/XHTML. Apple Books (and epub-check) reject these. We patch every
    .xhtml file in the zip after Pandoc writes it.
    """
    tmp_path = epub_path + ".xhtml_fix.tmp"
    with zipfile.ZipFile(epub_path, "r") as zin, \
         zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith((".xhtml", ".html")):
                text = data.decode("utf-8")
                # <br\s*> matches <br> and <br > but NOT <br/> or <br />
                text = re.sub(r'<br\s*>', '<br/>', text)
                text = re.sub(r'<hr\s*>', '<hr/>', text)
                # <img ...> without trailing slash → <img .../>
                text = re.sub(r'<img([^>]*[^/])>', r'<img\1/>', text)
                data = text.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(tmp_path, epub_path)


# ── public API ──────────────────────────────────────────────────────────────────

def build_epub_from_markdown(
    markdown: str,
    images: dict[str, str],
    output_path: str,
    title: str = "Converted Document",
) -> None:
    """Build EPUB3 from Marker markdown + base64 images using Pandoc.

    Steps:
      1. Preprocess markdown (_unwrap_lines)
      2. Write input.md + images/ to a temp directory
      3. Run pandoc and write EPUB to output_path
    """
    markdown = _unwrap_lines(markdown)

    # Fix non-XHTML-compliant void tags from Marker raw HTML
    markdown = re.sub(r'<br\s*(?!/?)>', '<br/>', markdown)
    markdown = re.sub(r'<hr\s*(?!/?)>', '<hr/>', markdown)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Prepend YAML front matter so Pandoc picks up the title
        front_matter = f'---\ntitle: "{title.replace(chr(34), chr(39))}"\n---\n\n'
        md_path = tmp_path / "input.md"
        md_path.write_text(front_matter + markdown, encoding="utf-8")

        # Decode and save images alongside input.md so Pandoc resolves them
        # by relative path (Marker markdown refs are plain "filename.jpg", no subdir)
        print(f"[epub_builder] images received: {len(images)} — {list(images.keys())}")
        for name, b64 in images.items():
            try:
                (tmp_path / name).write_bytes(base64.b64decode(b64))
            except Exception as exc:
                print(f"[epub_builder] skipping image {name!r}: {exc}")

        # Run Pandoc — output_path must be absolute because cwd=tmp
        abs_output = str(Path(output_path).resolve())
        cmd = [
            "pandoc",
            str(md_path),
            "-o", abs_output,
            "--from=markdown+raw_html",
            f"--css={_CSS_PATH}",
            "--toc",
            "--epub-chapter-level=1",
            "--wrap=none",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=tmp)
        if result.returncode != 0:
            raise RuntimeError(f"Pandoc failed:\n{result.stderr}")

    # Post-process: fix non-XHTML-compliant void tags Pandoc emits in tables
    _fix_epub_xhtml(abs_output)
    print(f"[epub_builder] EPUB written → {output_path} (via Pandoc)")
