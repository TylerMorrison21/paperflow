from __future__ import annotations

import tempfile
from pathlib import Path

from api.config import PADDLEOCR_VL_ARGS, PADDLEOCR_VL_CMD
from api.services.local_cli_parser import command_invocation_available, load_parser_output, run_cli, split_extra_args


def parser_available(*, blocking: bool = True) -> bool:
    return command_invocation_available(
        PADDLEOCR_VL_CMD,
        ["doc_parser", "-h"],
        expected_text="doc_parser",
        cache_ttl_seconds=15.0,
        blocking=blocking,
    )


async def parse_pdf(pdf_bytes: bytes) -> dict:
    if not parser_available():
        raise RuntimeError(
            "PaddleOCR-VL-0.9B is not installed. Install PaddleOCR with document parsing support and make sure "
            f"'{PADDLEOCR_VL_CMD}' is on PATH, or set PADDLEOCR_VL_CMD."
        )

    with tempfile.TemporaryDirectory(prefix="paperflow-paddleocr-vl-") as temp_dir:
        work_dir = Path(temp_dir)
        input_path = work_dir / "input.pdf"
        output_dir = work_dir / "output"
        input_path.write_bytes(pdf_bytes)
        output_dir.mkdir(parents=True, exist_ok=True)

        args = [
            "doc_parser",
            "-i",
            str(input_path),
            "--device",
            "cpu",
            "--save_path",
            str(output_dir),
        ]
        args.extend(split_extra_args(PADDLEOCR_VL_ARGS))

        await run_cli(PADDLEOCR_VL_CMD, args, work_dir, "PaddleOCR-VL-0.9B")
        result = load_parser_output(output_dir, "PaddleOCR-VL-0.9B", preferred_stem=input_path.stem)
        result["metadata"] = {
            "source": "PaddleOCR-VL-0.9B local parser",
        }
        return result
