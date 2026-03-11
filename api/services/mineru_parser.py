from __future__ import annotations

import tempfile
from pathlib import Path

from api.config import MINERU_ARGS, MINERU_CMD
from api.services.local_cli_parser import command_available, load_parser_output, run_cli, split_extra_args


def parser_available() -> bool:
    return command_available(MINERU_CMD)


async def parse_pdf(pdf_bytes: bytes) -> dict:
    if not parser_available():
        raise RuntimeError(
            "MinerU is not installed. Install MinerU and make sure "
            f"'{MINERU_CMD}' is on PATH, or set MINERU_CMD."
        )

    with tempfile.TemporaryDirectory(prefix="paperflow-mineru-") as temp_dir:
        work_dir = Path(temp_dir)
        input_path = work_dir / "input.pdf"
        output_dir = work_dir / "output"
        input_path.write_bytes(pdf_bytes)
        output_dir.mkdir(parents=True, exist_ok=True)

        args = [
            "-p",
            str(input_path),
            "-o",
            str(output_dir),
        ]
        args.extend(split_extra_args(MINERU_ARGS))

        await run_cli(MINERU_CMD, args, work_dir, "MinerU")
        result = load_parser_output(output_dir, "MinerU", preferred_stem=input_path.stem)
        result["metadata"] = {
            "source": "MinerU local parser",
        }
        return result
