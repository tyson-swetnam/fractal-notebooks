#!/usr/bin/env python3
"""Generate llms.txt and llms-full.txt into the built site directory.

Adapted from tyson-swetnam/intro-gpt scripts/generate_llms_txt.py.

llms.txt       llmstxt.org outline: every nav page as "- [title](<twin .md URL>): description",
               grouped under "## <Tab>" / "## <Tab> — <Section>" headings (em dash) in nav order,
               with "## Knowledge — Concepts" and "## Knowledge — Proofs" (a directory walk of the
               two OKF bundles) placed right after the Knowledge tab's own sections; then
               "## Interactive apps" (the 16 React HashRouter routes, titles suffixed " (app)"),
               "## Meta" (the three change logs) and "## Optional". Prose notes (the HashRouter
               caveat) go in the preamble, before the first H2, so every section is a plain list.
               Body-derived descriptions are plain text (links -> text, no backticks, <= 300 chars
               cut at a sentence boundary); the two bundle roots get a fixed description.
llms-full.txt  the whole corpus in one file: per page a URL:/Source: header followed by the
               page's full Markdown source, OKF frontmatter included. Relative link/image
               targets (../assets/x.png, <stem>_files/x.png, sibling.md) are resolved against the
               page's twin URL so they work from the single file; fenced/inline code is untouched.

Site name, description, URL, nav, not_in_nav and related_llms come from zensical.toml.

--strict fails on: a nav target missing on disk, a page without a description, a page whose
frontmatter resource differs from its URL, a docs page that is neither in the nav nor
not_in_nav/excluded, and a sitemap.xml URL that no entry covers.

Usage: python scripts/generate_llms_txt.py [--config zensical.toml] [--docs docs] [--okf okf] [--out site] [--strict]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urljoin
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from okf_common import (  # noqa: E402
    ConfigError,
    FRONTMATTER_RE,
    ROOT,
    docs_dir,
    exclude_spec,
    first_paragraph,
    html_url,
    is_excluded,
    is_external,
    load_config,
    md_url,
    nav_pages,
    not_in_nav_spec,
    rewrite_link_targets,
    site_dir,
    site_root,
    split_frontmatter,
)

SEP = " — "  # em dash between tab and section
RULE = "-" * 78
KNOWLEDGE_TAB = "Knowledge"  # nav tab whose sections the bundle walk follows
DESC_LIMIT = 300  # characters, like the OKF description rule in validate_okf.py
TRAILING_SECTIONS = ("Interactive apps", "Other", "Meta", "Optional")

# Mirrors react/src/App.tsx (Route paths) and components/layout/Navigation.tsx (labels).
# scripts/tests/test_generate_llms_txt.py asserts that every route and label still exists there.
REACT_ROUTES: list[tuple[str, str, str]] = [
    ("/", "Home", "Landing page listing all interactive fractal apps."),
    ("/mandelbrot", "Mandelbrot Set", "WebGL escape-time renderer with zoom, iteration and colour controls."),
    ("/julia", "Julia Sets", "WebGL Julia set explorer for f(z) = z^2 + c with a movable parameter c."),
    ("/brownian", "Brownian Motion", "Random-walk and fractional Brownian motion traces with a Hurst-exponent control."),
    ("/conway", "Conway's Game of Life", "Cellular automaton on a WebGL grid with density and colour-scheme options."),
    ("/noise", "Noise Patterns", "White, pink and brown noise generators with spectra."),
    ("/waves", "Wave Dynamics", "Interactive wave superposition and interference patterns."),
    ("/plant-lab", "Plant Architecture Lab", "L-system plant engine with presets and parameter sliders."),
    ("/fern-frond-3d", "Fern Frond 3D", "Three-dimensional fern frond built from an L-system."),
    ("/dla", "Diffusion-Limited Aggregation", "DLA cluster growth with vector-field bias modes."),
    ("/ferns", "Barnsley Ferns", "Iterated-function-system fern with adjustable affine maps."),
    ("/trees", "Fractal Trees", "Recursive branching trees with angle and length-ratio sliders."),
    ("/pythagoras", "Pythagoras Tree", "Recursive Pythagoras tree of squares."),
    ("/tree-roots-3d", "3D Tree with Roots", "Three-dimensional tree and root system visualisation."),
    ("/zeta-space-tiling", "Zeta Space Tiling", "Plane tiling with shape areas following the Riemann zeta distribution."),
    ("/zeta-3d-visualization", "3D Zeta Visualization", "Three-dimensional Riemann zeta sphere packing."),
]

KNOWLEDGE_BUNDLES = (
    ("concepts", "Concepts", "Canonical fractal concepts generated from the RAG seed ontology."),
    ("proofs", "Proofs", "Appendix-level proofs of the quantitative claims in the Foundations chapters."),
)


def read_page(path: Path) -> tuple[dict, str, str]:
    text = path.read_text(encoding="utf-8")
    try:
        meta, body = split_frontmatter(text)
    except ValueError:
        meta, body = None, text
    return (meta or {}), body, text


def clean_description(text: str, limit: int = DESC_LIMIT) -> str:
    """One line of plain text: [text](url) -> text, backticks dropped, whitespace collapsed,
    cut at the last sentence boundary within ``limit`` characters (else at a word, with ...)."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = " ".join(text.replace("`", "").split())
    if len(text) <= limit:
        return text
    head = text[:limit]
    ends = [m.end() for m in re.finditer(r"[.!?](?=\s|$)", head)]
    if ends:
        return head[: ends[-1]]
    return head[: limit - 4].rsplit(" ", 1)[0] + " ..."


def describe(meta: dict, body: str, fallback: str) -> str:
    desc = str(meta.get("description") or "").strip()
    if desc:
        return clean_description(desc)
    para = first_paragraph(body)
    return clean_description(para) if para else fallback


def plural(n: int, noun: str) -> str:
    return f"{n} {noun}" if n == 1 else f"{n} {noun}s"


def bundle_root_description(root: Path, noun: str) -> str:
    """Fixed description for a bundle's root index.md, whose body is maintainer prose
    ("do not edit these files by hand ..."), e.g. 'Root index of the OKF concept bundle
    (32 concepts in 12 groups)' / 'Root index of the OKF proof bundle (12 proofs)'."""
    pages = [p for p in root.rglob("*.md") if p.name not in ("index.md", "log.md")
             and not any(part.startswith(".") for part in p.relative_to(root).parts)]
    groups = {p.parent for p in pages if p.parent != root}
    counts = plural(len(pages), noun) + (f" in {plural(len(groups), 'group')}" if groups else "")
    return f"Root index of the OKF {noun} bundle ({counts})"


def absolutize_links(text: str, source_url: str) -> str:
    """Resolve relative Markdown link/image (and raw src=/href=) targets in a page against
    its twin URL, the way the renderer resolves them against the source file. External,
    #anchor, mailto:, tel: and data: targets, fenced/inline code and the frontmatter are
    left alone; #fragments and trailing attr_lists ({ width="500" }) survive."""
    m = FRONTMATTER_RE.match(text) if text.startswith("---") else None
    head, body = (text[: m.end()], text[m.end():]) if m else ("", text)

    def fix(target: str) -> str:
        if not target or is_external(target):
            return target
        return urljoin(source_url, target)

    return head + rewrite_link_targets(body, fix)


def status_suffix(meta: dict) -> str:
    status = meta.get("status")
    if status == "draft":
        return " (draft)"
    if status == "deprecated":
        return " (deprecated; kept for history)"
    return ""


def list_links(body: str) -> int:
    return len(re.findall(r"^\s*[*-]\s+\[", body, re.M))


class Builder:
    def __init__(self, cfg: dict, docs: Path, okf: Path):
        self.cfg = cfg
        self.docs = docs
        self.okf = okf
        self.site = site_root(cfg)
        self.repo = str(cfg.get("repo_url") or "").rstrip("/")
        self.problems: list[str] = []
        self.sections: dict[str, list[str]] = {}
        self.preamble: list[str] = []  # prose notes emitted before the first H2
        self.full: list[str] = []
        self.emitted_urls: set[str] = set()
        self.emitted_rel: set[str] = set()
        self.entries = 0

    # -- helpers ---------------------------------------------------------------
    def add(self, section: str, line: str) -> None:
        self.sections.setdefault(section, []).append(line)
        self.entries += 1

    def add_full(self, title: str, page_url: str, source_url: str, text: str) -> None:
        text = absolutize_links(text, source_url)
        self.full += ["", RULE, f"# {title}", f"URL: {page_url}", f"Source: {source_url}", RULE, "", text.rstrip(), ""]

    # -- docs pages ------------------------------------------------------------
    def docs_entry(self, section: str, rel: str, label: str | None) -> None:
        path = self.docs / rel
        if not path.is_file():
            self.problems.append(f"nav target missing on disk: {rel}")
            return
        meta, body, text = read_page(path)
        title = str(meta.get("title") or label or Path(rel).stem.replace("-", " ").replace("_", " ").title())
        desc = str(meta.get("description") or "").strip().replace("\n", " ")
        if not desc:
            self.problems.append(f"{rel}: missing description")
        page = html_url(self.site, rel)
        source = md_url(self.site, rel)
        if meta.get("resource") and meta["resource"] != page:
            self.problems.append(f"{rel}: resource {meta['resource']!r} != {page!r}")
        self.add(section, f"- [{title}]({source}): {desc}{status_suffix(meta)}")
        self.add_full(title, page, source, text)
        self.emitted_urls.add(page)
        self.emitted_rel.add(rel)

    def walk_nav(self) -> None:
        for trail, label, target in nav_pages(self.cfg.get("nav", [])):
            if is_external(target):
                continue  # the React launcher etc.; the apps get their own section
            rel = target.replace("\\", "/")
            if rel.startswith(("okf/concepts/", "okf/proofs/")):
                self.emitted_rel.add(rel)  # listed by the bundle walk instead
                continue
            if rel in self.emitted_rel:
                continue
            section = SEP.join(trail) if trail else (label or "Pages")
            self.docs_entry(section, rel, label)

    # -- OKF bundles -----------------------------------------------------------
    def walk_bundle(self, name: str, heading: str, fallback_desc: str) -> None:
        root = self.okf / name
        section = f"{KNOWLEDGE_TAB}{SEP}{heading}"
        noun = heading.lower()[:-1] if heading.lower().endswith("s") else heading.lower()
        if not root.is_dir():
            self.problems.append(f"OKF bundle missing: {root}")
            return
        files = sorted(p for p in root.rglob("*.md") if not any(part.startswith(".") for part in p.relative_to(root).parts))
        # root index first, then each group's index.md followed by its pages; logs go to Meta
        files.sort(key=lambda p: (p.name != "index.md" or p.parent != root, p.parent.relative_to(root).as_posix(), p.name != "index.md", p.name))
        for path in files:
            rel_bundle = path.relative_to(root).as_posix()
            rel_docs = f"okf/{name}/{rel_bundle}"
            meta, body, text = read_page(path)
            page = html_url(self.site, rel_docs)
            source = md_url(self.site, rel_docs)
            h1 = re.search(r"^#\s+(.+?)\s*$", body, re.M)
            title = str(meta.get("title") or (h1.group(1) if h1 else Path(rel_bundle).stem.replace("-", " ").title()))
            if path.name == "log.md":
                self.add("Meta", f"- [{title}]({source}): dated change history of the {heading.lower()} bundle (newest first).")
                self.add_full(title, page, source, text)
            else:
                if path.name == "index.md" and path.parent == root:
                    # the root body is maintainer prose ("do not edit these files by hand"): fixed text instead
                    desc = describe(meta, "", bundle_root_description(root, noun))
                elif path.name == "index.md":
                    desc = describe(meta, body, "")
                    if not desc:  # generated group indexes have no prose: list what they index
                        names = re.findall(r"^\s*[*-]\s+\[([^\]]+)\]", body, re.M)
                        desc = f"Index of the {len(names)} concept page(s) in the {title} group: " + ", ".join(names) + "."
                else:
                    desc = describe(meta, body, fallback_desc)
                self.add(section, f"- [{title}]({source}): {desc}{status_suffix(meta)}")
                self.add_full(title, page, source, text)
            self.emitted_urls.add(page)
            self.emitted_rel.add(rel_docs)

    # -- other sections --------------------------------------------------------
    def react_section(self) -> None:
        base = f"{self.site}/react/#"
        self.preamble.append(
            "The entries under \"Interactive apps\" are one React single-page application (HashRouter): "
            f"every route shares the crawlable URL {self.site}/react/ and needs JavaScript. Read "
            f"{md_url(self.site, 'applications/react-apps.md')} for what each app does."
        )
        for route, title, desc in REACT_ROUTES:
            self.add("Interactive apps", f"- [{title} (app)]({base}{route}): {desc}")

    def meta_section(self) -> None:
        log = self.docs / "log.md"
        if log.is_file():
            meta, body, text = read_page(log)
            title = str(meta.get("title") or "Change log")
            page = html_url(self.site, "log.md")
            source = md_url(self.site, "log.md")
            line = f"- [{title}]({source}): {describe(meta, body, 'Dated history of changes to this site (newest first).')}"
            self.sections.setdefault("Meta", []).insert(0, line)
            self.entries += 1
            self.add_full(title, page, source, text)
            self.emitted_urls.add(page)
            self.emitted_rel.add("log.md")

    def optional_section(self) -> None:
        owner_repo = self.repo.split("github.com/", 1)[-1] if self.repo else ""
        lines = [
            f"- [Full corpus (llms-full.txt)]({self.site}/llms-full.txt): every page in this outline, Markdown source with OKF frontmatter, in one file.",
            f"- [Sitemap]({self.site}/sitemap.xml): crawl surface of the rendered site.",
        ]
        if self.repo:
            lines += [
                f"- [Source repository]({self.repo}): Markdown sources, notebooks, OKF bundles, React and Streamlit apps.",
                f"- [Notebooks on nbviewer](https://nbviewer.org/github/{owner_repo}/tree/main/docs/notebooks/): rendered views of every notebook, including those not published as pages.",
                f"- [Raw notebooks]({self.repo}/tree/main/docs/notebooks): the .ipynb files.",
                f"- [Streamlit app sources]({self.repo}/tree/main/apps): the Python apps, runnable with `streamlit run`.",
            ]
        self.sections["Optional"] = lines
        self.entries += len(lines)

    def other_pages(self) -> None:
        spec = exclude_spec(self.cfg)
        nin = not_in_nav_spec(self.cfg)
        for path in sorted(self.docs.rglob("*.md")):
            rel = path.relative_to(self.docs).as_posix()
            if rel in self.emitted_rel or is_excluded(spec, rel):
                continue
            if rel.startswith(("okf/concepts/", "okf/proofs/")):
                continue  # staged copies, listed from the canonical bundle
            if nin.match_file(rel):
                self.docs_entry("Other", rel, None)
                continue
            self.problems.append(f"page not in nav (added under 'Other'): {rel}")
            self.docs_entry("Other", rel, None)

    def sitemap_coverage(self, out: Path) -> None:
        sm = out / "sitemap.xml"
        if not sm.is_file():
            return
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        for loc in ElementTree.parse(sm).getroot().iter(f"{ns}loc"):
            url = (loc.text or "").strip()
            if url and url not in self.emitted_urls:
                self.problems.append(f"sitemap URL not covered by llms.txt: {url}")

    # -- output ----------------------------------------------------------------
    def render(self) -> tuple[str, str]:
        name = str(self.cfg.get("site_name", "Documentation"))
        desc = " ".join(str(self.cfg.get("site_description", "")).split())
        lines = [f"# {name}", "", f"> {desc}", ""]
        related = (self.cfg.get("extra") or {}).get("related_llms") or []
        for url in related:
            lines.append(f"Related OKF bundle: {url}")
        if related:
            lines.append("")
        lines += [
            "The site is an Open Knowledge Format (OKF v0.2) bundle: every page carries YAML frontmatter "
            "with type, description, provenance (generated, sources, verified) and lifecycle (status). "
            "Each link below is the page's verbatim Markdown source; the rendered page is the same URL with "
            ".md replaced by / (directory pages: drop the trailing index.md). The whole corpus is in "
            f"{self.site}/llms-full.txt.",
            "",
        ]
        for note in self.preamble:
            lines += [note, ""]
        for section, entries in self.sections.items():
            lines += [f"## {section}", ""] + entries + [""]
        full = [f"# {name}{SEP}full content", "", f"> {desc}", ""] + self.full
        return "\n".join(lines).rstrip() + "\n", "\n".join(full).rstrip() + "\n"


def build(cfg: dict, docs: Path, okf: Path, out: Path) -> Builder:
    b = Builder(cfg, docs, okf)
    b.walk_nav()
    for name, heading, fallback in KNOWLEDGE_BUNDLES:
        b.walk_bundle(name, heading, fallback)
    b.react_section()
    b.meta_section()
    b.other_pages()
    b.optional_section()
    # Order: nav sections, with the walked bundle sections right after the Knowledge tab's own
    # sections (so they do not land after "For AI Agents"), then Interactive apps, Other, Meta, Optional.
    bundle_keys = [f"{KNOWLEDGE_TAB}{SEP}{heading}" for _, heading, _ in KNOWLEDGE_BUNDLES if f"{KNOWLEDGE_TAB}{SEP}{heading}" in b.sections]
    order = [k for k in b.sections if k not in bundle_keys and k not in TRAILING_SECTIONS]
    knowledge = [i for i, k in enumerate(order) if k == KNOWLEDGE_TAB or k.startswith(KNOWLEDGE_TAB + SEP)]
    at = knowledge[-1] + 1 if knowledge else len(order)
    order[at:at] = bundle_keys
    order += [k for k in TRAILING_SECTIONS if k in b.sections]
    b.sections = {k: b.sections[k] for k in order}
    b.sitemap_coverage(out)
    return b


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None, help="zensical.toml (default: repo root)")
    ap.add_argument("--docs", default=None, help="docs directory (default: docs_dir from the config)")
    ap.add_argument("--okf", default=str(ROOT / "okf"), help="canonical OKF bundles (default: okf/)")
    ap.add_argument("--out", default=None, help="output directory (default: site_dir from the config)")
    ap.add_argument("--strict", action="store_true", help="fail on any problem listed in the module docstring")
    args = ap.parse_args(argv)
    try:
        cfg = load_config(ROOT, args.config)
    except ConfigError as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 2
    docs = Path(args.docs) if args.docs else docs_dir(cfg)
    out = Path(args.out) if args.out else site_dir(cfg)
    b = build(cfg, docs, Path(args.okf), out)
    txt, full = b.render()
    out.mkdir(parents=True, exist_ok=True)
    (out / "llms.txt").write_text(txt, encoding="utf-8")
    (out / "llms-full.txt").write_text(full, encoding="utf-8")
    print(f"Wrote {out / 'llms.txt'} ({b.entries} entries, {len(b.sections)} sections) and {out / 'llms-full.txt'} ({(out / 'llms-full.txt').stat().st_size // 1024} KB)")
    for p in b.problems:
        print(f"WARNING: {p}", file=sys.stderr)
    if b.problems and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
