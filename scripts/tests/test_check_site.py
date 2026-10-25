from pathlib import Path

import check_site as cs
from conftest import SITE_URL


def write(p: Path, text: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


STUB = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>Redirecting...</title>\n'
        '<link rel="canonical" href="{dest}">\n<script>var anchor=window.location.hash.substr(1);location.href="{dest}"+(anchor?"#"+anchor:"")</script>\n'
        '<meta http-equiv="refresh" content="0; url={dest}">\n</head>\n<body>You\'re being redirected to a <a href="{dest}">new destination</a>.</body>\n</html>\n')


def test_classify_stub_detection(tmp_path):
    site = tmp_path / "site"
    # Zensical stub: meta refresh + relative canonical
    write(site / "old" / "index.html", STUB.format(dest="../a/"))
    assert cs.classify(site / "old" / "index.html", site) == ("stub", "../a/")
    # canonical-only stub pointing elsewhere (relative)
    write(site / "old2" / "index.html", '<html><head><link rel="canonical" href="../sub/b/#frag"></head><body></body></html>')
    assert cs.classify(site / "old2" / "index.html", site) == ("stub", "../sub/b/#frag")
    # canonical-only stub pointing to an external URL
    write(site / "old3" / "index.html", '<html><head><link rel="canonical" href="https://example.com/elsewhere/"></head></html>')
    assert cs.classify(site / "old3" / "index.html", site)[0] == "stub"
    # a real page carries its own absolute canonical
    write(site / "a" / "index.html", f'<html><head><link rel="canonical" href="{SITE_URL}/a/"></head><body><h1>A</h1></body></html>')
    assert cs.classify(site / "a" / "index.html", site) == ("page", None)
    write(site / "index.html", f'<html><head><link rel="canonical" href="{SITE_URL}/"></head><body></body></html>')
    assert cs.classify(site / "index.html", site) == ("page", None)
    write(site / "sub" / "b" / "index.html", f'<html><head><link rel="canonical" href="{SITE_URL}/sub/b/"></head></html>')
    assert cs.classify(site / "sub" / "b" / "index.html", site) == ("page", None)
    write(site / "plain" / "index.html", "<html><head><title>no canonical</title></head></html>")
    assert cs.classify(site / "plain" / "index.html", site) == ("page", None)
    assert cs.classify(site / "missing" / "index.html", site) == ("missing", None)


def test_redirect_rules_follow_the_plan():
    r = cs.redirect_for
    assert r("dims/") == ("dims.md", "foundations/dimensionality.md")
    assert r("introduction/") == ("introduction.md", "metabolic-scaling/introduction.md")
    assert r("react-apps/") == ("react-apps.md", "applications/react-apps.md")
    assert r("tree_roots/") == ("tree_roots.md", "applications/tree-roots-3d.md")
    assert r("applications/") == ("applications.md", None)  # served by applications/index.md, never redirected
    assert r("notebooks/3dep/") == ("notebooks/3dep/index.md", "notebooks/research.md#3dep-canopy-height-models")
    assert r("notebooks/3dep/modified/sites/harvard_forest/chm_harvard_forest/")[1] == "notebooks/research.md#3dep-canopy-height-models"
    assert r("notebooks/3dep/original/01_3DEP_Generate_DEM_User_AOI/")[1] == "notebooks/research.md#3dep-canopy-height-models"
    assert r("notebooks/3dep/modified/utils/cog_utils/") == ("notebooks/3dep/modified/utils/cog_utils.md", "https://github.com/tyson-swetnam/fractal-notebooks/blob/main/docs/notebooks/3dep/modified/utils/cog_utils.py")
    assert r("notebooks/foundations/blender/dla_export/")[1].endswith("/blob/main/docs/notebooks/foundations/blender/dla_export.py")
    assert r("notebooks/metabolic-scaling/review/fractal_review_utils/")[1].endswith("fractal_review_utils.py")
    assert r("notebooks/foundations/") == ("notebooks/foundations/index.md", "notebooks/index.md")
    assert r("notebooks/foundations/blender/") == ("notebooks/foundations/blender/index.md", "applications/blender-dla.md")
    assert r("notebooks/foundations/blender/dla_visualization/")[1] == "notebooks/research.md#blender-point-cloud-tools"
    assert r("notebooks/foundations/dla_point_cloud_plan/")[1] == "notebooks/research.md#blender-point-cloud-tools"
    assert r("notebooks/foundations/3d_dla/")[1] == "notebooks/research.md#gpu-research-notebooks"
    assert r("notebooks/foundations/lichen_dla_claude/")[1] == "notebooks/research.md#gpu-research-notebooks"
    assert r("notebooks/foundations/ferns/")[1] == "notebooks/research.md#work-in-progress"
    assert r("notebooks/foundations/ANALYSIS_AND_FIXES/")[1] == "notebooks/research.md#work-in-progress"
    assert r("notebooks/foundations/1_history/") == ("notebooks/foundations/1_history.md", None)  # a real page, not a redirect
    assert r("notebooks/metabolic-scaling/review/") == ("notebooks/metabolic-scaling/review/index.md", "notebooks/research.md#reviewer-companions-part-ii")
    assert r("notebooks/metabolic-scaling/review/abstract_companion/")[1] == "notebooks/research.md#reviewer-companions-part-ii"
    assert r("notebooks/metabolic-scaling/2_mst_equations/")[1] == "notebooks/research.md#metabolic-scaling-tutorials"
    assert r("notebooks/metabolic-scaling/mst_claude/")[1] == "notebooks/research.md#metabolic-scaling-tutorials"
    assert r("notebooks/sierra-nevada/PLAN/")[1] == "notebooks/research.md#sierra-nevada-giant-forest"
    assert r("notebooks/smithsonian/1_chm_exploration/")[1] == "notebooks/research.md#smithsonian-barro-colorado-island"
    assert r("superpowers/specs/2026-07-13-zensical-migration/") == ("superpowers/specs/2026-07-13-zensical-migration.md", "fractal-rag/index.md")
    assert r("notebooks/old_dla/")[1] == "notebooks/foundations/dla.md"
    assert r("notebooks/torch_test/")[1] == "notebooks/research.md#work-in-progress"


def test_live_fixture_has_a_rule_for_every_legacy_url():
    """Every live URL is either a page the new site serves or has a redirect rule."""
    served_prefixes = ("applications/", "biological-geometry/", "foundations/", "fractal-rag/", "hypotheses/",
                       "metabolic-scaling/", "spectral-geometry/", "notebooks/foundations/1_history/",
                       "notebooks/foundations/2_mathematics/", "notebooks/foundations/3_dimensionality/",
                       "notebooks/foundations/4_zeta_space/", "notebooks/foundations/dla/", "notebooks/foundations/fractals/",
                       "notebooks/foundations/fractal_generators/", "notebooks/foundations/zeta_space/",
                       "notebooks/metabolic-scaling/methods/", "notebooks/metabolic-scaling/results/")
    missing_rules = []
    for p in cs.read_fixture(cs.FIXTURE):
        if p == "" or p.startswith(served_prefixes):
            continue
        key, dest = cs.redirect_for(p)
        if dest is None:
            missing_rules.append(p)
    assert missing_rules == [], missing_rules


def test_read_fixture_home_blank_and_comment_lines(tmp_path):
    fixture = tmp_path / "live.txt"
    fixture.write_text("# captured sitemap\n/\n\nfoundations/history/\n  /old/  \n\n", encoding="utf-8")
    assert cs.read_fixture(fixture) == ["", "foundations/history/", "old/"]
    assert cs.read_fixture(cs.FIXTURE)[0] == ""  # the committed fixture starts with the home page
    assert "" not in cs.read_fixture(cs.FIXTURE)[1:]


def test_coverage_links_leaks_redirects_on_fake_site(built_fx, tmp_path):
    site = built_fx.site
    fixture = tmp_path / "live.txt"
    fixture.write_text("/\n# a comment\n\nfoundations/history/\nold/\ngone/\nnever-existed/\n", encoding="utf-8")
    rep = cs.Report()
    missing = cs.check_coverage(rep, site, fixture, emit=False, repo_url="https://github.com/example/fx", include_legacy=False)
    assert missing == ["never-existed/"]
    assert rep.lines[0].startswith("FAIL coverage: 4/5 live URLs resolve (pages 2, stubs 2)")

    rep = cs.Report()
    cs.check_links(rep, site, SITE_URL)
    assert rep.failures == [], rep.lines
    # a broken link, a bad anchor and a root-absolute link are all reported
    write(site / "bad" / "index.html", '<html><body><a href="../nowhere/">x</a><a href="../foundations/history/#missing">y</a><a href="/root-abs/">z</a><img src="../img.png"></body></html>')
    rep = cs.Report()
    cs.check_links(rep, site, SITE_URL)
    joined = "\n".join(rep.lines)
    assert "FAIL links" in joined and "broken link ../nowhere/" in joined and "anchor #missing not found" in joined
    assert "root-absolute link /root-abs/" in joined and "broken link ../img.png" in joined
    (site / "bad" / "index.html").unlink()

    rep = cs.Report()
    cs.check_leaks(rep, site)
    assert rep.failures == []
    write(site / "notebooks" / "x.ipynb", "{}")
    write(site / "superpowers" / "specs" / "index.html", "<html>r01c01u30-gpu07</html>")
    write(site / "react" / "x.py", "ignored")  # react/ is exempt
    rep = cs.Report()
    cs.check_leaks(rep, site)
    joined = "\n".join(rep.lines)
    assert "notebooks/x.ipynb: forbidden file type" in joined and "superpowers/specs/index.html: internal path published" in joined and "contains 'r01c01u30'" in joined
    assert "react/x.py" not in joined

    rep = cs.Report()
    cs.check_redirects(rep, site, built_fx.cfg, SITE_URL)
    assert rep.failures == [], rep.lines
    write(site / "old" / "index.html", STUB.format(dest="../agents/"))
    rep = cs.Report()
    cs.check_redirects(rep, site, built_fx.cfg, SITE_URL)
    assert "old.md: stub points to 'agents/', config says 'foundations/history/'" in "\n".join(rep.lines)


def test_links_into_react_are_skipped_until_the_spa_is_built(built_fx):
    site = built_fx.site
    write(site / "applications" / "index.html",
          f'<html><body><a href="{SITE_URL}/react/">launch</a><a href="{SITE_URL}/react/#/mandelbrot">m</a>'
          '<a href="../react">r</a><script src="../react/assets/x.js"></script></body></html>')
    rep = cs.Report()
    cs.check_links(rep, site, SITE_URL)
    assert rep.failures == [], rep.lines
    assert "note links: react/ not built: 4 links to the React app not checked" in rep.lines
    assert sum(1 for line in rep.lines if line.startswith("note ")) == 1
    # once site/react/index.html exists the same links are checked for real
    write(site / "react" / "index.html", "<html></html>")
    rep = cs.Report()
    cs.check_links(rep, site, SITE_URL)
    joined = "\n".join(rep.lines)
    assert "react/ not built" not in joined
    assert rep.failures == ["links"] and "broken link ../react/assets/x.js" in joined
    assert "react/#/mandelbrot" not in joined  # HashRouter route, resolves to react/index.html


def test_react_route_count_follows_generate_llms_txt():
    import generate_llms_txt as gl

    assert cs.REACT_ROUTE_COUNT == len(gl.REACT_ROUTES) == 16


def test_other_checks_and_cli(built_fx, monkeypatch, capsys):
    site = built_fx.site
    (site / "okf" / "concepts").mkdir(parents=True, exist_ok=True)
    (site / "okf" / "concepts" / "index.md").write_text('---\nokf_version: "0.2"\n---\n', encoding="utf-8")
    (site / "okf" / "concepts" / "geometry").mkdir(exist_ok=True)
    (site / "okf" / "concepts" / "geometry" / "self-affinity.md").write_text("# x\n\n[y](fractal.md)\n", encoding="utf-8")
    (site / "okf" / "proofs").mkdir(exist_ok=True)
    (site / "okf" / "proofs" / "index.md").write_text('---\nokf_version: "0.2"\n---\n', encoding="utf-8")
    (site / "llms.txt").write_text("\n".join("- [x](y)" for _ in range(40)) + "\n", encoding="utf-8")
    (site / "llms-full.txt").write_text("full\n", encoding="utf-8")
    rep = cs.Report()
    cs.check_llms(rep, site, built_fx.cfg, built_fx.okf)
    cs.check_robots(rep, site)
    cs.check_okf(rep, site)
    cs.check_icons(rep, site)
    cs.check_size(rep, site, 25, 100)
    assert rep.failures == [], rep.lines
    assert "sitemap.xml lists 15 URLs" in "\n".join(rep.lines)
    (site / "llms.txt").write_text("- [x](y)\n", encoding="utf-8")
    (site / "index.html").write_text("<html>:material-robot:</html>", encoding="utf-8")
    (site / "okf" / "concepts" / "geometry" / "self-affinity.md").write_text("[y](/geometry/fractal.md)\n", encoding="utf-8")
    rep = cs.Report()
    cs.check_llms(rep, site, built_fx.cfg, built_fx.okf)
    cs.check_okf(rep, site)
    cs.check_icons(rep, site)
    cs.check_size(rep, site, 0.00001, 100)
    assert rep.failures == ["llms", "okf", "icons", "size"]

    monkeypatch.setattr(cs, "ROOT", built_fx.root)
    rc = cs.main(["--config", str(built_fx.config), "--site", str(site), "--okf", str(built_fx.okf), "--fixture", str(built_fx.root / "nofixture.txt")])
    out = capsys.readouterr().out
    assert rc == 1 and "FAIL coverage" in out and "check_site:" in out
    assert cs.main(["--config", str(built_fx.root / "missing.toml")]) == 2


def test_emit_redirects(built_fx, tmp_path, capsys):
    fixture = tmp_path / "live.txt"
    fixture.write_text("dims/\nnotebooks/3dep/\nunknown-thing/\nfoundations/history/\n", encoding="utf-8")
    rep = cs.Report()
    cs.check_coverage(rep, built_fx.site, fixture, emit=True, repo_url="https://github.com/example/fx", include_legacy=True)
    out = capsys.readouterr().out
    assert '"dims.md" = "foundations/dimensionality.md"' in out
    assert '"notebooks/3dep/index.md" = "notebooks/research.md#3dep-canopy-height-models"' in out
    assert '# TODO no rule: "unknown-thing.md"' in out
    assert '"notebooks/old_dla.md" = "notebooks/foundations/dla.md"' in out
    assert "foundations/history" not in out.split("[project.plugins.redirects.redirect_maps]")[1].split("# gh-pages")[0]
