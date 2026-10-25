from pathlib import Path

import validate_okf as vo
from conftest import SITE_URL


def run(bundle: Path, profile: str, **kw):
    excludes = kw.pop("excludes", [])
    rep, types, unverified = vo.validate(bundle, profile, SITE_URL, vo.PROFILES[profile]["resource_prefix"], excludes, kw.pop("cfg", None), kw.pop("strict", False))
    return rep, types


def errors_of(rep):
    return [line for line in rep.lines if "[ERROR]" in line]


def warnings_of(rep):
    return [line for line in rep.lines if "[WARN]" in line]


def test_docs_profile_passes_on_fixture(fx):
    rep, types = run(fx.docs, "docs", excludes=["okf/concepts/**", "okf/proofs/**"], cfg=fx.cfg)
    assert errors_of(rep) == [], rep.lines
    assert types["Index"] == 4 and types["Chapter"] == 1 and types["Paper Section"] == 1 and types["Guide"] == 1 and types["Log"] == 1
    # excluded files (notes/, README.md) and dot-dirs are skipped entirely
    assert not any("notes/PLAN.md" in line or "README.md" in line for line in rep.lines)


def test_docs_profile_errors(fx):
    u = SITE_URL + "/"
    hist = fx.docs / "foundations" / "history.md"
    text = hist.read_text(encoding="utf-8")
    hist.write_text(text.replace("type: Chapter\n", "").replace('description: "A fixture', 'description: "Has <angle brackets> and A fixture'), encoding="utf-8")
    (fx.docs / "agents.md").write_text((fx.docs / "agents.md").read_text(encoding="utf-8").replace('title: "For AI Agents"', 'title: "Fixture Home"').replace(f"resource: {u}agents/", f"resource: {u}wrong/"), encoding="utf-8")
    idx = fx.docs / "index.md"
    idx.write_text(idx.read_text(encoding="utf-8").replace('---\nokf_version: "0.2"\ntype: Index\n', '---\ntype: Index\nokf_version: "0.2"\n'), encoding="utf-8")
    (fx.docs / "weird.md").write_text("---\ntype: Blog Post\ntitle: W\ndescription: " + "w" * 60 + f"\nresource: {u}weird/\ntags: [notebook]\ngenerated:\n  by: nobody\n  at: 2026-01-01\nstatus: live\n---\n# W\n", encoding="utf-8")
    rep, _ = run(fx.docs, "docs", excludes=["okf/concepts/**", "okf/proofs/**"], cfg=fx.cfg)
    errs = "\n".join(errors_of(rep))
    assert "foundations/history.md: [ERROR] frontmatter must contain a non-empty 'type'" in errs
    assert "attribute-breaking characters" in errs
    assert "[ERROR] title 'Fixture Home' duplicates" in errs  # reported on whichever page sorts second
    assert f"agents.md: [ERROR] resource '{u}wrong/' != canonical '{u}agents/'" in errs
    assert "index.md: [ERROR] bundle root index.md must declare okf_version" in errs
    assert "weird.md: [ERROR] type 'Blog Post' not in this bundle's taxonomy" in errs
    assert "weird.md: [ERROR] generated.by 'nobody' is not a valid OKF actor" in errs
    assert "weird.md: [ERROR] generated.at" in errs  # unquoted date parsed as a date object
    assert "weird.md: [ERROR] status 'live'" in errs
    assert "not reachable from index.md through index pages: weird.md" in "\n".join(warnings_of(rep))


def test_docs_profile_warnings(fx):
    page = fx.docs / "foundations" / "history.md"
    text = page.read_text(encoding="utf-8").replace("tags: [foundations, part-i, classics]", "tags: [foundations, part-i, classics, made-up]").replace("# Chapter 1\n", "# Chapter 1\n\n[bad](nope.md) [abs](/foundations/index.md)\n")
    page.write_text(text.replace("status: stable\n---", "status: stable\nmystery: 1\n---"), encoding="utf-8")
    rep, _ = run(fx.docs, "docs", excludes=["okf/concepts/**", "okf/proofs/**"], cfg=fx.cfg)
    warns = "\n".join(warnings_of(rep))
    assert errors_of(rep) == []
    assert "tags not in vocabulary: ['made-up']" in warns
    assert "unknown frontmatter keys ['mystery']" in warns
    assert "broken internal link: nope.md" in warns
    assert "root-absolute link '/foundations/index.md'" in warns
    assert "keys are not in the canonical order" not in warns
    # key-order warning
    page.write_text(page.read_text(encoding="utf-8").replace('type: Chapter\ntitle: "Chapter 1: History of Fractals"\n', 'title: "Chapter 1: History of Fractals"\ntype: Chapter\n'), encoding="utf-8")
    rep, _ = run(fx.docs, "docs", excludes=["okf/concepts/**", "okf/proofs/**"], cfg=fx.cfg)
    assert "keys are not in the canonical order" in "\n".join(warnings_of(rep))


def test_authors_orcid_and_paper(fx):
    page = fx.docs / "metabolic-scaling" / "abstract.md"
    page.write_text(page.read_text(encoding="utf-8").replace("https://orcid.org/0000-0002-6639-7181", "0000-0002-6639-7181"), encoding="utf-8")
    rep, _ = run(fx.docs, "docs", excludes=["okf/**"], cfg=fx.cfg)
    assert any("authors[0].orcid" in line for line in errors_of(rep))


def test_log_page_rules(fx):
    log = fx.docs / "log.md"
    log.write_text(log.read_text(encoding="utf-8").replace("## 2026-02-01", "## 2025-12-01").replace("- **Update**: second.", "- second without a convention word."), encoding="utf-8")
    rep, _ = run(fx.docs, "docs", excludes=["okf/**"], cfg=fx.cfg)
    assert any("date headings must be strictly newest-first" in line for line in errors_of(rep))
    assert any("bullet without **Creation**" in line for line in warnings_of(rep))


def test_concept_profile(fx):
    rep, types = run(fx.okf / "concepts", "concept")
    assert errors_of(rep) == [], rep.lines
    assert types == {"Fractal Concept": 1}
    # group index must not carry frontmatter; root must carry only okf_version
    (fx.okf / "concepts" / "geometry" / "index.md").write_text("---\ntitle: Geometry\n---\n# Geometry\n", encoding="utf-8")
    (fx.okf / "concepts" / "index.md").write_text('---\nokf_version: "0.2"\ntitle: extra\n---\n# C\n\n* [Geometry](geometry/index.md)\n', encoding="utf-8")
    page = fx.okf / "concepts" / "geometry" / "fractal.md"
    page.write_text(page.read_text(encoding="utf-8").replace("* [Geometry index](index.md)", "* [self](/geometry/fractal.md)"), encoding="utf-8")
    rep, _ = run(fx.okf / "concepts", "concept")
    errs = "\n".join(errors_of(rep))
    assert "geometry/index.md: [ERROR] index.md must not contain frontmatter" in errs
    assert "root index.md frontmatter must be exactly okf_version" in errs
    assert "root-absolute link '/geometry/fractal.md'" in "\n".join(warnings_of(rep))


def test_proof_profile(fx):
    rep, types = run(fx.okf / "proofs", "proof")
    assert errors_of(rep) == [], rep.lines
    assert types == {"Fractal Proof": 1}
    p1 = fx.okf / "proofs" / "p1.md"
    p1.write_text(p1.read_text(encoding="utf-8").replace("verification_status: verified", "verification_status: checked").replace("concept: ../concepts/geometry/fractal.md", "concept: ../concepts/geometry/missing.md"), encoding="utf-8")
    (fx.okf / "proofs" / "log.md").write_text("---\ntype: Log\n---\n# L\n\n## 2026-01-01\n\n* **Creation**: x\n", encoding="utf-8")
    rep, _ = run(fx.okf / "proofs", "proof")
    errs = "\n".join(errors_of(rep))
    assert "verification_status 'checked'" in errs
    assert "log.md must not contain frontmatter" in errs


def test_strict_turns_coverage_into_errors(fx):
    (fx.docs / "lonely.md").write_text("---\ntype: Guide\ntitle: Lonely\ndescription: " + "l" * 60 + f"\nresource: {SITE_URL}/lonely/\ntags: [agents, okf]\ngenerated:\n  by: human:t\n  at: \"2026-01-01T00:00:00Z\"\nstatus: stable\n---\n# L\n", encoding="utf-8")
    rep, _ = run(fx.docs, "docs", excludes=["okf/**"], cfg=fx.cfg, strict=True)
    assert any("not reachable from index.md" in line for line in errors_of(rep))


def test_cli(fx, monkeypatch, capsys):
    monkeypatch.setattr(vo, "ROOT", fx.root)
    rc = vo.main([str(fx.docs), "--exclude", "okf/**", "--config", str(fx.config)])
    out = capsys.readouterr().out
    assert rc == 0 and "0 error(s)" in out and "type counts: Chapter=1" in out
    assert vo.main([str(fx.okf / "concepts"), "--profile", "concept", "--site-url", SITE_URL]) == 0
    assert vo.main([str(fx.okf / "proofs"), "--site-url", SITE_URL]) == 0  # profile inferred from the directory name
    assert vo.main([str(fx.root / "nowhere")]) == 2
