#!/usr/bin/env python3
"""Publish every page's raw Markdown source as a verbatim "twin" inside site/.

Twin rule (what agents and <link rel="alternate" type="text/markdown"> rely on):

    page URL                                   twin
    <site_url>/                                <site_url>/index.md
    <site_url>/foundations/history/            <site_url>/foundations/history.md
    <site_url>/metabolic-scaling/              <site_url>/metabolic-scaling/index.md
    <site_url>/okf/concepts/geometry/fractal/  <site_url>/okf/concepts/geometry/fractal.md

The page list is site/sitemap.xml (Zensical lists not_in_nav pages there and
omits redirect stubs) unioned with every non-excluded docs/**/*.md that has a
rendered index.html. okf/concepts/** and okf/proofs/** URLs resolve against the
repo's canonical okf/ tree, so the published bundle is byte-identical to the
committed one. Redirect stubs are skipped.

Post-conditions (exit 1 when violated):
  * every twin has a rendered sibling index.html;
  * no .ipynb / .py / .yaml / .yml / .geojson under site/ (site/react/ excluded);
  * no path component matching superpowers|_claude|PLAN|README under site/.

--verify additionally parses every site/**/index.html (not react/, not stubs),
reads the rel="alternate" type="text/markdown" href and asserts the file exists.

Usage: python scripts/publish_sources.py [--config zensical.toml] [--site site] [--docs docs] [--okf okf] [--verify] [--verify-only]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from okf_common import (  # noqa: E402
    ConfigError,
    ROOT,
    docs_dir,
    exclude_spec,
    is_excluded,
    load_config,
    site_dir,
    site_root,
    url_to_source_candidates,
)

STUB_RE = re.compile(r'http-equiv="refresh"|<title>Redirecting\.\.\.</title>', re.I)
ALT_RE = re.compile(r'<link[^>]+rel="alternate"[^>]+type="text/markdown"[^>]+href="([^"]+)"|<link[^>]+href="([^"]+)"[^>]+type="text/markdown"[^>]+rel="alternate"', re.I)
FORBIDDEN_EXT = {".ipynb", ".py", ".yaml", ".yml", ".geojson"}
FORBIDDEN_PART = re.compile(r"superpowers|_claude|PLAN|README|\.DS_Store")


def is_redirect_stub_path(p, site):
    """True for a redirect stub written by Zensical's redirects plugin at an old URL
    (an index.html whose head carries <meta http-equiv="refresh">), or for a directory
    that contains nothing but such stubs. Old notes/specs URLs legitimately live on as
    stubs, so the leak check must not flag their path names."""
    try:
        if p.is_file():
            if p.name != "index.html" or p.stat().st_size > 4000:
                return False
            return 'http-equiv="refresh"' in p.read_text(encoding="utf-8", errors="replace")
        if p.is_dir():
            files = [f for f in p.rglob("*") if f.is_file()]
            return bool(files) and all(is_redirect_stub_path(f, site) for f in files)
    except OSError:
        return False
    return False
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def sitemap_paths(site: Path, base: str) -> list[str]:
    """URL paths (relative to the site root, trailing slash kept) listed in sitemap.xml."""
    sm = site / "sitemap.xml"
    if not sm.is_file():
        return []
    tree = ElementTree.parse(sm)
    out: list[str] = []
    for loc in tree.getroot().iter(f"{SITEMAP_NS}loc"):
        url = (loc.text or "").strip()
        if not url:
            continue
        if url.startswith(base):
            path = url[len(base):]
        else:
            path = urlparse(url).path
        out.append(unquote(path).lstrip("/"))
    return out


def is_stub(html_path: Path) -> bool:
    try:
        head = html_path.read_text(encoding="utf-8", errors="replace")[:4000]
    except OSError:
        return False
    return bool(STUB_RE.search(head))


def resolve_source(url_path: str, docs: Path, okf: Path) -> tuple[Path, str] | None:
    """Return (source file, twin path relative to site/) for a page URL path.

    okf/concepts/** and okf/proofs/** resolve against the canonical okf/ tree; everything
    else (including the hand-written docs/okf/index.md) against docs/.
    """
    path = url_path.strip("/")
    for candidate in url_to_source_candidates(path):
        if candidate.startswith(("okf/concepts/", "okf/proofs/")):
            src = okf / candidate[len("okf/"):]
            if src.is_file():
                return src, candidate
            continue
        src = docs / candidate
        if src.is_file():
            return src, candidate
    return None


def rel_url_path(site: Path, html_path: Path) -> str:
    rel = html_path.parent.relative_to(site).as_posix()
    return "" if rel == "." else rel + "/"


def publish(cfg: dict, site: Path, docs: Path, okf: Path) -> tuple[int, list[str]]:
    base = site_root(cfg) + "/"
    spec = exclude_spec(cfg)
    errors: list[str] = []

    candidates: list[str] = sitemap_paths(site, base)
    seen = set(candidates)
    for md in sorted(docs.rglob("*.md")):
        rel = md.relative_to(docs).as_posix()
        if is_excluded(spec, rel):
            continue
        url_path = "" if rel == "index.md" else (rel[: -len("index.md")] if rel.endswith("/index.md") else rel[:-3] + "/")
        if url_path not in seen and (site / url_path / "index.html").is_file():
            candidates.append(url_path)
            seen.add(url_path)

    written = 0
    for url_path in candidates:
        html = site / url_path / "index.html"
        if not html.is_file():
            errors.append(f"{url_path or '/'}: listed in sitemap.xml but {html.relative_to(site)} does not exist")
            continue
        if is_stub(html):
            continue
        resolved = resolve_source(url_path, docs, okf)
        if resolved is None:
            errors.append(f"{url_path or '/'}: no Markdown source found for this page (tried {url_to_source_candidates(url_path)})")
            continue
        src, twin_rel = resolved
        dest = site / twin_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        if not dest.exists() or dest.read_bytes() != data:
            dest.write_bytes(data)
        written += 1

    # Post-conditions over the whole site (react/ is a separate SPA build).
    for p in sorted(site.rglob("*")):
        rel = p.relative_to(site)
        if rel.parts and rel.parts[0] == "react":
            continue
        if p.is_file() and p.suffix.lower() in FORBIDDEN_EXT:
            errors.append(f"{rel.as_posix()}: forbidden file type published under site/")
        if any(FORBIDDEN_PART.search(part) for part in rel.parts) and not is_redirect_stub_path(p, site):
            errors.append(f"{rel.as_posix()}: internal file/path leaked into site/")
        if p.is_file() and p.suffix == ".md":
            page_dir = p.parent if p.name == "index.md" else p.parent / p.stem
            if not (page_dir / "index.html").is_file():
                errors.append(f"{rel.as_posix()}: twin without a rendered sibling {page_dir.relative_to(site).as_posix()}/index.html")
    return written, errors


def verify(cfg: dict, site: Path) -> tuple[int, list[str]]:
    base = site_root(cfg) + "/"
    errors: list[str] = []
    checked = 0
    for html in sorted(site.rglob("index.html")):
        rel = html.relative_to(site)
        if rel.parts and rel.parts[0] == "react":
            continue
        text = html.read_text(encoding="utf-8", errors="replace")
        if STUB_RE.search(text[:4000]):
            continue
        m = ALT_RE.search(text)
        if not m:
            errors.append(f"{rel.as_posix()}: no <link rel=\"alternate\" type=\"text/markdown\"> in <head>")
            continue
        href = unquote(m.group(1) or m.group(2))
        if href.startswith(base):
            local = site / href[len(base):]
        elif href.startswith(("http://", "https://")):
            errors.append(f"{rel.as_posix()}: alternate href {href} is outside the site")
            continue
        else:
            local = (html.parent / href).resolve()
        if not local.is_file():
            errors.append(f"{rel.as_posix()}: alternate href {href} -> {local.relative_to(site) if local.is_relative_to(site) else local} does not exist")
            continue
        checked += 1
    return checked, errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None, help="zensical.toml (default: repo root)")
    ap.add_argument("--site", default=None, help="built site directory (default: site_dir from the config)")
    ap.add_argument("--docs", default=None, help="docs directory (default: docs_dir from the config)")
    ap.add_argument("--okf", default=str(ROOT / "okf"), help="canonical OKF bundles (default: okf/)")
    ap.add_argument("--verify", action="store_true", help="after publishing, assert every page's alternate link resolves")
    ap.add_argument("--verify-only", action="store_true", help="only run the alternate-link verification")
    args = ap.parse_args(argv)
    try:
        cfg = load_config(ROOT, args.config)
    except ConfigError as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 2
    site = Path(args.site) if args.site else site_dir(cfg)
    docs = Path(args.docs) if args.docs else docs_dir(cfg)
    if not site.is_dir():
        print(f"ERROR {site}: not found; run `zensical build` first", file=sys.stderr)
        return 2
    rc = 0
    if not args.verify_only:
        written, errors = publish(cfg, site, docs, Path(args.okf))
        for e in errors:
            print(f"ERROR {e}", file=sys.stderr)
        print(f"publish_sources: {written} Markdown twins under {site}; {len(errors)} problem(s)")
        rc = 1 if errors else 0
    if args.verify or args.verify_only:
        checked, errors = verify(cfg, site)
        for e in errors:
            print(f"ERROR {e}", file=sys.stderr)
        print(f"publish_sources --verify: {checked} pages with a resolvable text/markdown alternate; {len(errors)} problem(s)")
        rc = rc or (1 if errors else 0)
    return rc


if __name__ == "__main__":
    sys.exit(main())
