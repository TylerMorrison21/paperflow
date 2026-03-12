import subprocess
import unittest
from unittest.mock import patch

from api.services import local_cli_parser, marker_local_parser, paddleocr_vl_parser


class ParserReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        local_cli_parser._PROBE_CACHE.clear()
        local_cli_parser._PROBE_IN_FLIGHT.clear()

    def test_command_invocation_available_requires_successful_probe(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["fake", "--help"],
            returncode=0,
            stdout="doc_parser help output",
            stderr="",
        )

        with (
            patch.object(local_cli_parser, "command_available", return_value=True),
            patch("api.services.local_cli_parser.subprocess.run", return_value=completed),
        ):
            result = local_cli_parser.command_invocation_available(
                "fake",
                ["doc_parser", "-h"],
                expected_text="doc_parser",
            )

        self.assertTrue(result)

    def test_command_invocation_available_rejects_failed_probe(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["fake", "--help"],
            returncode=1,
            stdout="",
            stderr="unknown command",
        )

        with (
            patch.object(local_cli_parser, "command_available", return_value=True),
            patch("api.services.local_cli_parser.subprocess.run", return_value=completed),
        ):
            result = local_cli_parser.command_invocation_available(
                "fake",
                ["doc_parser", "-h"],
                expected_text="doc_parser",
            )

        self.assertFalse(result)

    def test_command_invocation_available_uses_short_cache(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["fake", "--help"],
            returncode=0,
            stdout="doc_parser help output",
            stderr="",
        )

        with (
            patch.object(local_cli_parser, "command_available", return_value=True),
            patch("api.services.local_cli_parser.subprocess.run", return_value=completed) as run_mock,
        ):
            first = local_cli_parser.command_invocation_available(
                "fake",
                ["doc_parser", "-h"],
                expected_text="doc_parser",
            )
            second = local_cli_parser.command_invocation_available(
                "fake",
                ["doc_parser", "-h"],
                expected_text="doc_parser",
            )

        self.assertTrue(first)
        self.assertTrue(second)
        self.assertEqual(run_mock.call_count, 1)

    def test_paddleocr_parser_available_uses_doc_parser_probe(self) -> None:
        with patch("api.services.paddleocr_vl_parser.command_invocation_available", return_value=True) as probe:
            self.assertTrue(paddleocr_vl_parser.parser_available())

        probe.assert_called_once_with(
            paddleocr_vl_parser.PADDLEOCR_VL_CMD,
            ["doc_parser", "-h"],
            expected_text="doc_parser",
            cache_ttl_seconds=15.0,
            blocking=True,
        )

    def test_marker_local_parser_available_uses_help_probe(self) -> None:
        with patch("api.services.marker_local_parser.command_invocation_available", return_value=True) as probe:
            self.assertTrue(marker_local_parser.parser_available())

        probe.assert_called_once_with(
            marker_local_parser.MARKER_SINGLE_CMD,
            ["--help"],
            expected_text="marker",
            cache_ttl_seconds=15.0,
            blocking=True,
        )

    def test_non_blocking_probe_returns_cached_or_false_and_skips_wait(self) -> None:
        with (
            patch.object(local_cli_parser, "command_available", return_value=True),
            patch("api.services.local_cli_parser.threading.Thread") as thread_cls,
        ):
            result = local_cli_parser.command_invocation_available(
                "fake",
                ["doc_parser", "-h"],
                expected_text="doc_parser",
                blocking=False,
            )

        self.assertFalse(result)
        thread_cls.assert_called_once()


if __name__ == "__main__":
    unittest.main()
