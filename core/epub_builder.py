"""EPUB generation with ebooklib."""

from ebooklib import epub


def build_epub(pages: list, output_path: str, title: str = "Converted Document") -> None:
    """Build an EPUB file from cleaned page data.

    Args:
        pages: List of PageData objects with cleaned raw_text.
        output_path: Where to write the .epub file.
        title: Book title for EPUB metadata.
    """
    book = epub.EpubBook()
    book.set_identifier("pdfreflow-output")
    book.set_title(title)
    book.set_language("en")

    chapters = []
    for page in pages:
        ch = epub.EpubHtml(
            title=f"Page {page.page_number}",
            file_name=f"page_{page.page_number}.xhtml",
            lang="en",
        )
        ch.content = f"<html><body>{_markdown_to_html(page.raw_text)}</body></html>"
        book.add_item(ch)
        chapters.append(ch)

    # Table of contents and spine
    book.toc = chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + chapters

    epub.write_epub(output_path, book)


def _markdown_to_html(text: str) -> str:
    """Minimal Markdown-to-HTML conversion for EPUB content.

    Args:
        text: Markdown-formatted text.

    Returns:
        HTML string.
    """
    # TODO: Use a proper Markdown library for full conversion
    paragraphs = text.split("\n\n")
    return "".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip())
