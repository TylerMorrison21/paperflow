"""Compatibility wrapper around the packaged PaperFlow postprocessor."""

from paperflow_postprocess import (
    clean_headers_footers,
    convert_to_footnotes,
    fix_latex_delimiters,
    inject_frontmatter,
    linkify_figures,
    linkify_tables,
    postprocess,
)

__all__ = [
    "postprocess",
    "fix_latex_delimiters",
    "clean_headers_footers",
    "convert_to_footnotes",
    "linkify_figures",
    "linkify_tables",
    "inject_frontmatter",
]
