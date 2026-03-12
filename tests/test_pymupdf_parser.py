import unittest
from unittest.mock import patch

from api.services import pymupdf_parser


class FakeTable:
    def __init__(self, markdown: str) -> None:
        self._markdown = markdown

    def to_markdown(self) -> str:
        return self._markdown


class FakeTableFinder:
    def __init__(self, tables) -> None:
        self.tables = tables


class FakePage:
    def __init__(self, markdown: str = "", blocks=None, tables=None) -> None:
        self._markdown = markdown
        self._blocks = blocks or []
        self._tables = tables or []

    def get_text(self, mode: str, sort: bool = False):
        if mode == "markdown":
            return self._markdown
        if mode == "blocks":
            return self._blocks
        raise AssertionError(f"Unexpected mode: {mode}")

    def find_tables(self):
        return FakeTableFinder(self._tables)


class FakeDoc(list):
    metadata = {}


class PyMuPDFParserTests(unittest.TestCase):
    def test_extract_markdown_prefers_pymupdf4llm_when_available(self) -> None:
        fake_doc = FakeDoc()

        class FakePyMuPDF4LLM:
            @staticmethod
            def to_markdown(doc, **kwargs):
                self.assertIs(doc, fake_doc)
                self.assertIn("page_separators", kwargs)
                return "# Better markdown"

        with patch.object(pymupdf_parser, "pymupdf4llm", FakePyMuPDF4LLM):
            markdown = pymupdf_parser._extract_markdown(fake_doc)

        self.assertEqual(markdown, "# Better markdown")

    def test_extract_page_markdown_falls_back_to_sorted_blocks(self) -> None:
        page = FakePage(
            markdown="",
            blocks=[
                (0, 0, 10, 10, "First block", 0, 0),
                (0, 12, 10, 22, "Second block", 0, 0),
            ],
        )

        markdown = pymupdf_parser._extract_page_markdown(page)

        self.assertEqual(markdown, "First block\n\nSecond block")

    def test_extract_page_markdown_appends_table_markdown(self) -> None:
        page = FakePage(
            markdown="Body text",
            tables=[FakeTable("| A |\n| - |\n| 1 |")],
        )

        markdown = pymupdf_parser._extract_page_markdown(page)

        self.assertIn("Body text", markdown)
        self.assertIn("| A |", markdown)


if __name__ == "__main__":
    unittest.main()
