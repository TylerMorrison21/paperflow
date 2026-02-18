"""Text cleaning for Markdown content from the scanned PDF pipeline."""

import re

# PaddleOCR-VL sometimes leaks internal layout-position tokens into its output.
_LOC_TOKEN_RE = re.compile(r"<\|LOC_\d+\|>")

# Repetition heuristic: if any single token repeats ≥ this many times the page
# is likely a diagram hallucination and should be blanked.
_REPETITION_THRESHOLD = 20


def clean_text(page) -> "PageData":
    """Clean markdown text on a PageData object (scanned pipeline output).

    Args:
        page: A PageData object with .markdown to clean.

    Returns:
        The same PageData object with cleaned markdown.
    """
    text = page.markdown
    text = strip_loc_tokens(text)
    text = remove_headers_footers(text)
    text = merge_broken_lines(text)
    text = remove_duplicate_blank_lines(text)
    if _is_hallucination(text):
        text = ""
    page.markdown = text.strip()
    return page


def strip_loc_tokens(text: str) -> str:
    """Remove PaddleOCR internal layout-position tokens (e.g. <|LOC_137|>)."""
    return _LOC_TOKEN_RE.sub("", text)


def _is_hallucination(text: str) -> bool:
    """Return True if the page looks like model hallucination.

    Detects repetitive-token output (e.g. hundreds of 'T T T' or 'https://www.')
    that the model generates when it cannot read an image-heavy page.
    """
    if not text.strip():
        return False
    # Tokenise on whitespace and check if any single token dominates
    tokens = text.split()
    if len(tokens) < _REPETITION_THRESHOLD:
        return False
    from collections import Counter
    most_common_token, count = Counter(tokens).most_common(1)[0]
    return count / len(tokens) > 0.4


def remove_headers_footers(text: str) -> str:
    """Remove standalone page numbers (e.g. '— 3 —', '3', '.3.')."""
    text = re.sub(r"^\s*[-–—.]?\s*\d+\s*[-–—.]?\s*$", "", text, flags=re.MULTILINE)
    return text


def merge_broken_lines(text: str) -> str:
    """Merge lines that were broken mid-sentence by PDF hard returns.

    Supports both English and Chinese text.

    Args:
        text: Text with potential mid-sentence line breaks.

    Returns:
        Text with broken lines merged into proper paragraphs.
    """
    # English: join lines ending with lowercase/comma that continue with lowercase
    text = re.sub(r"(?<=[a-z,;])\n(?=[a-z])", " ", text)
    # Chinese: join lines not ending with Chinese punctuation followed by Chinese chars
    text = re.sub(
        r"(?<=[^\n。！？；」）】\s])\n(?=[\u4e00-\u9fff])", "", text
    )
    return text


def remove_duplicate_blank_lines(text: str) -> str:
    """Collapse multiple consecutive blank lines into one."""
    return re.sub(r"\n{3,}", "\n\n", text)
