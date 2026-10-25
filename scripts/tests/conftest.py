"""Shared fixtures: a tiny docs tree + zensical.toml + OKF bundles under tmp_path."""

from __future__ import annotations

import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
REPO = SCRIPTS.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SITE_URL = "https://example.org/fx"
REPO_URL = "https://github.com/example/fx"

ZENSICAL_TOML = f"""
[project]
site_name = "Fixture Site"
site_url = "{SITE_URL}"
site_description = "A fixture site for the scripts tests, with OKF knowledge bundles."
repo_url = "{REPO_URL}"
repo_name = "example/fx"
edit_uri = "edit/main/docs/"
docs_dir = "docs"
site_dir = "site"
use_directory_urls = true
strict = true
exclude_docs = \"\"\"
*.ipynb
/notes/
README.md
\"\"\"
not_in_nav = \"\"\"
/log.md
/okf/concepts/*/
/okf/*/log.md
\"\"\"
nav = [
  {{ "Home" = "index.md" }},
  {{ "Foundations" = [ {{ "Contents" = "foundations/index.md" }}, {{ "Chapter 1: History" = "foundations/history.md" }} ] }},
  {{ "Research" = [ {{ "Part II: Metabolic Scaling" = [ {{ "Contents" = "metabolic-scaling/index.md" }}, {{ "Abstract" = "metabolic-scaling/abstract.md" }} ] }} ] }},
  {{ "Knowledge" = [ {{ "Contents" = "okf/index.md" }}, {{ "OKF Concepts" = "okf/concepts/index.md" }}, {{ "OKF Proofs" = [ {{ "Contents" = "okf/proofs/index.md" }}, "okf/proofs/p1.md" ] }} ] }},
  {{ "For AI Agents" = "agents.md" }},
  {{ "Launch the apps" = "https://example.org/fx/react/" }},
]
[project.extra]
related_llms = ["https://example.org/other/llms.txt"]
[project.plugins.redirects.redirect_maps]
"old.md" = "foundations/history.md"
"gone/index.md" = "metabolic-scaling/index.md"
"ext.md" = "https://example.com/elsewhere/"
"""


def fm(type_: str, title: str, description: str, resource: str, tags: list[str] | None = None, *,
       okf_version: bool = False, generated_by: str = "human:tester", at: str = "2026-01-01T00:00:00Z",
       status: str = "stable", extra: str = "", log: bool = False) -> str:
    import json

    lines = ["---"]
    if okf_version:
        lines.append('okf_version: "0.2"')
    lines += [f"type: {type_}", f"title: {json.dumps(title)}", f"description: {json.dumps(description)}", f"resource: {resource}"]
    if tags:
        lines.append("tags: [" + ", ".join(tags) + "]")
    if extra:
        lines.append(extra.rstrip("\n"))
    if not log:
        lines += ["generated:", f"  by: {generated_by}", f'  at: "{at}"', f"status: {status}"]
    lines.append("---")
    return "\n".join(lines) + "\n\n"


DESC = "A fixture page description that is comfortably longer than fifty characters."


@dataclass
class FixtureSite:
    root: Path
    docs: Path
    okf: Path
    site: Path
    config: Path
    cfg: dict


def build_fixture(root: Path) -> FixtureSite:
    docs = root / "docs"
    okf = root / "okf"
    site = root / "site"
    for d in (docs / "foundations", docs / "metabolic-scaling", docs / "okf", docs / "notes",
              okf / "concepts" / "geometry", okf / "proofs"):
        d.mkdir(parents=True, exist_ok=True)
    (root / "zensical.toml").write_text(ZENSICAL_TOML, encoding="utf-8")
    u = SITE_URL + "/"
    (docs / "index.md").write_text(fm("Index", "Fixture Home", DESC, u, ["knowledge", "foundations"], okf_version=True)
                                   + "# Home\n\n- [Foundations](foundations/index.md)\n- [Part II](metabolic-scaling/index.md)\n- [Knowledge](okf/index.md)\n- [Agents](agents.md)\n", encoding="utf-8")
    (docs / "foundations" / "index.md").write_text(fm("Index", "Foundations", DESC, u + "foundations/", ["foundations", "part-i"])
                                                   + "# Foundations\n\n- [Chapter 1](history.md)\n", encoding="utf-8")
    (docs / "foundations" / "history.md").write_text(fm("Chapter", "Chapter 1: History of Fractals", DESC, u + "foundations/history/", ["foundations", "part-i", "classics"],
                                                        extra="sources:\n  - id: mandelbrot1982\n    resource: https://example.org/book\n    title: The Fractal Geometry of Nature")
                                                     + "# Chapter 1\n\n## Cantor\n\nText with a [link](../metabolic-scaling/abstract.md).\n", encoding="utf-8")
    (docs / "metabolic-scaling" / "index.md").write_text(fm("Index", "Part II: Metabolic Scaling", DESC, u + "metabolic-scaling/", ["research", "part-ii"])
                                                         + "# Part II\n\n- [Abstract](abstract.md)\n", encoding="utf-8")
    (docs / "metabolic-scaling" / "abstract.md").write_text(fm("Paper Section", "Metabolic Scaling - Abstract", DESC, u + "metabolic-scaling/abstract/", ["paper", "part-ii", "metabolic-scaling"], status="draft",
                                                               extra="paper:\n  title: Fractal Patterns in Nature\n  stage: draft\nauthors:\n  - name: A. Author\n    orcid: https://orcid.org/0000-0002-6639-7181")
                                                            + "# Abstract\n\nBody.\n", encoding="utf-8")
    (docs / "okf" / "index.md").write_text(fm("Index", "Knowledge bundles", DESC, u + "okf/", ["knowledge", "okf"])
                                           + "# Knowledge bundles\n\n- [Concepts](concepts/index.md)\n- [Proofs](proofs/index.md)\n", encoding="utf-8")
    (docs / "agents.md").write_text(fm("Guide", "For AI Agents", DESC, u + "agents/", ["agents", "llms-txt"]) + "# For AI Agents\n\nText.\n", encoding="utf-8")
    (docs / "log.md").write_text(fm("Log", "Change log", DESC, u + "log/", log=True) + "# Log\n\n## 2026-02-01\n\n- **Update**: second.\n\n## 2026-01-01\n\n- **Creation**: first.\n", encoding="utf-8")
    (docs / "notes" / "PLAN.md").write_text("# internal plan\n", encoding="utf-8")
    (docs / "README.md").write_text("# readme\n", encoding="utf-8")
    (docs / "x.ipynb").write_text("{}", encoding="utf-8")

    # Exchange bundles (spec-pure reserved files)
    (okf / "concepts" / "index.md").write_text('---\nokf_version: "0.2"\n---\n\n# Concepts\n\nGenerated from the seed.\n\n* [Geometry](geometry/index.md) - 1 concept(s)\n', encoding="utf-8")
    (okf / "concepts" / "geometry" / "index.md").write_text("# Geometry\n\n* [Fractal](fractal.md) - A shape.\n", encoding="utf-8")
    (okf / "concepts" / "geometry" / "fractal.md").write_text(
        fm("Fractal Concept", "Fractal", "A complex geometric shape exhibiting self-similarity at multiple scales.", u + "okf/concepts/geometry/fractal/", ["geometry", "foundations"],
           generated_by="process:fractal-rag-okf-export", extra="aliases:\n- fractals\nhausdorff_dim_range: [0, 3]")
        + "# Definition\n\nA shape.\n\n# Related concepts\n\n* [Geometry index](index.md)\n", encoding="utf-8")
    (okf / "concepts" / "log.md").write_text("# Concept Bundle Update Log\n\n## 2026-01-01\n* **Initialization**: Generated.\n", encoding="utf-8")
    (okf / "proofs" / "index.md").write_text('---\nokf_version: "0.2"\n---\n\n# Proofs\n\n* [Proof one](p1.md) - D = 1.\n', encoding="utf-8")
    (okf / "proofs" / "p1.md").write_text(
        fm("Fractal Proof", "Proof one", "The fixture set has dimension one by direct computation of the Moran equation.", u + "okf/proofs/p1/", ["classics", "dimension-theory"],
           extra="result: D = 1\nconcept: ../concepts/geometry/fractal.md\nhistorical_source: Someone (1900)\nverification_status: verified")
        + "# Statement\n\n$D = 1$.\n", encoding="utf-8")
    (okf / "proofs" / "log.md").write_text("# Proof Bundle Change Log\n\n## 2026-01-01\n\n* **Creation**: Initialized.\n", encoding="utf-8")

    from okf_common import load_config  # noqa: E402

    cfg = load_config(root)
    return FixtureSite(root=root, docs=docs, okf=okf, site=site, config=root / "zensical.toml", cfg=cfg)


def render_fake_site(fx: FixtureSite, with_stubs: bool = True) -> None:
    """Write a minimal 'built' site (index.html per page, sitemap, stubs) without Zensical."""
    pages = ["", "foundations/", "foundations/history/", "metabolic-scaling/", "metabolic-scaling/abstract/",
             "okf/", "okf/concepts/", "okf/concepts/geometry/", "okf/concepts/geometry/fractal/", "okf/proofs/",
             "okf/proofs/p1/", "agents/", "log/", "okf/concepts/log/", "okf/proofs/log/"]
    locs = []
    for p in pages:
        d = fx.site / p
        d.mkdir(parents=True, exist_ok=True)
        rel_md = "index.md" if p == "" else (p + "index.md" if (fx.docs / p / "index.md").exists() or (fx.okf / p[len("okf/"):] / "index.md").exists() else p.rstrip("/") + ".md")
        if p in ("okf/concepts/geometry/fractal/", "okf/proofs/p1/", "okf/concepts/log/", "okf/proofs/log/", "okf/concepts/geometry/", "okf/concepts/", "okf/proofs/"):
            rel_md = p.rstrip("/") + ".md" if not p.endswith(("concepts/", "proofs/", "geometry/")) else p + "index.md"
        canonical = f"{SITE_URL}/{p}"
        up = "../" * p.count("/")
        (d / "index.html").write_text(textwrap.dedent(f"""\
            <!doctype html><html><head><title>{p or 'home'}</title>
            <link rel="canonical" href="{canonical}">
            <link rel="alternate" type="text/markdown" href="{SITE_URL}/{rel_md}" title="Markdown source">
            </head><body><h1 id="top-heading">{p or 'home'}</h1><a href="{up}foundations/history/#cantor">x</a>
            <a href="{SITE_URL}/agents/">agents</a></body></html>
            """), encoding="utf-8")
        locs.append(f"<url><loc>{canonical}</loc></url>")
        # the Markdown twin publish_sources.py would copy (so alternate links resolve)
        src = (fx.okf / rel_md[len("okf/"):]) if rel_md.startswith(("okf/concepts/", "okf/proofs/")) else fx.docs / rel_md
        if src.is_file():
            twin = fx.site / rel_md
            twin.parent.mkdir(parents=True, exist_ok=True)
            twin.write_bytes(src.read_bytes())
    # the real heading id on the history page
    (fx.site / "foundations" / "history" / "index.html").write_text(
        f'<!doctype html><html><head><title>h</title><link rel="canonical" href="{SITE_URL}/foundations/history/">'
        f'<link rel="alternate" type="text/markdown" href="{SITE_URL}/foundations/history.md"></head>'
        '<body><h1 id="chapter-1">Chapter 1</h1><h2 id="cantor">Cantor</h2></body></html>', encoding="utf-8")
    (fx.site / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(locs) + "\n</urlset>\n", encoding="utf-8")
    (fx.site / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    if with_stubs:
        for key, dest in {"old": "../foundations/history/", "gone": "../metabolic-scaling/", "ext": "https://example.com/elsewhere/"}.items():
            d = fx.site / key
            d.mkdir(parents=True, exist_ok=True)
            (d / "index.html").write_text(
                f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>Redirecting...</title>\n'
                f'<link rel="canonical" href="{dest}">\n<meta http-equiv="refresh" content="0; url={dest}">\n</head>\n'
                f'<body>You\'re being redirected to a <a href="{dest}">new destination</a>.</body></html>\n', encoding="utf-8")


@pytest.fixture
def fx(tmp_path: Path) -> FixtureSite:
    return build_fixture(tmp_path)


@pytest.fixture
def built_fx(tmp_path: Path) -> FixtureSite:
    f = build_fixture(tmp_path)
    render_fake_site(f)
    return f
