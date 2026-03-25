"""Cross-platform command resolution helpers."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Iterable


_WINDOWS_EXTENSIONS = (".cmd", ".exe", ".bat", ".com")


def is_windows() -> bool:
    return platform.system().lower() == "windows"


def resolve_command(command: str) -> str | None:
    """Resolve a command or path to an executable entrypoint.

    On Windows, explicitly tries common executable/script suffixes so npm-generated
    shims like ``iflow.cmd`` and ``npm.cmd`` can be found reliably.
    """
    raw = (command or "").strip()
    if not raw:
        return None

    candidate = Path(raw).expanduser()
    if candidate.parent != Path(".") or candidate.is_absolute():
        if candidate.exists():
            return str(candidate)
        if is_windows() and not candidate.suffix:
            for ext in _WINDOWS_EXTENSIONS:
                alt = candidate.with_suffix(ext)
                if alt.exists():
                    return str(alt)
        return None

    found = shutil.which(raw)
    if found:
        return found

    if is_windows() and not Path(raw).suffix:
        for ext in _WINDOWS_EXTENSIONS:
            found = shutil.which(raw + ext)
            if found:
                return found

    return None


def prepare_subprocess_command(cmd: Iterable[str]) -> list[str]:
    """Prepare a subprocess command with Windows shim support.

    If the resolved executable is a ``.cmd``/``.bat`` shim, route it through
    ``cmd.exe /d /c`` explicitly instead of relying on ``shell=True``.
    """
    parts = [str(x) for x in cmd]
    if not parts:
        raise ValueError("empty command")

    resolved = resolve_command(parts[0])
    if not resolved:
        raise FileNotFoundError(parts[0])

    if is_windows() and Path(resolved).suffix.lower() in {".cmd", ".bat"}:
        comspec = os.environ.get("COMSPEC") or "cmd.exe"
        return [comspec, "/d", "/c", resolved, *parts[1:]]

    return [resolved, *parts[1:]]


def run_command(cmd: Iterable[str], **kwargs) -> subprocess.CompletedProcess:
    prepared = prepare_subprocess_command(cmd)
    return subprocess.run(prepared, **kwargs)
