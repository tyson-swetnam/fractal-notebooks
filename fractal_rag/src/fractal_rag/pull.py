"""Wrap ``gocmd`` to mirror the iRODS corpus to local disk.

Why ``gocmd`` rather than the iRODS MCP server: the MCP server is restricted
to ``/iplant/home/shared/*`` paths, but the corpus lives under the user's
home (``/iplant/home/tswetnam/fractal-notebooks/``). ``gocmd`` reuses the
existing ``~/.irods/`` auth.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import Settings, get_settings


class GoCmdMissingError(RuntimeError):
    pass


class GoCmdError(RuntimeError):
    pass


@dataclass
class PullResult:
    irods_root: str
    local_root: Path
    returncode: int
    stdout: str
    stderr: str


def _resolve_gocmd() -> str:
    path = shutil.which("gocmd")
    if path is None:
        raise GoCmdMissingError(
            "gocmd not found on PATH. Install per "
            "https://github.com/cyverse/gocommands and ensure ~/.irods/ is set up."
        )
    return path


def pull(
    *,
    settings: Settings | None = None,
    force: bool = False,
    dry_run: bool = False,
) -> PullResult:
    """Mirror ``irods_root`` to ``corpus_root``.

    By default gocmd skips files whose checksum matches; ``force=True`` passes
    ``--no-skip`` so every file is re-fetched.
    """
    s = settings or get_settings()
    s.corpus_root.mkdir(parents=True, exist_ok=True)

    gocmd = _resolve_gocmd()
    args = [gocmd, "get", "-fr", s.irods_root, str(s.corpus_root)]
    if force:
        args.append("--no-skip")

    if dry_run:
        return PullResult(
            irods_root=s.irods_root,
            local_root=s.corpus_root,
            returncode=0,
            stdout=" ".join(args),
            stderr="",
        )

    proc = subprocess.run(args, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise GoCmdError(
            f"gocmd get failed (exit {proc.returncode}):\n"
            f"stdout: {proc.stdout[-2000:]}\n"
            f"stderr: {proc.stderr[-2000:]}"
        )
    return PullResult(
        irods_root=s.irods_root,
        local_root=s.corpus_root,
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )
