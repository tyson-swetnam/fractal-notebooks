import textwrap

import generate_llms_txt as gl
from conftest import REPO, SITE_URL


def test_react_routes_match_app_tsx_and_navigation():
    app = (REPO / "react" / "src" / "App.tsx").read_text(encoding="utf-8")
    nav = (REPO / "react" / "src" / "components" / "layout" / "Navigation.tsx").read_text(encoding="utf-8").replace("\\'", "'")
    routes = {r for r, _, _ in gl.REACT_ROUTES}
    assert len(routes) == 16 == len(gl.REACT_ROUTES)
    import re

    app_routes = set(re.findall(r'<Route path="([^"]+)"', app))
    assert app_routes == routes, f"route drift: only in App.tsx {app_routes - routes}, only in script {routes - app_routes}"
    for route, label, _ in gl.REACT_ROUTES:
        if route == "/":
            continue
        assert f"path: '{route}', label: '{label}'" in nav, f"label drift for {route}: {label!r} not in Navigation.tsx"


def test_end_to_end_on_fixture(built_fx, capsys):
    out = built_fx.site
    b = gl.build(built_fx.cfg, built_fx.docs, built_fx.okf, out)
    txt, full = b.render()
    (out / "llms.txt").write_text(txt, encoding="utf-8")
    assert b.problems == [], b.problems
    assert txt.startswith("# Fixture Site\n\n> A fixture site")
    assert "Related OKF bundle: https://example.org/other/llms.txt" in txt
    # nav flattening with an em dash and nav order
    assert "## Home\n" in txt and "## Foundations\n" in txt
    assert "## Research — Part II: Metabolic Scaling\n" in txt
    assert "## Knowledge — OKF Proofs" not in txt  # bundle pages come from the walk, not the nav
    assert "## Knowledge — Concepts\n" in txt and "## Knowledge — Proofs\n" in txt
    assert txt.index("## Home") < txt.index("## Foundations") < txt.index("## Research — Part II") < txt.index("## Knowledge")
    assert "## For AI Agents\n" in txt
    # the walked bundle sections follow the Knowledge tab's sections and precede the next tab
    assert txt.index("## Knowledge\n") < txt.index("## Knowledge — Concepts") < txt.index("## Knowledge — Proofs") < txt.index("## For AI Agents")
    assert "- [" not in txt.split("## For AI Agents\n")[1].split("## ")[0].replace(f"- [For AI Agents]({SITE_URL}/agents.md)", "")
    assert "example.org/fx/react/) " not in txt.split("## Interactive apps")[0]  # external nav entry skipped
    # prose stays out of the H2 sections: the HashRouter note sits in the preamble
    preamble = txt.split("\n## ")[0]
    assert "single-page application (HashRouter)" in preamble and f"{SITE_URL}/react/" in preamble
    # entries link the Markdown twins and carry descriptions / status
    assert f"- [Chapter 1: History of Fractals]({SITE_URL}/foundations/history.md): A fixture page description" in txt
    assert f"- [Metabolic Scaling - Abstract]({SITE_URL}/metabolic-scaling/abstract.md): A fixture page description that is comfortably longer than fifty characters. (draft)" in txt
    assert f"- [Part II: Metabolic Scaling]({SITE_URL}/metabolic-scaling/index.md)" in txt
    # concepts: root index (fixed description, not the maintainer prose), group index (generated description), concept page
    assert f"- [Concepts]({SITE_URL}/okf/concepts/index.md): Root index of the OKF concept bundle (1 concept in 1 group)\n" in txt
    assert f"- [Proofs]({SITE_URL}/okf/proofs/index.md): Root index of the OKF proof bundle (1 proof)\n" in txt
    assert "Generated from the seed." not in txt
    assert f"- [Geometry]({SITE_URL}/okf/concepts/geometry/index.md): Index of the 1 concept page(s) in the Geometry group: Fractal." in txt
    assert f"- [Fractal]({SITE_URL}/okf/concepts/geometry/fractal.md): A complex geometric shape" in txt
    assert f"- [Proof one]({SITE_URL}/okf/proofs/p1.md): The fixture set has dimension one" in txt
    # apps, meta, optional
    apps = txt.split("## Interactive apps\n")[1].split("## ")[0]
    assert apps.count("- [") == 16 and f"- [Mandelbrot Set (app)]({SITE_URL}/react/#/mandelbrot): " in apps
    assert "single-page application" not in apps and all(line.startswith("- [") for line in apps.strip().splitlines())
    assert all(" (app)](" in line for line in apps.strip().splitlines())
    meta = txt.split("## Meta\n")[1].split("## ")[0]
    assert meta.count("- [") == 3 and f"({SITE_URL}/log.md)" in meta and f"({SITE_URL}/okf/concepts/log.md)" in meta and f"({SITE_URL}/okf/proofs/log.md)" in meta
    assert txt.rstrip().split("## ")[-1].startswith("Optional")
    assert f"{SITE_URL}/llms-full.txt" in txt and f"{SITE_URL}/sitemap.xml" in txt and "nbviewer.org/github/example/fx/tree/main/docs/notebooks/" in txt
    assert txt.count(f"]({SITE_URL}/agents.md)") == 1  # listed under its tab only, not again under Optional
    # full corpus keeps frontmatter and the URL/Source header
    assert full.startswith("# Fixture Site — full content\n")
    assert f"# Chapter 1: History of Fractals\nURL: {SITE_URL}/foundations/history/\nSource: {SITE_URL}/foundations/history.md\n" in full
    assert "\n---\ntype: Chapter\n" in full and 'okf_version: "0.2"' in full
    # every sitemap URL is covered
    assert not [p for p in b.problems if "sitemap" in p]
    n_entries = sum(1 for line in txt.splitlines() if line.startswith("- ["))
    assert n_entries == b.entries >= 7 + 4 + 2 + 16 + 3


def test_clean_description_and_describe():
    raw = ("Appendix-level proofs, primarily [Chapter 1](https://x/history/) (`docs/history.md`).\n"
           "Each  document is a `type: Fractal Proof` record with a cross-link to [`../concepts/`](../concepts/index.md).")
    assert gl.clean_description(raw) == ("Appendix-level proofs, primarily Chapter 1 (docs/history.md). "
                                         "Each document is a type: Fractal Proof record with a cross-link to ../concepts/.")
    assert gl.clean_description("![alt](img.png) shown") == "alt shown"
    long = " ".join(f"Sentence number {i} is here." for i in range(40))
    out = gl.clean_description(long)
    assert len(out) <= 300 and out.endswith(" is here.") and out.startswith("Sentence number 0 is here. Sentence number 1")
    assert len(out) > 250  # cut at the last sentence boundary within the limit, not far before it
    words = gl.clean_description("word " * 100)
    assert len(words) <= 300 and words.endswith(" ...") and " word" in words
    assert len(gl.clean_description("x" * 400)) <= 300
    assert gl.describe({"description": "  From   frontmatter.  "}, "# H\n\nBody.\n", "fb") == "From frontmatter."
    assert gl.describe({}, "# H\n\nSee [a](b.md) and `c`.\n\nSecond.\n", "fb") == "See a and c."
    assert gl.describe({}, "# H\n\n- only a list\n", "fb") == "fb"


def test_bundle_root_description_counts_pages_and_groups(built_fx):
    assert gl.bundle_root_description(built_fx.okf / "concepts", "concept") == "Root index of the OKF concept bundle (1 concept in 1 group)"
    assert gl.bundle_root_description(built_fx.okf / "proofs", "proof") == "Root index of the OKF proof bundle (1 proof)"
    # the real bundles (counts the task of the exporter and the proof authors keep in step)
    assert gl.bundle_root_description(REPO / "okf" / "concepts", "concept").startswith("Root index of the OKF concept bundle (")
    assert " concepts in " in gl.bundle_root_description(REPO / "okf" / "concepts", "concept")


def test_full_corpus_resolves_relative_links_against_the_twin(built_fx):
    page = built_fx.docs / "foundations" / "history.md"
    page.write_text(page.read_text(encoding="utf-8") + textwrap.dedent('''
        ![Julia](../assets/julia_set.png){ width="500" }
        See [the abstract](../metabolic-scaling/abstract.md#top), [here](#cantor), [ext](https://x.org/a.md),
        [mail](mailto:a@b.c), <img src="history_files/fig_1.png"> and `[code](inline.md)`.

        ```
        [fenced](fenced.md)
        ```
        '''), encoding="utf-8")
    b = gl.build(built_fx.cfg, built_fx.docs, built_fx.okf, built_fx.site)
    _, full = b.render()
    assert f'![Julia]({SITE_URL}/assets/julia_set.png){{ width="500" }}' in full
    assert f"[the abstract]({SITE_URL}/metabolic-scaling/abstract.md#top)" in full
    assert f"[link]({SITE_URL}/metabolic-scaling/abstract.md)." in full  # the fixture's own link
    assert "[here](#cantor)" in full and "[ext](https://x.org/a.md)" in full and "[mail](mailto:a@b.c)" in full
    assert f'<img src="{SITE_URL}/foundations/history_files/fig_1.png">' in full
    assert "`[code](inline.md)`" in full and "\n[fenced](fenced.md)\n" in full
    # frontmatter untouched; index pages resolve siblings in their own directory; bundle pages too
    assert f"\nresource: {SITE_URL}/foundations/history/\n" in full
    assert f"- [Chapter 1]({SITE_URL}/foundations/history.md)" in full  # foundations/index.md
    assert f"* [Fractal]({SITE_URL}/okf/concepts/geometry/fractal.md)" in full  # okf/concepts/geometry/index.md
    assert f"* [Geometry index]({SITE_URL}/okf/concepts/geometry/index.md)" in full  # a concept page's sibling link
    assert "](../" not in full and "](assets/" not in full


def test_strict_problems(built_fx):
    # a page in neither nav nor not_in_nav, a missing nav target, a bad resource, an uncovered sitemap URL
    (built_fx.docs / "orphan.md").write_text("---\ntype: Guide\ntitle: Orphan\ndescription: x\nresource: https://wrong/\n---\n# O\n", encoding="utf-8")
    cfg = dict(built_fx.cfg)
    cfg["nav"] = list(cfg["nav"]) + [{"Missing": "nope.md"}]
    sm = built_fx.site / "sitemap.xml"
    sm.write_text(sm.read_text(encoding="utf-8").replace("</urlset>", f"<url><loc>{SITE_URL}/ghost/</loc></url></urlset>"), encoding="utf-8")
    b = gl.build(cfg, built_fx.docs, built_fx.okf, built_fx.site)
    joined = "\n".join(b.problems)
    assert "nav target missing on disk: nope.md" in joined
    assert "page not in nav (added under 'Other'): orphan.md" in joined
    assert "orphan.md: resource 'https://wrong/'" in joined
    assert f"sitemap URL not covered by llms.txt: {SITE_URL}/ghost/" in joined
    txt, _ = b.render()
    assert "## Other\n" in txt


def test_main_requires_config(tmp_path, monkeypatch):
    monkeypatch.setattr(gl, "ROOT", tmp_path)
    assert gl.main(["--config", str(tmp_path / "missing.toml")]) == 2


def test_main_writes_files(built_fx, monkeypatch):
    monkeypatch.setattr(gl, "ROOT", built_fx.root)
    rc = gl.main(["--config", str(built_fx.config), "--okf", str(built_fx.okf), "--strict"])
    assert rc == 0
    assert (built_fx.site / "llms.txt").is_file() and (built_fx.site / "llms-full.txt").stat().st_size > 1000
