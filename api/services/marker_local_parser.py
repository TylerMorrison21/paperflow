from __future__ import annotations

import tempfile
from pathlib import Path

from api.config import MARKER_SINGLE_ARGS, MARKER_SINGLE_CMD
from api.services.local_cli_parser import command_available, load_parser_output, run_cli, split_extra_args


def parser_available() -> bool:
    return command_available(MARKER_SINGLE_CMD)


async def parse_pdf(pdf_bytes: bytes) -> dict:
    if not parser_available():
        raise RuntimeError(
            "Marker self-hosted is not installed. Install marker and make sure "
            f"'{MARKER_SINGLE_CMD}' is on PATH, or set MARKER_SINGLE_CMD."
        )

    with tempfile.TemporaryDirectory(prefix="paperflow-marker-") as temp_dir:
        work_dir = Path(temp_dir)
        input_path = work_dir / "input.pdf"
        output_dir = work_dir / "output"
        input_path.write_bytes(pdf_bytes)
        output_dir.mkdir(parents=True, exist_ok=True)

        args = [
            str(input_path),
            "--output_dir",
            str(output_dir),
            "--output_format",
            "markdown",
        ]
        args.extend(split_extra_args(MARKER_SINGLE_ARGS))

        await run_cli(MARKER_SINGLE_CMD, args, work_dir, "Marker self-hosted")
        result = load_parser_output(output_dir, "Marker self-hosted", preferred_stem=input_path.stem)
        result["metadata"] = {
            "source": "Marker self-hosted",
        }
        return result
