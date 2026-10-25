
import publish_sources as ps
from conftest import SITE_URL


def test_twins_are_placed_at_source_paths(built_fx):
    written, errors = ps.publish(built_fx.cfg, built_fx.site, built_fx.docs, built_fx.okf)
    assert errors == [], errors
    site = built_fx.site
    # docs pages: a/b.md and X/index.md and the home index.md
    assert (site / "index.md").read_bytes() == (built_fx.docs / "index.md").read_bytes()
    assert (site / "foundations" / "history.md").read_bytes() == (built_fx.docs / "foundations" / "history.md").read_bytes()
    assert (site / "metabolic-scaling" / "index.md").is_file()
    assert (site / "agents.md").is_file() and (site / "log.md").is_file()
    # okf pages resolve against the canonical okf/ tree (not docs/okf, which is never staged in this test)
    assert (site / "okf" / "concepts" / "index.md").read_text(encoding="utf-8").startswith('---\nokf_version: "0.2"')
    assert (site / "okf" / "concepts" / "geometry" / "fractal.md").read_bytes() == (built_fx.okf / "concepts" / "geometry" / "fractal.md").read_bytes()
    assert (site / "okf" / "concepts" / "geometry" / "index.md").is_file()
    assert (site / "okf" / "proofs" / "p1.md").is_file() and (site / "okf" / "proofs" / "log.md").is_file()
    assert (site / "okf" / "index.md").read_bytes() == (built_fx.docs / "okf" / "index.md").read_bytes()
    # redirect stubs get no twin; excluded sources are not published
    assert not (site / "old.md").exists() and not (site / "old" / "index.md").exists()
    assert not (site / "notes").exists() and not (site / "README.md").exists()
    assert written == 15
    # idempotent
    assert ps.publish(built_fx.cfg, built_fx.site, built_fx.docs, built_fx.okf) == (15, [])


def test_post_conditions_and_union_with_docs(built_fx):
    site = built_fx.site
    # a page rendered but missing from the sitemap is still twinned (union with docs/)
    sm = site / "sitemap.xml"
    sm.write_text(sm.read_text(encoding="utf-8").replace(f"<url><loc>{SITE_URL}/agents/</loc></url>", ""), encoding="utf-8")
    written, errors = ps.publish(built_fx.cfg, built_fx.site, built_fx.docs, built_fx.okf)
    assert errors == [] and (site / "agents.md").is_file()
    # leaks are reported
    (site / "notebooks").mkdir(exist_ok=True)
    (site / "notebooks" / "x.ipynb").write_text("{}", encoding="utf-8")
    (site / "superpowers").mkdir(exist_ok=True)
    (site / "stray.md").write_text("x", encoding="utf-8")  # twin without a rendered sibling
    _, errors = ps.publish(built_fx.cfg, built_fx.site, built_fx.docs, built_fx.okf)
    joined = "\n".join(errors)
    assert "notebooks/x.ipynb: forbidden file type" in joined
    assert "superpowers: internal file/path leaked" in joined
    assert "stray.md: twin without a rendered sibling stray/index.html" in joined
    # a sitemap URL with no source at all
    sm.write_text(sm.read_text(encoding="utf-8").replace("</urlset>", f"<url><loc>{SITE_URL}/ghost/</loc></url></urlset>"), encoding="utf-8")
    (site / "ghost").mkdir()
    (site / "ghost" / "index.html").write_text("<html></html>", encoding="utf-8")
    _, errors = ps.publish(built_fx.cfg, built_fx.site, built_fx.docs, built_fx.okf)
    assert any("ghost/: no Markdown source found" in e for e in errors)


def test_verify_alternate_links(built_fx):
    ps.publish(built_fx.cfg, built_fx.site, built_fx.docs, built_fx.okf)
    checked, errors = ps.verify(built_fx.cfg, built_fx.site)
    assert errors == [], errors
    assert checked == 15  # stubs are skipped
    # a page without the alternate link and one whose href points nowhere
    (built_fx.site / "agents" / "index.html").write_text("<html><head></head><body></body></html>", encoding="utf-8")
    (built_fx.site / "foundations" / "history" / "index.html").write_text(f'<html><head><link rel="alternate" type="text/markdown" href="{SITE_URL}/foundations/nope.md"></head></html>', encoding="utf-8")
    _, errors = ps.verify(built_fx.cfg, built_fx.site)
    joined = "\n".join(errors)
    assert 'agents/index.html: no <link rel="alternate"' in joined
    assert "foundations/history/index.html: alternate href" in joined and "does not exist" in joined


def test_cli(built_fx, monkeypatch, capsys):
    monkeypatch.setattr(ps, "ROOT", built_fx.root)
    assert ps.main(["--config", str(built_fx.config), "--okf", str(built_fx.okf), "--verify"]) == 0
    out = capsys.readouterr().out
    assert "15 Markdown twins" in out and "15 pages with a resolvable text/markdown alternate" in out
    assert ps.main(["--config", str(built_fx.root / "missing.toml")]) == 2
    assert ps.main(["--config", str(built_fx.config), "--site", str(built_fx.root / "nosite")]) == 2


def test_redirect_stub_at_old_notes_url_is_not_a_leak(tmp_path):
    from publish_sources import is_redirect_stub_path
    site = tmp_path / "site"
    stub = site / "superpowers" / "specs" / "old-spec" / "index.html"
    stub.parent.mkdir(parents=True)
    stub.write_text('<!doctype html><html><head><title>Redirecting...</title>'
                    '<meta http-equiv="refresh" content="0; url=../../../fractal-rag/"></head></html>', encoding="utf-8")
    assert is_redirect_stub_path(stub, site)
    assert is_redirect_stub_path(site / "superpowers", site)
    real = site / "superpowers" / "specs" / "leak" / "index.html"
    real.parent.mkdir(parents=True)
    real.write_text("<html>r01c01u30-gpu07</html>", encoding="utf-8")
    assert not is_redirect_stub_path(real, site)
    assert not is_redirect_stub_path(site / "superpowers", site)
