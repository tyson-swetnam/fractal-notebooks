#!/usr/bin/env python3
"""Stage the two OKF exchange bundles into the docs tree for the Zensical build.

    okf/concepts/**/*.md  ->  docs/okf/concepts/   (verbatim copy)
    okf/proofs/**/*.md    ->  docs/okf/proofs/     (verbatim copy)

Stale files are deleted ONLY inside those two directories; docs/okf/index.md is
hand-written, tracked, and never touched. Both target directories are gitignored
(build-time copies); the canonical bundles stay in okf/.

Usage: python scripts/stage_okf.py [--okf okf] [--docs docs] [--check]
  --check   report what would change and exit 1 if anything differs (writes nothing)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from okf_common import ROOT  # noqa: E402

BUNDLES = ("concepts", "proofs")


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def stage(okf: Path, docs: Path, check: bool = False) -> tuple[int, int, int, list[str]]:
    """Return (copied, unchanged, removed, problems)."""
    copied = unchanged = removed = 0
    problems: list[str] = []
    for bundle in BUNDLES:
        src_root = okf / bundle
        dst_root = docs / "okf" / bundle
        if not src_root.is_dir():
            problems.append(f"{src_root}: bundle directory not found")
            continue
        wanted: dict[Path, bytes] = {}
        for src in sorted(src_root.rglob("*.md")):
            if any(part.startswith(".") for part in src.relative_to(src_root).parts):
                continue
            wanted[dst_root / src.relative_to(src_root)] = src.read_bytes()
        if dst_root.is_dir():
            for existing in sorted(dst_root.rglob("*")):
                if existing.is_file() and existing not in wanted:
                    removed += 1
                    if check:
                        problems.append(f"{_rel(existing)}: stale (would be removed)")
                    else:
                        existing.unlink()
            if not check:
                for d in sorted((p for p in dst_root.rglob("*") if p.is_dir()), reverse=True):
                    if not any(d.iterdir()):
                        d.rmdir()
        for dst, data in wanted.items():
            if dst.exists() and dst.read_bytes() == data:
                unchanged += 1
                continue
            copied += 1
            if check:
                problems.append(f"{_rel(dst)}: {'differs' if dst.exists() else 'missing'}")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(data)
    return copied, unchanged, removed, problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--okf", default=str(ROOT / "okf"))
    ap.add_argument("--docs", default=str(ROOT / "docs"))
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    copied, unchanged, removed, problems = stage(Path(args.okf), Path(args.docs), args.check)
    for p in problems:
        print(("DRIFT " if args.check else "ERROR ") + p, file=sys.stderr)
    verb = "would copy" if args.check else "copied"
    print(f"stage_okf: {verb} {copied}, unchanged {unchanged}, removed {removed} file(s) under docs/okf/{{concepts,proofs}}")
    if problems:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
