#!/usr/bin/env python3
"""Compare the MkDocs build with the Zensical build during the transition (Phase 0-2 only).

For every page URL present in both site directories, compares:
  <title>, first <h1>, and the counts of .arithmatex math spans, <table>, .admonition,
  .tabbed-set, mermaid blocks, <img>, .md-button and footnotes.
Site-wide: Google Fonts link present, favicon link present, the custom
[data-md-color-scheme="fractals"] CSS is shipped, and the number of navigation tabs.

Prints a table of per-page differences (expected ones -- e.g. notebook pages that
mkdocs-jupyter rendered differently -- can be filtered with --ignore PREFIX).
Exit 1 with --fail-on-diff when any unexpected difference remains.

Usage: python scripts/compare_builds.py --old test-site --new site [--ignore notebooks/] [--fail-on-diff] [--expect-tabs 7]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")
COUNTS = {
    "math": re.compile(r'class="[^"]*\barithmatex\b'),
    "table": re.compile(r"<table\b", re.I),
    "admonition": re.compile(r'class="[^"]*\badmonition\b'),
    "tabbed": re.compile(r'class="[^"]*\btabbed-set\b'),
    "mermaid": re.compile(r'class="[^"]*\bmermaid\b'),
    "img": re.compile(r"<img\b", re.I),
    "button": re.compile(r'class="[^"]*\bmd-button\b'),
    "footnote": re.compile(r'class="[^"]*\bfootnote-ref\b'),
}


def clean(s: str) -> str:
    return " ".join(TAG_RE.sub("", s).replace("¶", "").split())


def page_stats(html: str) -> dict:
    t = TITLE_RE.search(html)
    h = H1_RE.search(html)
    stats = {"title": clean(t.group(1)) if t else "", "h1": clean(h.group(1)) if h else ""}
    for name, rx in COUNTS.items():
        stats[name] = len(rx.findall(html))
    return stats


def pages(site: Path) -> dict[str, Path]:
    out = {}
    for html in site.rglob("index.html"):
        rel = html.parent.relative_to(site).as_posix()
        if rel.split("/")[0] in ("react", "assets", "search"):
            continue
        out["" if rel == "." else rel + "/"] = html
    return out


def is_stub(html: str) -> bool:
    return 'http-equiv="refresh"' in html[:4000] or "<title>Redirecting...</title>" in html[:4000]


def site_checks(site: Path, expect_tabs: int) -> dict:
    home = (site / "index.html").read_text(encoding="utf-8", errors="replace") if (site / "index.html").is_file() else ""
    css_hit = False
    for css in site.rglob("*.css"):
        if 'data-md-color-scheme="fractals"' in css.read_text(encoding="utf-8", errors="replace"):
            css_hit = True
            break
    tabs = len(re.findall(r'class="md-tabs__item', home))
    return {
        "google_fonts": "fonts.googleapis.com" in home,
        "favicon": bool(re.search(r'<link[^>]+rel="icon"', home)),
        "fractals_css": css_hit,
        "tabs": tabs,
        "tabs_ok": tabs == expect_tabs,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--old", required=True, help="MkDocs output directory")
    ap.add_argument("--new", required=True, help="Zensical output directory")
    ap.add_argument("--ignore", action="append", default=[], help="URL prefix whose differences are expected (repeatable)")
    ap.add_argument("--expect-tabs", type=int, default=7)
    ap.add_argument("--fail-on-diff", action="store_true")
    args = ap.parse_args(argv)
    old, new = Path(args.old), Path(args.new)
    if not old.is_dir() or not new.is_dir():
        print("ERROR both --old and --new must be built site directories", file=sys.stderr)
        return 2
    po, pn = pages(old), pages(new)
    common = sorted(set(po) & set(pn))
    only_old = sorted(set(po) - set(pn))
    only_new = sorted(set(pn) - set(po))
    diffs: list[str] = []
    for url in common:
        ho = po[url].read_text(encoding="utf-8", errors="replace")
        hn = pn[url].read_text(encoding="utf-8", errors="replace")
        if is_stub(hn) or is_stub(ho):
            continue
        so, sn = page_stats(ho), page_stats(hn)
        changed = {k: (so[k], sn[k]) for k in so if so[k] != sn[k]}
        if changed:
            expected = any(url.startswith(p) for p in args.ignore)
            line = f"{'(expected) ' if expected else ''}/{url}: " + ", ".join(f"{k}: {a!r} -> {b!r}" for k, (a, b) in changed.items())
            if not expected:
                diffs.append(line)
            print(line)
    print(f"\ncompared {len(common)} common pages; {len(only_old)} only in old, {len(only_new)} only in new")
    if only_old:
        print("only in old (should be redirect stubs or deliberately removed):")
        for u in only_old[:200]:
            print(f"  /{u}")
    if only_new:
        print("only in new:")
        for u in only_new[:200]:
            print(f"  /{u}")
    checks = site_checks(new, args.expect_tabs)
    print("site-wide (new):", ", ".join(f"{k}={v}" for k, v in checks.items()))
    bad_site = [k for k in ("google_fonts", "favicon", "fractals_css", "tabs_ok") if not checks[k]]
    if bad_site:
        print(f"site-wide problems: {bad_site}")
    if args.fail_on_diff and (diffs or bad_site):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
