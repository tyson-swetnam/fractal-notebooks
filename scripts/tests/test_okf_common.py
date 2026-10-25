from pathlib import Path

import pytest

import okf_common as oc


BASE = "https://example.org/fx"


def test_url_math_index_cases():
    assert oc.html_url(BASE, "index.md") == BASE + "/"
    assert oc.html_url(BASE + "/", "index.md") == BASE + "/"
    assert oc.html_url(BASE, "foundations/index.md") == BASE + "/foundations/"
    assert oc.html_url(BASE, "foundations/history.md") == BASE + "/foundations/history/"
    assert oc.html_url(BASE, "okf/concepts/geometry/fractal.md") == BASE + "/okf/concepts/geometry/fractal/"
    assert oc.md_url(BASE, "index.md") == BASE + "/index.md"
    assert oc.md_url(BASE, "foundations/history.md") == BASE + "/foundations/history.md"
    assert oc.page_url(BASE + "/", "a/b.md") == BASE + "/a/b/"
    assert oc.page_url(BASE + "/", "assets/x.png") == BASE + "/assets/x.png"


def test_url_to_source_candidates():
    assert oc.url_to_source_candidates("") == ["index.md"]
    assert oc.url_to_source_candidates("/") == ["index.md"]
    assert oc.url_to_source_candidates("a/b/") == ["a/b.md", "a/b/index.md"]
    assert oc.url_to_source_candidates("okf/concepts/") == ["okf/concepts.md", "okf/concepts/index.md"]


def test_exclude_and_not_in_nav_specs(fx):
    spec = oc.exclude_spec(fx.cfg)
    assert oc.is_excluded(spec, "x.ipynb")
    assert oc.is_excluded(spec, "notebooks/3dep/deep/x.ipynb")
    assert oc.is_excluded(spec, "notes/PLAN.md")
    assert oc.is_excluded(spec, "README.md")
    assert oc.is_excluded(spec, "notebooks/foundations/README.md")
    assert oc.is_excluded(spec, ".claude/agents/x.md")  # dot-dirs are always excluded
    assert not oc.is_excluded(spec, "foundations/history.md")
    nin = oc.not_in_nav_spec(fx.cfg)
    assert nin.match_file("log.md")
    assert nin.match_file("okf/concepts/geometry/index.md")
    assert nin.match_file("okf/concepts/geometry/fractal.md")
    assert nin.match_file("okf/proofs/log.md")
    assert not nin.match_file("okf/concepts/index.md")
    assert not nin.match_file("foundations/history.md")


def test_load_config_missing_is_clear(tmp_path: Path):
    with pytest.raises(oc.ConfigError) as e:
        oc.load_config(tmp_path)
    assert "zensical.toml not found" in str(e.value)
    with pytest.raises(oc.ConfigError):
        oc.load_config(tmp_path, tmp_path / "nope.toml")


def test_load_config_reads_project_table(fx):
    assert fx.cfg["site_url"] == BASE
    assert oc.site_root(fx.cfg) == BASE
    assert oc.site_url(fx.cfg) == BASE + "/"
    assert oc.docs_dir(fx.cfg) == fx.docs.resolve()
    assert oc.site_dir(fx.cfg) == fx.site.resolve()
    assert oc.redirect_maps(fx.cfg)["old.md"] == "foundations/history.md"


def test_nav_pages_flattening(fx):
    items = list(oc.nav_pages(fx.cfg["nav"]))
    assert items[0] == ((), "Home", "index.md")
    assert ((("Foundations",), "Contents", "foundations/index.md")) in items
    assert ((("Research", "Part II: Metabolic Scaling"), "Abstract", "metabolic-scaling/abstract.md")) in items
    assert ((("Knowledge", "OKF Proofs"), None, "okf/proofs/p1.md")) in items
    assert ((), "Launch the apps", "https://example.org/fx/react/") in items
    targets = oc.nav_targets(fx.cfg)
    assert "https://example.org/fx/react/" not in targets
    assert targets[0] == "index.md" and "okf/proofs/p1.md" in targets


def test_split_frontmatter_and_first_paragraph():
    meta, body = oc.split_frontmatter("---\ntype: Guide\ntitle: X\n---\n\n# H\n\n- a list\n\nFirst prose paragraph\nwraps here.\n\nSecond.\n")
    assert meta == {"type": "Guide", "title": "X"}
    assert oc.first_paragraph(body) == "First prose paragraph wraps here."
    assert oc.split_frontmatter("# no fm\n") == (None, "# no fm\n")
    with pytest.raises(ValueError):
        oc.split_frontmatter("---\n: bad: [\n---\n")


def test_slugify_matches_python_markdown():
    assert oc.slugify("1.6 Modern Developments: Complex Dimensions and Spectral Geometry") == "16-modern-developments-complex-dimensions-and-spectral-geometry"
    assert oc.slugify("3DEP canopy height models") == "3dep-canopy-height-models"
    assert oc.slugify("Smithsonian: Barro Colorado Island") == "smithsonian-barro-colorado-island"
    assert oc.slugify("Reviewer companions (Part II)") == "reviewer-companions-part-ii"


def test_absolutize_and_rewrite():
    base = BASE + "/"
    assert oc.absolutize("../metabolic-scaling/abstract.md#x", "foundations/history.md", base) == BASE + "/metabolic-scaling/abstract/#x"
    assert oc.absolutize("history.md", "foundations/index.md", base) == BASE + "/foundations/history/"
    assert oc.absolutize("https://x.org/", "a.md", base) == "https://x.org/"
    body = "See [a](b.md) and `[c](d.md)`\n```\n[e](f.md)\n```\n"
    out = oc.rewrite_link_targets(body, lambda t: "X/" + t)
    assert "[a](X/b.md)" in out and "`[c](d.md)`" in out and "[e](f.md)" in out
