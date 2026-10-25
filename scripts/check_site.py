#!/usr/bin/env python3
"""Post-build checks over the Zensical output (run last in scripts/build_site.sh).

Checks (each prints `ok   <name>: ...` or `FAIL <name>: ...`; exit 1 on any FAIL):

  coverage   every path in scripts/fixtures/live-urls-<date>.txt (the sitemap of the
             MkDocs site captured before the cutover; '/' is the home page, blank and
             # lines are skipped) resolves to a built page or a redirect stub. Stubs are
             recognised by <meta http-equiv="refresh"> or by a <link rel="canonical">
             that points elsewhere (Zensical writes both).
  links      every internal href/src in site/**/*.html (site/react/ skipped) resolves to a
             file, and every #anchor to an id in the target page. Root-absolute links
             (/x) are errors: the site lives under /fractal-notebooks/. Links into react/
             are only checked when site/react/index.html exists (build_site.sh --with-react);
             otherwise one note reports how many were skipped.
  leaks      no .ipynb/.py/.yaml/.yml/.geojson, no superpowers|_claude|PLAN|README paths,
             no author e-mail or internal hostname in the output.
  redirects  every redirect_maps key has a stub whose destination matches the config.
  llms       llms.txt / llms-full.txt exist; entry count >= nav pages + bundle pages + apps.
  robots     robots.txt and sitemap.xml exist (sitemap <loc> count reported).
  okf        okf/concepts/index.md twin starts with okf_version "0.2";
             okf/concepts/geometry/self-affinity.md has no root-absolute ](/ link.
  icons      no literal :material-/:octicons- shortcode text in site/index.html.
  size       no file > --max-file-mb (25) and total <= --max-total-mb (100).

--emit-redirects prints `redirect_maps` TOML lines for the uncovered fixture paths using
the migration plan's mapping rules (groups A-G) and exits 0; paste them into zensical.toml.

Usage: python scripts/check_site.py [--config zensical.toml] [--site site]
           [--fixture scripts/fixtures/live-urls-2026-10-24.txt] [--emit-redirects] [--skip-links]
"""

from __future__ import annotations

import argparse
import posixpath
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from okf_common import (  # noqa: E402
    ConfigError,
    ROOT,
    is_external,
    load_config,
    nav_pages,
    page_url,
    redirect_maps,
    site_dir,
    site_root,
)
from generate_llms_txt import REACT_ROUTES  # noqa: E402

FIXTURE = ROOT / "scripts" / "fixtures" / "live-urls-2026-10-24.txt"
REFRESH_RE = re.compile(r'<meta[^>]+http-equiv="refresh"[^>]+content="[^"]*?url=([^"]+)"', re.I)
CANONICAL_RE = re.compile(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', re.I)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
ATTR_RE = re.compile(r"""<(?:a|link|img|script|source|iframe)\b[^>]*?\s(?:href|src)=["']([^"'#][^"']*|#[^"']*)["']""", re.I)
ID_RE = re.compile(r"""\s(?:id|name)=["']([^"']+)["']""")
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
LEAK_STRINGS = ("tswetnam@arizona.edu", "r01c01u30")
REACT_ROUTE_COUNT = len(REACT_ROUTES)  # the llms.txt "Interactive apps" entries
README_DIRS = {
    "notebooks/3dep/",
    "notebooks/foundations/",
    "notebooks/foundations/blender/",
    "notebooks/metabolic-scaling/review/",
}


@dataclass
class Report:
    failures: list[str] = field(default_factory=list)
    lines: list[str] = field(default_factory=list)

    def ok(self, name: str, msg: str) -> None:
        self.lines.append(f"ok   {name}: {msg}")

    def note(self, name: str, msg: str) -> None:
        self.lines.append(f"note {name}: {msg}")

    def fail(self, name: str, msg: str, details: list[str] | None = None) -> None:
        self.failures.append(name)
        self.lines.append(f"FAIL {name}: {msg}")
        for d in (details or [])[:40]:
            self.lines.append(f"       {d}")
        if details and len(details) > 40:
            self.lines.append(f"       ... {len(details) - 40} more")


# ------------------------------------------------------------------ stub detection


def classify(html_path: Path, site: Path) -> tuple[str, str | None]:
    """Return ('stub', destination) | ('page', None) | ('missing', None)."""
    if not html_path.is_file():
        return "missing", None
    head = html_path.read_text(encoding="utf-8", errors="replace")[:6000]
    m = REFRESH_RE.search(head)
    if m:
        return "stub", m.group(1).strip()
    own = html_path.parent.relative_to(site).as_posix()
    own = "" if own == "." else own + "/"
    c = CANONICAL_RE.search(head)
    if c:
        href = c.group(1).strip()
        if href.startswith(("http://", "https://")):
            # Zensical's own canonical is <site_url>/<own>; a stub's canonical points elsewhere.
            target = urlparse(href).path.rstrip("/")
            points_home = target == "" or target.endswith("/" + own.rstrip("/")) if own else target.count("/") <= 1
            if not points_home:
                return "stub", href
        else:
            target = posixpath.normpath(posixpath.join("/" + own, href)).lstrip("/")
            if target == ".":
                target = ""
            if target.rstrip("/") != own.rstrip("/"):
                return "stub", href
    return "page", None


def resolve_destination(stub_url_path: str, href: str, base_path: str) -> str:
    """Normalise a stub's destination href to a site-root-relative path (with #fragment)."""
    if href.startswith(("http://", "https://")):
        p = urlparse(href)
        path = p.path
        if base_path and path.startswith(base_path):
            path = path[len(base_path):]
        return path.lstrip("/") + (f"#{p.fragment}" if p.fragment else "") if p.netloc.endswith("github.io") else href
    frag = ""
    if "#" in href:
        href, frag = href.split("#", 1)
        frag = "#" + frag
    joined = posixpath.normpath(posixpath.join("/" + stub_url_path, href))
    if href.endswith("/") and not joined.endswith("/"):
        joined += "/"
    return joined.lstrip("/") + frag


# ------------------------------------------------------------------ redirect rules (plan groups A-G)

ROOT_LEGACY = {
    "introduction": "metabolic-scaling/introduction.md",
    "methods": "metabolic-scaling/methods.md",
    "results": "metabolic-scaling/results.md",
    "discussion": "metabolic-scaling/discussion.md",
    "conclusion": "metabolic-scaling/conclusion.md",
    "references": "metabolic-scaling/references.md",
    "glossary": "foundations/glossary.md",
    "dims": "foundations/dimensionality.md",
    "installation": "applications/installation.md",
    "dbc": "applications/dbc.md",
    "dla": "notebooks/foundations/dla.md",
    "tree_roots": "applications/tree-roots-3d.md",
    "react-apps": "applications/react-apps.md",
}
RESEARCH = "notebooks/research.md"
GPU = {"3d_dla", "dla_cuda_offgrid", "dla_slime_mold", "dla_slime_mold_cuda", "yeast_colony_simulation",
       "dla_cuda_plan", "PLAN_lichen_growth_updates", "lichen_dla_claude"}
WIP = {"ferns", "dbc", "zeta_3d", "torch_test", "ANALYSIS_AND_FIXES", "PROPOSED_FIX"}
FLAT_NOTEBOOKS = {"old_dla": "notebooks/foundations/dla.md", "dla": "notebooks/foundations/dla.md",
                  "fractals": "notebooks/foundations/fractals.md", "fractal_generators": "notebooks/foundations/fractal_generators.md",
                  "zeta_space": "notebooks/foundations/zeta_space.md"}
PY_PAGES = {
    "notebooks/3dep/modified/generate_site_notebooks", "notebooks/3dep/modified/utils/cog_utils",
    "notebooks/3dep/modified/utils/__init__", "notebooks/3dep/modified/utils/update_notebooks_cog",
    "notebooks/3dep/modified/utils/validate_cogs", "notebooks/foundations/blender/dla_advanced_features",
    "notebooks/foundations/blender/dla_batch_render", "notebooks/foundations/blender/dla_blender_setup",
    "notebooks/foundations/blender/dla_example_renders", "notebooks/foundations/blender/dla_export",
    "notebooks/foundations/blender/dla_gallery_render", "notebooks/metabolic-scaling/review/fractal_review_utils",
}


def redirect_for(url_path: str, repo_url: str = "https://github.com/tyson-swetnam/fractal-notebooks") -> tuple[str, str | None]:
    """(redirect_maps key, destination or None) for a legacy URL path such as 'dims/'."""
    path = url_path.strip("/")
    key = f"{path}/index.md" if (path + "/") in README_DIRS else f"{path}.md"
    if not path:
        return "index.md", None
    if "/" not in path:
        return key, ROOT_LEGACY.get(path)
    if path in PY_PAGES:
        return key, f"{repo_url}/blob/main/docs/{path}.py"
    if path.startswith("superpowers/specs/"):
        return key, "fractal-rag/index.md"
    if path == "notebooks/foundations":
        return key, "notebooks/index.md"
    if path == "notebooks/foundations/blender":
        return key, "applications/blender-dla.md"
    if path == "notebooks/foundations/blender/dla_visualization" or path == "notebooks/foundations/dla_point_cloud_plan":
        return key, f"{RESEARCH}#blender-point-cloud-tools"
    if path.startswith("notebooks/3dep"):
        return key, f"{RESEARCH}#3dep-canopy-height-models"
    if path.startswith("notebooks/sierra-nevada"):
        return key, f"{RESEARCH}#sierra-nevada-giant-forest"
    if path.startswith("notebooks/smithsonian"):
        return key, f"{RESEARCH}#smithsonian-barro-colorado-island"
    if path.startswith("notebooks/metabolic-scaling/review"):
        return key, f"{RESEARCH}#reviewer-companions-part-ii"
    if path.startswith("notebooks/metabolic-scaling/"):
        return key, f"{RESEARCH}#metabolic-scaling-tutorials"
    if path.startswith("notebooks/foundations/"):
        stem = path.rsplit("/", 1)[-1]
        if stem in GPU:
            return key, f"{RESEARCH}#gpu-research-notebooks"
        if stem in WIP:
            return key, f"{RESEARCH}#work-in-progress"
        return key, None
    if path.startswith("notebooks/") and path.count("/") == 1:
        stem = path.rsplit("/", 1)[-1]
        if stem in FLAT_NOTEBOOKS:
            return key, FLAT_NOTEBOOKS[stem]
        if stem in WIP:
            return key, f"{RESEARCH}#work-in-progress"
    return key, None


LEGACY_GROUPS_B_G = {
    "notebooks/old_dla.md": "notebooks/foundations/dla.md",
    "notebooks/dla.md": "notebooks/foundations/dla.md",
    "notebooks/fractals.md": "notebooks/foundations/fractals.md",
    "notebooks/fractal_generators.md": "notebooks/foundations/fractal_generators.md",
    "notebooks/zeta_space.md": "notebooks/foundations/zeta_space.md",
    "notebooks/ferns.md": f"{RESEARCH}#work-in-progress",
    "notebooks/dbc.md": f"{RESEARCH}#work-in-progress",
    "notebooks/zeta_3d.md": f"{RESEARCH}#work-in-progress",
    "notebooks/torch_test.md": f"{RESEARCH}#work-in-progress",
}


# ------------------------------------------------------------------ checks


def read_fixture(path: Path) -> list[str]:
    """Site-root-relative URL paths ('' is the home page, written as '/'); blank and # lines are skipped."""
    paths: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        paths.append(line.lstrip("/"))
    return paths


def check_coverage(rep: Report, site: Path, fixture: Path, emit: bool, repo_url: str, include_legacy: bool) -> list[str]:
    if not fixture.is_file():
        rep.fail("coverage", f"fixture {fixture} not found")
        return []
    paths = read_fixture(fixture)
    pages = stubs = 0
    missing: list[str] = []
    for p in paths:
        kind, _ = classify(site / p / "index.html", site)
        if kind == "page":
            pages += 1
        elif kind == "stub":
            stubs += 1
        else:
            missing.append(p or "/")
    total = len(paths)
    if missing:
        rep.fail("coverage", f"{total - len(missing)}/{total} live URLs resolve (pages {pages}, stubs {stubs}); missing {len(missing)}", missing)
    else:
        rep.ok("coverage", f"{total}/{total} live URLs resolve (pages {pages}, stubs {stubs})")
    if emit:
        print("# redirect_maps entries for live URLs that the build does not serve (generated by check_site.py --emit-redirects)")
        print("[project.plugins.redirects.redirect_maps]")
        for p in missing:
            key, dest = redirect_for(p if p != "/" else "", repo_url)
            if dest is None:
                print(f'# TODO no rule: "{key}" (live URL /{p})')
            else:
                print(f'"{key}" = "{dest}"')
        if include_legacy:
            print("# gh-pages-era flat notebook URLs (plan group B)")
            for k, v in LEGACY_GROUPS_B_G.items():
                print(f'"{k}" = "{v}"')
    return missing


def collect_ids(html_path: Path, cache: dict[Path, set[str]]) -> set[str]:
    if html_path not in cache:
        try:
            cache[html_path] = set(ID_RE.findall(html_path.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            cache[html_path] = set()
    return cache[html_path]


def check_links(rep: Report, site: Path, base: str) -> None:
    base_path = urlparse(base + "/").path  # e.g. /fractal-notebooks/
    broken: list[str] = []
    n_links = n_pages = n_react = 0
    react_built = (site / "react" / "index.html").is_file()  # only after build_site.sh --with-react
    cache: dict[Path, set[str]] = {}
    for html in sorted(site.rglob("*.html")):
        rel = html.relative_to(site)
        if rel.parts and rel.parts[0] == "react":
            continue
        n_pages += 1
        text = html.read_text(encoding="utf-8", errors="replace")
        page_dir = posixpath.dirname("/" + rel.as_posix())
        for raw in ATTR_RE.findall(text):
            href = unquote(raw.strip())
            if not href or href.startswith(("javascript:", "mailto:", "tel:", "data:", "//")):
                continue
            if href.startswith(("http://", "https://")):
                if not href.startswith(base + "/") and href != base:
                    continue
                href = href[len(base):] or "/"
                href = posixpath.join(base_path, href.lstrip("/")) if not href.startswith(base_path) else href
            n_links += 1
            frag = ""
            if "#" in href:
                href, frag = href.split("#", 1)
            href = href.split("?", 1)[0]
            if not href:
                target_file = html
            else:
                if href.startswith("/"):
                    if href.startswith(base_path):
                        local = href[len(base_path):]
                    else:
                        broken.append(f"{rel.as_posix()}: root-absolute link {raw} breaks under {base_path}")
                        continue
                else:
                    local = posixpath.normpath(posixpath.join(page_dir, href)).lstrip("/")
                    if local.startswith(".."):
                        broken.append(f"{rel.as_posix()}: link escapes the site: {raw}")
                        continue
                if not react_built and (local.rstrip("/") == "react" or local.startswith("react/")):
                    n_react += 1  # the SPA is merged into site/react/ only with --with-react
                    n_links -= 1
                    continue
                target = site / local if local else site
                if target.is_dir():
                    target_file = target / "index.html"
                elif target.is_file():
                    target_file = target
                elif (site / (local + ".html")).is_file():
                    target_file = site / (local + ".html")
                else:
                    broken.append(f"{rel.as_posix()}: broken link {raw}")
                    continue
                if not target_file.is_file():
                    broken.append(f"{rel.as_posix()}: broken link {raw} (directory without index.html)")
                    continue
            if frag and target_file.suffix == ".html":
                if frag.startswith("__") or frag in ("", "top"):
                    continue
                if frag.startswith("/") or target_file.relative_to(site).parts[:1] == ("react",):
                    continue  # HashRouter route (#/mandelbrot) inside the React app, not a page anchor
                if frag not in collect_ids(target_file, cache):
                    broken.append(f"{rel.as_posix()}: anchor #{frag} not found in {target_file.relative_to(site).as_posix()}")
    if broken:
        rep.fail("links", f"{len(broken)} broken link(s)/anchor(s) across {n_pages} pages ({n_links} internal links checked)", broken)
    else:
        rep.ok("links", f"{n_links} internal links and anchors across {n_pages} pages resolve")
    if n_react:
        rep.note("links", f"react/ not built: {n_react} links to the React app not checked")


def check_leaks(rep: Report, site: Path) -> None:
    problems: list[str] = []
    for p in sorted(site.rglob("*")):
        rel = p.relative_to(site)
        if rel.parts and rel.parts[0] == "react":
            continue
        if p.is_file() and p.suffix.lower() in FORBIDDEN_EXT:
            problems.append(f"{rel.as_posix()}: forbidden file type")
        if any(FORBIDDEN_PART.search(part) for part in rel.parts) and not is_redirect_stub_path(p, site):
            problems.append(f"{rel.as_posix()}: internal path published")
        if p.is_file() and p.suffix in (".html", ".md", ".txt", ".xml", ".json"):
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for s in LEAK_STRINGS:
                if s in text:
                    problems.append(f"{rel.as_posix()}: contains {s!r}")
    if problems:
        rep.fail("leaks", f"{len(problems)} leak(s)", problems)
    else:
        rep.ok("leaks", "no notebooks, scripts, data files, notes/specs, e-mail or hostnames under site/")


def check_redirects(rep: Report, site: Path, cfg: dict, base: str) -> None:
    maps = redirect_maps(cfg)
    base_path = urlparse(base + "/").path
    problems: list[str] = []
    anchor_map = {}
    rjson = site / "redirect.json"
    if rjson.is_file():
        try:
            anchor_map = json.loads(rjson.read_text(encoding="utf-8"))
        except ValueError:
            anchor_map = {}
    for key, dest in maps.items():
        if "#" in key:
            # Anchor-only redirect: Zensical serves it client-side from redirect.json
            # as {"old/page/#frag": "new/page/#frag"} (the home page key is just "#frag").
            src_md, src_frag = key.split("#", 1)
            src_page = page_url("", src_md).lstrip("/")
            json_key = f"{src_page}#{src_frag}"
            d, frag = (dest.split("#", 1) + [""])[:2]
            expected = page_url("", d).lstrip("/") + (f"#{frag}" if frag else "")
            actual = anchor_map.get(json_key)
            if actual is None:
                problems.append(f"{key}: anchor redirect {json_key!r} missing from redirect.json")
            elif actual.rstrip("/") != expected.rstrip("/"):
                problems.append(f"{key}: redirect.json points to {actual!r}, config says {expected!r}")
            continue
        stub_path = key[: -len("index.md")] if key.endswith("index.md") else key[:-3] + "/"
        stub_path = stub_path.strip("/") + ("/" if stub_path.strip("/") else "")
        html = site / stub_path / "index.html"
        kind, href = classify(html, site)
        if kind != "stub":
            problems.append(f"{key}: no redirect stub at {stub_path}index.html ({kind})")
            continue
        if dest.startswith(("http://", "https://")):
            expected = dest
            actual = href or ""
        else:
            d, frag = (dest.split("#", 1) + [""])[:2]
            expected = page_url("", d).lstrip("/") + (f"#{frag}" if frag else "")
            actual = resolve_destination(stub_path, href or "", base_path)
        if actual.rstrip("/") != expected.rstrip("/"):
            problems.append(f"{key}: stub points to {actual!r}, config says {expected!r}")
    if problems:
        rep.fail("redirects", f"{len(problems)} of {len(maps)} redirect_maps entries wrong", problems)
    else:
        rep.ok("redirects", f"{len(maps)} redirect_maps entries have matching stubs")


def expected_llms_minimum(cfg: dict, okf: Path) -> tuple[int, str]:
    nav = [t for _, _, t in nav_pages(cfg.get("nav", [])) if not is_external(t) and not t.startswith(("okf/concepts/", "okf/proofs/"))]
    nav_n = len(dict.fromkeys(nav))
    concepts = len([p for p in (okf / "concepts").rglob("*.md")]) if (okf / "concepts").is_dir() else 0
    proofs = len([p for p in (okf / "proofs").rglob("*.md")]) if (okf / "proofs").is_dir() else 0
    total = nav_n + concepts + proofs + REACT_ROUTE_COUNT
    return total, f"{nav_n} nav pages + {concepts} concept files + {proofs} proof files + {REACT_ROUTE_COUNT} apps"


def check_llms(rep: Report, site: Path, cfg: dict, okf: Path) -> None:
    llms = site / "llms.txt"
    full = site / "llms-full.txt"
    if not llms.is_file() or not full.is_file():
        rep.fail("llms", "llms.txt or llms-full.txt missing")
        return
    entries = sum(1 for line in llms.read_text(encoding="utf-8").splitlines() if line.startswith("- ["))
    minimum, how = expected_llms_minimum(cfg, okf)
    if entries < minimum:
        rep.fail("llms", f"llms.txt has {entries} entries, expected at least {minimum} ({how})")
    else:
        rep.ok("llms", f"llms.txt has {entries} entries (>= {minimum}: {how}); llms-full.txt {full.stat().st_size // 1024} KB")


def check_robots(rep: Report, site: Path) -> None:
    robots = site / "robots.txt"
    sm = site / "sitemap.xml"
    problems = []
    if not robots.is_file():
        problems.append("robots.txt missing")
    n = 0
    if not sm.is_file():
        problems.append("sitemap.xml missing")
    else:
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        n = sum(1 for _ in ElementTree.parse(sm).getroot().iter(f"{ns}loc"))
    if problems:
        rep.fail("robots", "; ".join(problems))
    else:
        rep.ok("robots", f"robots.txt present; sitemap.xml lists {n} URLs")


def check_okf(rep: Report, site: Path) -> None:
    problems = []
    idx = site / "okf" / "concepts" / "index.md"
    if not idx.is_file():
        problems.append("okf/concepts/index.md twin missing")
    elif not idx.read_text(encoding="utf-8").startswith('---\nokf_version: "0.2"'):
        problems.append('okf/concepts/index.md does not start with ---\\nokf_version: "0.2"')
    sa = site / "okf" / "concepts" / "geometry" / "self-affinity.md"
    if not sa.is_file():
        problems.append("okf/concepts/geometry/self-affinity.md twin missing")
    elif "](/" in sa.read_text(encoding="utf-8"):
        problems.append("okf/concepts/geometry/self-affinity.md still has root-absolute ](/ links")
    pidx = site / "okf" / "proofs" / "index.md"
    if not pidx.is_file():
        problems.append("okf/proofs/index.md twin missing")
    if problems:
        rep.fail("okf", "; ".join(problems))
    else:
        rep.ok("okf", "bundle twins present, v0.2 root, relative concept links")


def check_icons(rep: Report, site: Path) -> None:
    home = site / "index.html"
    if not home.is_file():
        rep.fail("icons", "site/index.html missing")
        return
    text = home.read_text(encoding="utf-8", errors="replace")
    hits = re.findall(r":(?:material|octicons)-[a-z0-9-]+:", text)
    if hits:
        rep.fail("icons", f"literal icon shortcodes on the home page: {sorted(set(hits))[:5]}")
    else:
        rep.ok("icons", "no literal :material-/:octicons- text on the home page")


def check_size(rep: Report, site: Path, max_file_mb: float, max_total_mb: float) -> None:
    total = 0
    big = []
    for p in site.rglob("*"):
        if p.is_file():
            s = p.stat().st_size
            total += s
            if s > max_file_mb * 1024 * 1024:
                big.append(f"{p.relative_to(site).as_posix()}: {s / 1024 / 1024:.1f} MB")
    problems = list(big)
    if total > max_total_mb * 1024 * 1024:
        problems.append(f"total {total / 1024 / 1024:.1f} MB > {max_total_mb} MB")
    if problems:
        rep.fail("size", f"{len(problems)} size problem(s)", problems)
    else:
        rep.ok("size", f"total {total / 1024 / 1024:.1f} MB; largest file within {max_file_mb} MB")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None)
    ap.add_argument("--site", default=None)
    ap.add_argument("--okf", default=str(ROOT / "okf"))
    ap.add_argument("--fixture", default=str(FIXTURE))
    ap.add_argument("--emit-redirects", action="store_true", help="print redirect_maps TOML for uncovered live URLs and exit")
    ap.add_argument("--include-legacy-groups", action="store_true", help="with --emit-redirects, also print the gh-pages-era group B entries")
    ap.add_argument("--skip-links", action="store_true")
    ap.add_argument("--max-file-mb", type=float, default=25)
    ap.add_argument("--max-total-mb", type=float, default=100)
    args = ap.parse_args(argv)
    try:
        cfg = load_config(ROOT, args.config)
    except ConfigError as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 2
    site = Path(args.site) if args.site else site_dir(cfg)
    if not site.is_dir():
        print(f"ERROR {site}: not found; run `zensical build` first", file=sys.stderr)
        return 2
    base = site_root(cfg)
    rep = Report()
    repo_url = str(cfg.get("repo_url") or "https://github.com/tyson-swetnam/fractal-notebooks").rstrip("/")
    check_coverage(rep, site, Path(args.fixture), args.emit_redirects, repo_url, args.include_legacy_groups)
    if args.emit_redirects:
        return 0
    if not args.skip_links:
        check_links(rep, site, base)
    check_leaks(rep, site)
    check_redirects(rep, site, cfg, base)
    check_llms(rep, site, cfg, Path(args.okf))
    check_robots(rep, site)
    check_okf(rep, site)
    check_icons(rep, site)
    check_size(rep, site, args.max_file_mb, args.max_total_mb)
    for line in rep.lines:
        print(line)
    if rep.failures:
        print(f"check_site: {len(rep.failures)} check(s) failed: {', '.join(rep.failures)}")
        return 1
    print("check_site: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
