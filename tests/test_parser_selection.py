import unittest
from unittest.mock import patch

from fastapi import HTTPException

from api.routes import submit
from api.services import parsers


class ParserSelectionTests(unittest.TestCase):
    def test_normalize_parser_maps_mineru_to_paddleocr_vl(self) -> None:
        self.assertEqual(submit._normalize_parser("mineru"), "paddleocr_vl")
        self.assertEqual(submit._normalize_parser("  MiNeRu  "), "paddleocr_vl")

    def test_normalize_marker_api_key_requires_byok_for_marker_api(self) -> None:
        with self.assertRaises(HTTPException) as context:
            submit._normalize_marker_api_key("marker_api", "")

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("requires your own Datalab API key", context.exception.detail)

    def test_normalize_marker_api_key_ignores_empty_key_for_other_parsers(self) -> None:
        self.assertEqual(submit._normalize_marker_api_key("pymupdf", ""), "")

    def test_validate_parser_accepts_normalized_alias(self) -> None:
        with patch.object(submit, "list_parsers", return_value=[{"id": "paddleocr_vl", "configured": True, "setup": "ok"}]):
            selected = submit._validate_parser("mineru")

        self.assertEqual(selected["id"], "paddleocr_vl")

    def test_list_parsers_marks_marker_api_as_byok(self) -> None:
        with (
            patch.object(parsers.pymupdf_parser, "parser_available", return_value=True),
            patch.object(parsers.marker_local_parser, "parser_available", return_value=False),
            patch.object(parsers.paddleocr_vl_parser, "parser_available", return_value=False),
        ):
            parser_rows = parsers.list_parsers()

        marker_api = next(row for row in parser_rows if row["id"] == "marker_api")
        self.assertTrue(marker_api["configured"])
        self.assertTrue(marker_api["requires_user_key"])
        self.assertIn("Datalab.to API key", marker_api["setup"])

    def test_list_parsers_uses_requested_display_order_and_commands(self) -> None:
        with (
            patch.object(parsers.pymupdf_parser, "parser_available", return_value=True),
            patch.object(parsers.marker_local_parser, "parser_available", return_value=True),
            patch.object(parsers.paddleocr_vl_parser, "parser_available", return_value=True),
        ):
            parser_rows = parsers.list_parsers()

        self.assertEqual(
            [row["id"] for row in parser_rows],
            ["pymupdf", "paddleocr_vl", "marker_api", "marker_local"],
        )
        self.assertEqual(parser_rows[0]["speed"], "Free")
        self.assertEqual(parser_rows[0]["quality"], "Fastest")
        self.assertEqual(parser_rows[1]["quality"], "Best quality")
        self.assertEqual(parser_rows[2]["speed"], "Easy")
        self.assertEqual(parser_rows[3]["speed"], "Privacy")
        self.assertTrue(parser_rows[1]["commands"])
        self.assertIn("paddleocr doc_parser -h", parser_rows[1]["commands"])
        self.assertIn("text-layer PDFs", parser_rows[0]["best_for"])
        self.assertIn("cloud processing", parser_rows[2]["positioning"])
        self.assertTrue(parser_rows[3]["facts"])


if __name__ == "__main__":
    unittest.main()
