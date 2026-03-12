import unittest

from paperflow_postprocess import convert_to_footnotes, enhance, postprocess


class PaperflowPostprocessTests(unittest.TestCase):
    def test_convert_to_footnotes_handles_ranges(self) -> None:
        raw = """Body cites [1-3].

## References

[1] One.
[2] Two.
[3] Three.
"""

        result = convert_to_footnotes(raw)

        self.assertIn("Body cites [^1][^2][^3].", result)
        self.assertIn("[^1]: One.", result)
        self.assertIn("[^3]: Three.", result)

    def test_postprocess_injects_frontmatter_and_links_figures(self) -> None:
        raw = """See [Fig. 2].

Figure 2: Sample caption

## References

[1] Example.
"""
        result = postprocess(
            raw_markdown=raw,
            images={},
            metadata={
                "title": "A Paper",
                "authors": ["Alice", "Bob"],
                "source": "https://example.com",
                "date": "2026/03/11",
            },
        )

        self.assertTrue(result.startswith("---\n"))
        self.assertIn('title: "A Paper"', result)
        self.assertIn('source: "https://example.com"', result)
        self.assertIn('date: "2026-03-11"', result)
        self.assertIn('[[#^fig-2|Fig. 2]]', result)
        self.assertIn("Figure 2: Sample caption ^fig-2", result)

    def test_enhance_accepts_none_defaults_and_generic_markdown(self) -> None:
        raw = """A parser gave us this [1].

Figure 3: Generic caption

References
[1] Generic Source.
"""
        result = enhance(raw)

        self.assertIn("[^1]", result)
        self.assertIn("Figure 3: Generic caption ^fig-3", result)
        self.assertIn('title: "Untitled Paper"', result)
        self.assertIn("[^1]: Generic Source.", result)

    def test_convert_to_footnotes_accepts_references_and_notes_heading(self) -> None:
        raw = """Body cites [1].

## References and Notes

[1] Source One.
"""

        result = convert_to_footnotes(raw)

        self.assertIn("Body cites [^1].", result)
        self.assertIn("## References", result)
        self.assertIn("[^1]: Source One.", result)

    def test_convert_to_footnotes_accepts_numbered_reference_entries(self) -> None:
        raw = """Body cites [1] and [2].

Appendix text.

1. Source One.
2) Source Two.
3. Source Three.
"""

        result = convert_to_footnotes(raw)

        self.assertIn("Body cites [^1] and [^2].", result)
        self.assertIn("[^1]: Source One.", result)
        self.assertIn("[^2]: Source Two.", result)
        self.assertIn("[^3]: Source Three.", result)


if __name__ == "__main__":
    unittest.main()
