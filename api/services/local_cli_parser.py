from __future__ import annotations

import asyncio
import base64
import logging
import shlex
import shutil
import subprocess
import threading
import time
from pathlib import Path

logger = logging.getLogger(__name__)

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg"}
_PROBE_CACHE: dict[tuple[str, tuple[str, ...], str], tuple[float, bool]] = {}
_PROBE_IN_FLIGHT: set[tuple[str, tuple[str, ...], str]] = set()
_PROBE_LOCK = threading.Lock()


def command_available(command: str) -> bool:
    if not command:
        return False

    if Path(command).exists():
        return True

    return shutil.which(command) is not None


def command_invocation_available(
    command: str,
    args: list[str],
    *,
    timeout_seconds: int = 4,
    expected_text: str = "",
    cache_ttl_seconds: float = 5.0,
    blocking: bool = True,
) -> bool:
    cache_key = (command, tuple(args), expected_text.casefold())
    now = time.monotonic()
    cached = _PROBE_CACHE.get(cache_key)
    if cached and now - cached[0] < cache_ttl_seconds:
        return cached[1]

    if not blocking:
        _refresh_probe_in_background(
            cache_key,
            command,
            args,
            timeout_seconds=timeout_seconds,
            expected_text=expected_text,
        )
        return cached[1] if cached else False

    return _run_probe(
        cache_key,
        command,
        args,
        timeout_seconds=timeout_seconds,
        expected_text=expected_text,
    )


def _refresh_probe_in_background(
    cache_key: tuple[str, tuple[str, ...], str],
    command: str,
    args: list[str],
    *,
    timeout_seconds: int,
    expected_text: str,
) -> None:
    with _PROBE_LOCK:
        if cache_key in _PROBE_IN_FLIGHT:
            return
        _PROBE_IN_FLIGHT.add(cache_key)

    thread = threading.Thread(
        target=_probe_in_background,
        args=(cache_key, command, args),
        kwargs={
            "timeout_seconds": timeout_seconds,
            "expected_text": expected_text,
        },
        daemon=True,
    )
    thread.start()


def _probe_in_background(
    cache_key: tuple[str, tuple[str, ...], str],
    command: str,
    args: list[str],
    *,
    timeout_seconds: int,
    expected_text: str,
) -> None:
    try:
        _run_probe(
            cache_key,
            command,
            args,
            timeout_seconds=timeout_seconds,
            expected_text=expected_text,
        )
    finally:
        with _PROBE_LOCK:
            _PROBE_IN_FLIGHT.discard(cache_key)


def _run_probe(
    cache_key: tuple[str, tuple[str, ...], str],
    command: str,
    args: list[str],
    *,
    timeout_seconds: int,
    expected_text: str,
) -> bool:
    now = time.monotonic()

    if not command_available(command):
        _PROBE_CACHE[cache_key] = (now, False)
        return False

    try:
        completed = subprocess.run(
            [command, *args],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except (OSError, ValueError, subprocess.TimeoutExpired):
        _PROBE_CACHE[cache_key] = (now, False)
        return False

    if completed.returncode != 0:
        _PROBE_CACHE[cache_key] = (now, False)
        return False

    if not expected_text:
        _PROBE_CACHE[cache_key] = (now, True)
        return True

    combined = f"{completed.stdout}\n{completed.stderr}".casefold()
    result = expected_text.casefold() in combined
    _PROBE_CACHE[cache_key] = (now, result)
    return result


def split_extra_args(raw: str) -> list[str]:
    if not raw.strip():
        return []
    return shlex.split(raw, posix=False)


async def run_cli(command: str, args: list[str], cwd: Path, parser_label: str) -> None:
    process = await asyncio.create_subprocess_exec(
        command,
        *args,
        cwd=str(cwd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        return

    stdout_text = stdout.decode("utf-8", errors="ignore").strip()
    stderr_text = stderr.decode("utf-8", errors="ignore").strip()
    message = stderr_text or stdout_text or f"{parser_label} exited with code {process.returncode}."
    raise RuntimeError(f"{parser_label} failed: {message[-1200:]}")


def load_parser_output(output_dir: Path, parser_label: str, preferred_stem: str = "") -> dict:
    markdown_path = _find_markdown_file(output_dir, preferred_stem=preferred_stem)
    if not markdown_path:
        raise RuntimeError(f"{parser_label} did not produce a markdown file in {output_dir}.")

    markdown = markdown_path.read_text(encoding="utf-8", errors="ignore").strip()
    if not markdown:
        raise RuntimeError(f"{parser_label} produced an empty markdown file.")

    images = _collect_images(output_dir)

    return {
        "markdown": markdown,
        "images": images,
    }


def _find_markdown_file(output_dir: Path, preferred_stem: str = "") -> Path | None:
    candidates = [path for path in output_dir.rglob("*.md") if path.is_file()]
    if not candidates:
        return None

    preferred_stem = preferred_stem.casefold()

    def score(path: Path) -> tuple[int, int, int]:
        same_stem = 1 if preferred_stem and path.stem.casefold() == preferred_stem else 0
        return (same_stem, len(path.parts) * -1, path.stat().st_size)

    return max(candidates, key=score)


def _collect_images(output_dir: Path) -> dict[str, str]:
    images: dict[str, str] = {}

    for image_path in output_dir.rglob("*"):
        if not image_path.is_file():
            continue
        if image_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue

        image_name = image_path.name
        if image_name in images:
            image_name = _dedupe_name(image_name, images)

        images[image_name] = base64.b64encode(image_path.read_bytes()).decode("ascii")

    logger.info("Collected %s images from %s", len(images), output_dir)
    return images


def _dedupe_name(name: str, images: dict[str, str]) -> str:
    path = Path(name)
    stem = path.stem
    suffix = path.suffix
    counter = 2
    candidate = name

    while candidate in images:
        candidate = f"{stem}-{counter}{suffix}"
        counter += 1

    return candidate
