"""Unit tests for the OKF v0.2 concept bundle exporter (``fractal_rag.okf_export``)."""

from __future__ import annotations

import builtins
import io
import os
import pathlib
import re
import subprocess
import sys

import pytest
import yaml
from click.testing import CliRunner

from fractal_rag import okf_export
from fractal_rag.cli import main as cli_main
from fractal_rag.okf_export import (
    DEFAULT_SEED,
    GENERATOR,
    LOG_TITLE,
    OKF_VERSION,
    SITE_URL,
    UnmanagedFilesError,
    bundle_url,
    description_for,
    export,
    load_concepts,
    main,
    plan,
    run,
    split_frontmatter,
    update_log,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
COMMITTED_BUNDLE = REPO_ROOT / "okf" / "concepts"
SRC_DIR = pathlib.Path(okf_export.__file__).resolve().parents[1]

EN_DASH = chr(0x2013)
ARROW = chr(0x2192)
GEQ = chr(0x2265)
DATE = "2026-10-24"

# Three concepts across two groups; Beta Flow lives in `dynamics`, the others in `geometry`.
# The definitions exercise the description sanitizer and a non-ASCII dash.
FIXTURE_SEED = """\
# fixture seed
- name: Alpha Shape
  aliases: [alpha, alpha shapes]
  definition: >-
    A base shape with self-similar structure at every scale. It is related to the
    beta flow when x -> y.
  domain: [geometry, foundations]

- name: Beta Flow
  aliases: [beta]
  definition: >-
    A flow on an alpha shape whose scaling obeys x >= 1 and "quotes" <tags>. Second sentence.
  domain: [dynamics, geometry]
  hausdorff_dim_range: [1.5, 1.7]

- name: Gamma Dust
  aliases: []
  definition: >-
    Dust left by an alpha shape under a beta flow; the en dash <DASH> survives round trips.
  domain: [geometry]
"""

EXPECTED_FILES = [
    "dynamics/beta-flow.md",
    "dynamics/index.md",
    "geometry/alpha-shape.md",
    "geometry/gamma-dust.md",
    "geometry/index.md",
    "index.md",
]

LINK_RE = re.compile(r"\]\(([^)]+)\)")


@pytest.fixture
def seed(tmp_path: pathlib.Path) -> pathlib.Path:
    p = tmp_path / "seed.yaml"
    p.write_text(FIXTURE_SEED.replace("<DASH>", EN_DASH), encoding="utf-8")
    return p


def _md_files(root: pathlib.Path) -> list[str]:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*.md"))


def _snapshot(root: pathlib.Path) -> dict[str, bytes]:
    return {rel: (root / rel).read_bytes() for rel in _md_files(root)}


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _frontmatter(path: pathlib.Path) -> dict | None:
    return split_frontmatter(_read(path))[0]


def _links(path: pathlib.Path) -> list[str]:
    return [t for t in LINK_RE.findall(_read(path)) if not t.startswith(("http://", "https://"))]


def _change_seed(seed: pathlib.Path, old: str, new: str) -> None:
    text = _read(seed)
    assert old in text
    seed.write_text(text.replace(old, new), encoding="utf-8")


def _generated_stub(title: str) -> str:
    """A Markdown file that looks like exporter output (``generated.by`` is the exporter)."""
    return (
        f"---\ntype: Fractal Concept\ntitle: {title}\ngenerated:\n  by: {GENERATOR}\n"
        f'  at: "{DATE}T00:00:00Z"\nstatus: stable\n---\n\n# {title}\n'
    )


def _human_stub(title: str) -> str:
    return (
        f"---\ntype: Fractal Proof\ntitle: {title}\ngenerated:\n  by: human:tswetnam\n"
        f'  at: "{DATE}T00:00:00Z"\nstatus: stable\n---\n\n# {title}\n'
    )


# ---------------------------------------------------------------------------
# Determinism & idempotency


def test_export_is_deterministic_for_a_fixed_date(seed: pathlib.Path, tmp_path: pathlib.Path) -> None:
    a, b = tmp_path / "a", tmp_path / "b"
    stats_a = export(seed, a, DATE)
    stats_b = export(seed, b, DATE)
    assert stats_a == stats_b == {
        "concepts": 3,
        "groups": 2,
        "added": 6,
        "updated": 0,
        "deleted": 0,
        "pruned": 0,
        "unknown": 0,
        "changed": 6,
    }
    assert _md_files(a) == [*EXPECTED_FILES, "log.md"]
    assert _snapshot(a) == _snapshot(b)


def test_second_export_changes_nothing_even_with_a_new_date(seed: pathlib.Path, tmp_path: pathlib.Path) -> None:
    out = tmp_path / "bundle"
    export(seed, out, DATE)
    before = _snapshot(out)
    stats = export(seed, out, "2027-01-01")
    assert stats["changed"] == 0
    assert _snapshot(out) == before  # including log.md: nothing was appended
    assert 'at: "2026-10-24T00:00:00Z"' in _read(out / "geometry/alpha-shape.md")


# ---------------------------------------------------------------------------
# Links


def test_related_links_are_relative_and_resolve_on_disk(seed: pathlib.Path, tmp_path: pathlib.Path) -> None:
    out = tmp_path / "bundle"
    export(seed, out, DATE)
    concept_files = [out / rel for rel in EXPECTED_FILES if not rel.endswith("index.md")]
    seen = 0
    for path in concept_files:
        for target in _links(path):
            seen += 1
            assert not target.startswith("/"), f"{path.name}: root-absolute link {target}"
            assert (path.parent / target).resolve().is_file(), f"{path.name}: dangling {target}"
    assert seen >= 3

    beta = _read(out / "dynamics/beta-flow.md")
    assert "* [Alpha Shape](../geometry/alpha-shape.md)" in beta  # cross-group, title as text
    gamma = _read(out / "geometry/gamma-dust.md")
    assert "* [Alpha Shape](alpha-shape.md)" in gamma  # same group
    assert "* [Beta Flow](../dynamics/beta-flow.md)" in gamma
    assert "[alpha]" not in gamma  # alias never used as link text


def test_root_index_links_group_indexes_and_carries_only_okf_version(
    seed: pathlib.Path, tmp_path: pathlib.Path
) -> None:
    out = tmp_path / "bundle"
    export(seed, out, DATE)
    root = out / "index.md"
    assert _frontmatter(root) == {"okf_version": OKF_VERSION}
    targets = _links(root)
    group_links = [t for t in targets if t != "log.md"]
    assert group_links == ["dynamics/index.md", "geometry/index.md"]
    assert all(t.endswith("/index.md") for t in group_links)
    assert all((out / t).is_file() for t in targets)
    assert "- 2 concepts" in _read(root) and "- 1 concept\n" in _read(root)
    # the maintainer note is an HTML comment right under the H1; the prose is one plain sentence
    root_text = _read(root)
    body = root_text.split("---\n", 2)[2]
    lines = [ln for ln in body.split("\n") if ln.strip()]
    assert lines[0].startswith("# ")
    assert lines[1].startswith("<!-- Generated from `fractal_rag/src/fractal_rag/concepts/seed.yaml`")
    assert lines[1].endswith("-->") and "do not edit these files by hand" in lines[1]
    assert lines[2] == (
        "Canonical concepts for self-affine fractals, dimension theory, and metabolic scaling, "
        "grouped by domain."
    )
    assert body.count("do not edit") == 1  # only inside the comment
    # group indexes and the log have no frontmatter
    assert _frontmatter(out / "geometry/index.md") is None
    assert _frontmatter(out / "log.md") is None
    assert "* [Alpha Shape](alpha-shape.md) - A base shape" in _read(out / "geometry/index.md")


# ---------------------------------------------------------------------------
# Frontmatter


def test_concept_frontmatter_has_v02_keys_in_order(seed: pathlib.Path, tmp_path: pathlib.Path) -> None:
    out = tmp_path / "bundle"
    export(seed, out, DATE)

    beta_text = _read(out / "dynamics/beta-flow.md")
    beta = split_frontmatter(beta_text)[0]
    assert beta is not None
    assert list(beta) == [
        "type",
        "title",
        "description",
        "resource",
        "tags",
        "aliases",
        "hausdorff_dim_range",
        "sources",
        "generated",
        "status",
    ]
    assert beta["type"] == "Fractal Concept"
    assert beta["title"] == "Beta Flow"
    assert beta["description"] == f"A flow on an alpha shape whose scaling obeys x {GEQ} 1 and 'quotes' tags."
    assert beta["resource"] == f"{bundle_url()}dynamics/beta-flow/"
    assert beta["tags"] == ["dynamics", "geometry"]
    assert beta["aliases"] == ["beta"]
    assert beta["hausdorff_dim_range"] == [1.5, 1.7]
    assert [s["id"] for s in beta["sources"]] == ["glossary", "seed"]
    assert all(s["resource"].startswith("https://") and s["title"] for s in beta["sources"])
    assert beta["sources"][0]["resource"] == f"{SITE_URL}/foundations/glossary/"
    assert beta["generated"] == {"by": GENERATOR, "at": f"{DATE}T00:00:00Z"}
    assert isinstance(beta["generated"]["at"], str)  # quoted, not a YAML timestamp
    assert f'at: "{DATE}T00:00:00Z"' in beta_text
    assert beta["status"] == "stable"
    assert "timestamp" not in beta
    assert "okf_version" not in beta
    assert f"Approximately **1.5 {EN_DASH} 1.7**." in beta_text

    gamma = _frontmatter(out / "geometry/gamma-dust.md")
    assert gamma is not None
    assert list(gamma) == ["type", "title", "description", "resource", "tags", "sources", "generated", "status"]
    assert EN_DASH in gamma["description"]

    alpha = _frontmatter(out / "geometry/alpha-shape.md")
    assert alpha is not None
    assert alpha["description"] == "A base shape with self-similar structure at every scale."
    for fm in (alpha, beta, gamma):
        assert not any(ch in fm["description"] for ch in '"<>')
        assert 50 <= len(fm["description"]) <= 300


def test_site_url_override_changes_resource_and_source_urls(seed: pathlib.Path, tmp_path: pathlib.Path) -> None:
    out = tmp_path / "bundle"
    export(seed, out, DATE, site_url="https://example.org/site/")
    fm = _frontmatter(out / "geometry/alpha-shape.md")
    assert fm is not None
    assert fm["resource"] == "https://example.org/site/okf/concepts/geometry/alpha-shape/"
    assert fm["sources"][0]["resource"] == "https://example.org/site/foundations/glossary/"
    assert fm["sources"][1]["resource"].startswith("https://github.com/")  # seed URL is repo-based


def test_description_sanitizer() -> None:
    assert description_for('x -> y and a >= b; "q" <t>. Next sentence.') == f"x {ARROW} y and a {GEQ} b; 'q' t."
    assert description_for("  Many\n  spaces   here.  ") == "Many spaces here."
    assert description_for("No terminal period") == "No terminal period"


def test_description_does_not_stop_at_abbreviations() -> None:
    assert (
        description_for("Complex values, used by Lapidus et al. to describe oscillations of sets. More.")
        == "Complex values, used by Lapidus et al. to describe oscillations of sets."
    )
    assert description_for("Rough curves, e.g. coastlines, i.e. not smooth. Next.") == "Rough curves, e.g. coastlines, i.e. not smooth."
    assert description_for("Compare cf. Fig. 2 vs. Fig. 3 here. Next.") == "Compare cf. Fig. 2 vs. Fig. 3 here."
    assert description_for("Ends with an abbreviation et al.") == "Ends with an abbreviation et al."
    assert description_for("Plain. Second.") == "Plain."


# ---------------------------------------------------------------------------
# generated.at preservation


def test_generated_at_preserved_unless_content_changes(seed: pathlib.Path, tmp_path: pathlib.Path) -> None:
    out = tmp_path / "bundle"
    export(seed, out, "2026-01-01")
    _change_seed(seed, "Dust left by an alpha shape", "Residue left by an alpha shape")
    stats = export(seed, out, "2026-02-02")
    assert stats["added"] == 0 and stats["deleted"] == 0
    assert stats["updated"] == 2  # the concept and its group index (description changed)
    assert 'at: "2026-01-01T00:00:00Z"' in _read(out / "geometry/alpha-shape.md")
    assert 'at: "2026-01-01T00:00:00Z"' in _read(out / "dynamics/beta-flow.md")
    assert 'at: "2026-02-02T00:00:00Z"' in _read(out / "geometry/gamma-dust.md")


def test_check_ignores_generated_at_only_differences(seed: pathlib.Path, tmp_path: pathlib.Path) -> None:
    out = tmp_path / "bundle"
    export(seed, out, DATE)
    path = out / "geometry/alpha-shape.md"
    tampered = _read(path).replace(f'at: "{DATE}T00:00:00Z"', 'at: "2020-05-05T00:00:00Z"')
    path.write_text(tampered, encoding="utf-8")
    assert export(seed, out, DATE, check=True)["changed"] == 0
    export(seed, out, DATE)  # a real run leaves the hand-set date alone too
    assert _read(path) == tampered


# ---------------------------------------------------------------------------
# Log


def test_log_is_append_only_without_same_day_duplicates(seed: pathlib.Path, tmp_path: pathlib.Path) -> None:
    out = tmp_path / "bundle"
    out.mkdir()
    old = f"{LOG_TITLE}\n\n## 2025-01-01\n* **Initialization**: Generated OKF v0.1 bundle.\n"
    (out / "log.md").write_text(old, encoding="utf-8")

    export(seed, out, DATE)
    log = _read(out / "log.md")
    assert log.startswith(f"{LOG_TITLE}\n\n## {DATE}\n")
    assert log.index(f"## {DATE}") < log.index("## 2025-01-01")
    assert "* **Initialization**: Generated OKF v0.1 bundle." in log
    assert "* **Creation**: 6 files added" in log and "`geometry/alpha-shape.md`" in log
    assert _frontmatter(out / "log.md") is None

    export(seed, out, DATE)  # same day, nothing changed -> log untouched
    assert _read(out / "log.md") == log

    _change_seed(seed, "A base shape with self-similar structure", "A seed shape with self-similar structure")
    export(seed, out, DATE)  # same day, real change -> bullet added to the same section
    log2 = _read(out / "log.md")
    assert log2.count(f"## {DATE}") == 1
    assert log2.count("## 2025-01-01") == 1
    assert "* **Update**: 2 files regenerated" in log2
    assert "* **Initialization**: Generated OKF v0.1 bundle." in log2
    assert log2.index("* **Creation**") < log2.index("* **Update**") < log2.index("## 2025-01-01")


def test_update_log_unit() -> None:
    assert update_log(None, DATE, [], [], []) is None
    fresh = update_log(None, DATE, ["a.md"], [], [])
    assert fresh == f"{LOG_TITLE}\n\n## {DATE}\n* **Creation**: 1 file added by the OKF v{OKF_VERSION} exporter from `concepts/seed.yaml`: `a.md`.\n"
    legacy = f"---\ntype: Log\n---\n{LOG_TITLE}\n\n## 2025-01-01\n* **Initialization**: x.\n"
    rebuilt = update_log(legacy, DATE, [], ["b.md"], ["c.md"])
    assert rebuilt is not None
    assert not rebuilt.startswith("---")  # frontmatter dropped: the log is frontmatter-free
    assert "* **Update**: 1 file regenerated" in rebuilt
    assert "* **Deprecation**: 1 stale file removed" in rebuilt and "`c.md`" in rebuilt
    assert "Deletion" not in rebuilt  # OKF log vocabulary is Creation / Update / Deprecation
    assert rebuilt.endswith("## 2025-01-01\n* **Initialization**: x.\n")
    pruned = update_log(None, DATE, [], [], [], ["README.md"])
    assert pruned is not None
    assert "* **Deprecation**: 1 unmanaged file not generated by the exporter removed with `--prune-unknown`: `README.md`." in pruned


# ---------------------------------------------------------------------------
# Stale files


def test_stale_markdown_is_deleted_and_logged(seed: pathlib.Path, tmp_path: pathlib.Path) -> None:
    """Files the exporter generated earlier (and a group index left with only such files) go."""
    out = tmp_path / "bundle"
    export(seed, out, DATE)
    (out / "geometry" / "old-thing.md").write_text(_generated_stub("Old Thing"), encoding="utf-8")
    (out / "misc").mkdir()
    (out / "misc" / "zzz.md").write_text(_generated_stub("Zzz"), encoding="utf-8")
    (out / "misc" / "index.md").write_text("# Misc\n\n* [Zzz](zzz.md) - Zzz.\n", encoding="utf-8")
    (out / "notes.txt").write_text("keep me\n", encoding="utf-8")

    checked = export(seed, out, DATE, check=True)
    assert checked["deleted"] == 3 and checked["changed"] == 3 and checked["unknown"] == 0
    assert (out / "geometry" / "old-thing.md").exists()  # check mode deletes nothing

    stats = export(seed, out, DATE)
    assert stats["deleted"] == 3 and stats["pruned"] == 0
    assert not (out / "geometry" / "old-thing.md").exists()
    assert not (out / "misc").exists()  # emptied directory removed
    assert (out / "notes.txt").exists()  # only *.md is managed
    assert (out / "log.md").exists()
    log = _read(out / "log.md")
    assert "* **Deprecation**: 3 stale files removed" in log
    assert "`geometry/old-thing.md`" in log and "`misc/zzz.md`" in log and "`misc/index.md`" in log
    assert "Deletion" not in log


def test_unmanaged_markdown_blocks_the_run_unless_pruned(seed: pathlib.Path, tmp_path: pathlib.Path) -> None:
    """``--out okf`` (one level too high) must not wipe README.md, the proofs or nested logs."""
    out = tmp_path / "okf"
    export(seed, out, DATE)
    (out / "README.md").write_text("# OKF knowledge bundles\n", encoding="utf-8")
    (out / "proofs").mkdir()
    (out / "proofs" / "x.md").write_text(_human_stub("Proof X"), encoding="utf-8")
    (out / "proofs" / "index.md").write_text('---\nokf_version: "0.2"\n---\n\n# Proofs\n\n* [x](x.md)\n', encoding="utf-8")
    (out / "proofs" / "log.md").write_text("# Proof Bundle Change Log\n\n## 2026-07-13\n* **Creation**: x.\n", encoding="utf-8")
    (out / "geometry" / "log.md").write_text(_generated_stub("Not Really A Log"), encoding="utf-8")
    before = _snapshot(out)

    # check mode: reported, exit 1, nothing written
    checked = export(seed, out, DATE, check=True)
    assert checked["unknown"] == 3 and checked["deleted"] == 0 and checked["pruned"] == 0 and checked["changed"] == 0
    code, message = run(seed, out, DATE, SITE_URL, check=True)
    assert code == 1
    assert "3 unmanaged file(s)" in message
    for rel in ("README.md", "proofs/index.md", "proofs/x.md"):
        assert f"  ? {rel} (not generated by this exporter; remove it or pass --prune-unknown)" in message
    assert "log.md" not in message  # logs at any depth are neither stale nor unmanaged
    assert _snapshot(out) == before

    # write mode: refuses before touching anything
    with pytest.raises(UnmanagedFilesError, match=r"refusing to write .*okf") as excinfo:
        export(seed, out, DATE)
    assert excinfo.value.files == ["README.md", "proofs/index.md", "proofs/x.md"]
    assert "--prune-unknown" in str(excinfo.value)
    code, message = run(seed, out, DATE, SITE_URL, check=False)
    assert code == 2 and "refusing" in message and "? proofs/x.md" in message
    assert main(["--seed", str(seed), "--out", str(out), "--date", DATE]) == 2
    assert _snapshot(out) == before  # not even the log changed

    # --prune-unknown: the unmanaged files go, every log.md stays, and the log records it
    stats = export(seed, out, DATE, prune_unknown=True)
    assert stats["pruned"] == 3 and stats["unknown"] == 0 and stats["deleted"] == 0 and stats["changed"] == 3
    assert not (out / "README.md").exists() and not (out / "proofs" / "x.md").exists()
    assert not (out / "proofs" / "index.md").exists()
    assert (out / "proofs" / "log.md").exists() and (out / "geometry" / "log.md").exists()
    log = _read(out / "log.md")
    assert "* **Deprecation**: 3 unmanaged files not generated by the exporter removed with `--prune-unknown`: `README.md`, `proofs/index.md`, `proofs/x.md`." in log
    assert export(seed, out, DATE, check=True)["changed"] == 0


def test_cli_prune_unknown_flag(seed: pathlib.Path, tmp_path: pathlib.Path) -> None:
    out = tmp_path / "bundle"
    runner = CliRunner()
    args = ["okf", "export", "--seed", str(seed), "--out", str(out), "--date", DATE]
    assert runner.invoke(cli_main, args).exit_code == 0
    (out / "stray.md").write_text("# Stray\n", encoding="utf-8")
    res = runner.invoke(cli_main, args)
    assert res.exit_code == 2, res.output
    assert "refusing" in res.output and "? stray.md" in res.output
    assert (out / "stray.md").exists()
    res = runner.invoke(cli_main, [*args, "--prune-unknown"])
    assert res.exit_code == 0, res.output
    assert "1 pruned" in res.output
    assert not (out / "stray.md").exists()


# ---------------------------------------------------------------------------
# Check mode


def test_check_mode_detects_drift_and_writes_nothing(seed: pathlib.Path, tmp_path: pathlib.Path, capsys) -> None:
    out = tmp_path / "bundle"
    stats = export(seed, out, DATE, check=True)
    assert stats == {"concepts": 3, "groups": 2, "added": 6, "updated": 0, "deleted": 0, "pruned": 0, "unknown": 0, "changed": 6}
    assert not out.exists() or _md_files(out) == []

    assert main(["--check", "--seed", str(seed), "--out", str(out)]) == 1
    assert "out of date" in capsys.readouterr().out

    assert main(["--seed", str(seed), "--out", str(out), "--date", DATE]) == 0
    assert "Wrote 3 concepts across 2 groups" in capsys.readouterr().out
    assert main(["--check", "--seed", str(seed), "--out", str(out)]) == 0
    assert "up to date" in capsys.readouterr().out

    path = out / "dynamics/beta-flow.md"
    drifted = _read(path) + "\nhand edit\n"
    path.write_text(drifted, encoding="utf-8")
    before = _snapshot(out)
    code, message = run(seed, out, DATE, SITE_URL, check=True)
    assert code == 1
    assert "~ dynamics/beta-flow.md" in message
    assert _snapshot(out) == before  # nothing written, not even the log


def test_cli_okf_export_matches_module_entry_point(seed: pathlib.Path, tmp_path: pathlib.Path) -> None:
    out = tmp_path / "bundle"
    runner = CliRunner()
    args = ["okf", "export", "--seed", str(seed), "--out", str(out), "--date", DATE]
    res = runner.invoke(cli_main, [*args, "--check"])
    assert res.exit_code == 1, res.output
    assert "out of date" in res.output
    res = runner.invoke(cli_main, [*args, "--site-url", "https://example.org/x"])
    assert res.exit_code == 0, res.output
    assert "Wrote 3 concepts across 2 groups" in res.output
    assert "https://example.org/x/okf/concepts/geometry/alpha-shape/" in _read(out / "geometry/alpha-shape.md")
    res = runner.invoke(cli_main, [*args, "--site-url", "https://example.org/x", "--check"])
    assert res.exit_code == 0, res.output
    assert "up to date" in res.output


# ---------------------------------------------------------------------------
# Encoding


def test_all_text_io_is_explicit_utf8(seed: pathlib.Path, tmp_path: pathlib.Path, monkeypatch) -> None:
    """Every text-mode open() must pass encoding='utf-8' (the locale default is 'locale')."""
    out = tmp_path / "bundle"
    real_open = io.open
    opened: list[str] = []

    def strict_open(file, mode="r", *args, **kwargs):
        if "b" not in mode:
            encoding = kwargs.get("encoding", args[1] if len(args) > 1 else None)
            assert encoding == "utf-8", f"text open without utf-8: {file} mode={mode} encoding={encoding!r}"
            opened.append(str(file))
        return real_open(file, mode, *args, **kwargs)

    with monkeypatch.context() as m:
        m.setattr(io, "open", strict_open)
        m.setattr(builtins, "open", strict_open)
        export(seed, out, DATE)
        assert export(seed, out, DATE, check=True)["changed"] == 0
    assert any(p.endswith("gamma-dust.md") for p in opened)

    raw = (out / "geometry/gamma-dust.md").read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")  # must not raise
    assert EN_DASH in text
    assert EN_DASH.encode("utf-8") in raw


def test_round_trip_under_ascii_locale_subprocess(seed: pathlib.Path, tmp_path: pathlib.Path) -> None:
    """Run the module entry point with a C locale and UTF-8 mode disabled."""
    env = {
        "PATH": os.environ.get("PATH", ""),
        "LC_ALL": "C",
        "LANG": "C",
        "PYTHONUTF8": "0",
        "PYTHONCOERCECLOCALE": "0",
        "PYTHONPATH": str(SRC_DIR),
    }
    probe = subprocess.run(
        [sys.executable, "-c", "import locale,sys;print(locale.getpreferredencoding(False), sys.flags.utf8_mode)"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    preferred, utf8_mode = probe.stdout.split()
    if utf8_mode != "0" or "utf" in preferred.lower():
        pytest.skip(f"interpreter cannot be put into an ASCII locale here ({preferred}, utf8_mode={utf8_mode})")

    out = tmp_path / "bundle"
    cmd = [sys.executable, "-m", "fractal_rag.okf_export", "--seed", str(seed), "--out", str(out), "--date", DATE]
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    text = (out / "geometry/gamma-dust.md").read_text(encoding="utf-8")
    assert EN_DASH in text
    res = subprocess.run([*cmd, "--check"], env=env, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


# ---------------------------------------------------------------------------
# Seed validation


def test_load_concepts_rejects_duplicates_and_bad_entries(tmp_path: pathlib.Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("- name: A\n  definition: x.\n- name: a\n  definition: y.\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        load_concepts(bad)
    bad.write_text("- name: A\n", encoding="utf-8")
    with pytest.raises(ValueError, match="needs 'name' and 'definition'"):
        load_concepts(bad)
    bad.write_text("name: A\n", encoding="utf-8")
    with pytest.raises(ValueError, match="YAML list"):
        load_concepts(bad)


def test_invalid_date_is_rejected(seed: pathlib.Path, tmp_path: pathlib.Path) -> None:
    with pytest.raises(ValueError, match="ISO date"):
        export(seed, tmp_path / "x", "24/10/2026")


# ---------------------------------------------------------------------------
# The real seed and the committed bundle


def test_real_seed_has_32_concepts_in_12_groups() -> None:
    concepts = load_concepts(DEFAULT_SEED)
    assert len(concepts) == 32
    assert len(okf_export.group_concepts(concepts)) == 12
    for c in concepts:
        desc = description_for(c["definition"])
        assert not any(ch in desc for ch in '"<>'), c["name"]
        assert 50 <= len(desc) <= 300, (c["name"], len(desc))


@pytest.mark.skipif(not COMMITTED_BUNDLE.is_dir(), reason="committed okf/concepts bundle not available")
def test_committed_bundle_matches_seed_and_is_v02() -> None:
    result = plan(DEFAULT_SEED, COMMITTED_BUNDLE)
    assert (result.n_concepts, result.n_groups) == (32, 12)
    assert result.changed == 0, (result.added, result.updated, result.deleted)
    assert export(DEFAULT_SEED, COMMITTED_BUNDLE, check=True)["changed"] == 0

    assert _frontmatter(COMMITTED_BUNDLE / "index.md") == {"okf_version": OKF_VERSION}
    concept_pages = [p for p in COMMITTED_BUNDLE.rglob("*.md") if p.name not in ("index.md", "log.md")]
    assert len(concept_pages) == 32
    for page in concept_pages:
        text = _read(page)
        assert "](/" not in text, f"{page}: root-absolute link"
        fm = yaml.safe_load(text.split("---\n")[1])
        assert fm["type"] == "Fractal Concept"
        assert fm["resource"] == f"{bundle_url()}{page.parent.name}/{page.stem}/"
        assert fm["generated"]["by"] == GENERATOR
        for target in _links(page):
            assert (page.parent / target).resolve().is_file(), f"{page}: dangling {target}"
