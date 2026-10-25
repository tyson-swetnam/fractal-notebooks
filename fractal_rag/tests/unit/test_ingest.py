"""Unit tests for the ingest orchestrator with the DryRunWriter."""

from __future__ import annotations

import json
from pathlib import Path

import nbformat
import pytest

from fractal_rag.config import Settings
from fractal_rag.ingest import DryRunWriter, run_ingest
from fractal_rag.parsers import RawDocument


@pytest.fixture
def fixtures(tmp_path: Path) -> Settings:
    """Build a tiny corpus and override Settings.corpus_root / repo_root."""
    corpus = tmp_path / "corpus"
    repo = tmp_path / "repo"
    (corpus / "embeddings").mkdir(parents=True)
    (corpus / "notebooks").mkdir(parents=True)
    (repo / "docs").mkdir(parents=True)

    # JSONL fixture — 2 records
    jsonl = corpus / "embeddings" / "fake.jsonl"
    with jsonl.open("w") as f:
        for i in range(2):
            f.write(
                json.dumps(
                    {
                        "id": f"ark://x/{i}",
                        "doi": f"10.0/test.{i}",
                        "title": f"Mandelbrot set study {i}",
                        "creator": ["A"],
                        "publicationYear": 2024,
                        "isPartOf": "J",
                        "wordCount": 10,
                        "keyphrase": ["fractal dimension"],
                        "unigramCount": {"fractal": 5},
                        "bigramCount": {"fractal dimension": 3},
                    }
                )
                + "\n"
            )

    # Notebook fixture
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        nbformat.v4.new_markdown_cell("# Notebook\n\nDiscusses Julia Set extensively."),
        nbformat.v4.new_code_cell("print('hi')"),
    ]
    nbformat.write(nb, (corpus / "notebooks" / "demo.ipynb").open("w"))

    # Markdown fixture under repo/docs
    (repo / "docs" / "intro.md").write_text("# Intro\n\nHausdorff dimension is key.")

    return Settings(
        corpus_root=corpus,
        repo_root=repo,
        chunk_max_tokens=500,
        chunk_overlap_tokens=50,
        cache_dir=tmp_path / "cache",
    )


def test_dry_run_ingests_all_sources(fixtures: Settings) -> None:
    writer = DryRunWriter()
    report = run_ingest(
        ["json", "notebooks", "docs", "pdfs"],
        writer,
        settings=fixtures,
    )

    by_source = {r.source: r for r in report.runs}
    assert by_source["concepts"].concepts_upserted >= 20
    assert by_source["json"].parsed_docs == 2
    assert by_source["notebooks"].parsed_docs == 2  # md + code cells
    assert by_source["docs"].parsed_docs == 1
    # PDFs source returns no docs (no fixtures), but the source ran.
    assert "pdfs" in by_source

    # Every parsed doc produces anchor + ≥1 sub-chunk.
    assert by_source["json"].inserted_chunks >= 4
    assert by_source["json"].failed_chunks == 0


def test_dry_run_attaches_concept_uuids(fixtures: Settings) -> None:
    writer = DryRunWriter()
    run_ingest(["docs"], writer, settings=fixtures)
    assert writer.concepts, "concepts pass produced no UUIDs"
    # Hausdorff Dimension is in seed and mentioned in fixture markdown.
    assert "Hausdorff Dimension" in writer.concepts


def test_state_file_written(fixtures: Settings) -> None:
    writer = DryRunWriter()
    run_ingest(["docs"], writer, settings=fixtures)
    state = json.loads(fixtures.state_path.read_text())
    assert "runs" in state
    sources_run = {r["source"] for r in state["runs"]}
    assert {"concepts", "docs"} <= sources_run


def test_one_bad_document_is_recorded_and_skipped(fixtures: Settings, monkeypatch) -> None:
    """A document whose chunking raises is counted in failed_docs; the rest of the source survives."""
    import fractal_rag.ingest as ingest_mod

    real_chunk_document = ingest_mod.chunk_document

    def flaky_chunk_document(doc: RawDocument, settings=None):
        if doc.title == "Mandelbrot set study 1":
            raise KeyError("simulated chunker bug")
        return real_chunk_document(doc, settings=settings)

    monkeypatch.setattr(ingest_mod, "chunk_document", flaky_chunk_document)
    writer = DryRunWriter()
    report = run_ingest(["json"], writer, settings=fixtures)
    stats = {r.source: r for r in report.runs}["json"]
    assert stats.parsed_docs == 2
    assert stats.failed_docs == 1
    assert stats.inserted_chunks >= 2  # the good document was fully ingested
    assert stats.failed_chunks == 0
    assert all(uri != "ark://x/1" for uri, _ in writer.artifacts)
    failures = [json.loads(line) for line in fixtures.failed_objects_path.read_text().splitlines()]
    assert len(failures) == 1
    assert failures[0]["kind"] == "document"
    assert failures[0]["source_uri"] == "ark://x/1"
    assert "simulated chunker bug" in failures[0]["error"]


# ---------------------------------------------------------------------------
# Source discovery (ingest.discover_markdown / discover_notebooks)

from fractal_rag.ingest import (  # noqa: E402
    discover_markdown,
    discover_notebooks,
    parse_source,
    site_exclude_spec,
)

ZENSICAL_TOML = """\
[project]
site_name = "Fractal Self-Affinity in Nature"
site_url = "https://tyson-swetnam.github.io/fractal-notebooks"
exclude_docs = \"\"\"
*.ipynb
*.py
README.md
PLAN*.md
/notebooks/3dep/
/superpowers/
\"\"\"
draft_docs = \"\"\"
drafts/
\"\"\"
"""


def _touch(path: Path, text: str = "# Page\n\nBody.\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _write_nb(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_markdown_cell("# Nb\n\nMandelbrot set.")]
    nbformat.write(nb, path.open("w"))
    return path


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A repo checkout with the site config and every exclusion case."""
    root = tmp_path / "repo"
    docs = root / "docs"
    root.mkdir()
    (root / "zensical.toml").write_text(ZENSICAL_TOML, encoding="utf-8")
    # kept
    _touch(docs / "index.md")
    _touch(docs / "foundations" / "history.md")
    _touch(docs / "notebooks" / "research.md")
    _touch(docs / "okf" / "index.md")  # hand-written "Knowledge bundles" page, a real nav page
    # skipped: change logs (any depth)
    _touch(docs / "log.md")
    # skipped: dot-prefixed path parts
    _touch(docs / ".claude" / "agents" / "x.md")
    _touch(docs / "foundations" / ".hidden.md")
    # skipped: extracted-output directories
    _touch(docs / "notebooks" / "foundations" / "dla_files" / "note.md")
    # skipped: build-time copies of the OKF bundles (only concepts/ and proofs/)
    _touch(docs / "okf" / "concepts" / "index.md")
    _touch(docs / "okf" / "concepts" / "geometry" / "fractal.md")
    _touch(docs / "okf" / "proofs" / "cantor-set-dimension.md")
    # skipped: exclude_docs / draft_docs patterns from zensical.toml
    _touch(docs / "notebooks" / "3dep" / "README.md")
    _touch(docs / "notebooks" / "3dep" / "original" / "page.md")
    _touch(docs / "README.md")
    _touch(docs / "PLAN_notes.md")
    _touch(docs / "superpowers" / "specs" / "spec.md")
    _touch(docs / "drafts" / "wip.md")
    # skipped: rendered notebook page next to its .ipynb
    _touch(docs / "notebooks" / "foundations" / "dla.md")
    _write_nb(docs / "notebooks" / "foundations" / "dla.ipynb")
    # skipped: empty file
    _touch(docs / "applications" / "empty.md", "")
    # canonical OKF bundles at the repo root: indexed (except their change logs)
    _touch(root / "okf" / "concepts" / "index.md", '---\nokf_version: "0.2"\n---\n\n# Concepts\n')
    _touch(root / "okf" / "concepts" / "geometry" / "fractal.md")
    _touch(root / "okf" / "concepts" / "log.md", "# Concept Bundle Update Log\n\n## 2026-10-24\n* **Update**: x.\n")
    _touch(root / "okf" / "proofs" / "cantor-set-dimension.md")
    _touch(root / "okf" / "proofs" / "log.md", "# Proof Bundle Change Log\n\n## 2026-10-24\n* **Update**: x.\n")
    _touch(root / "okf" / "README.md")  # not part of a bundle
    return root


def test_site_exclude_spec_reads_exclude_and_draft_docs(repo: Path, tmp_path: Path) -> None:
    spec = site_exclude_spec(repo)
    assert spec is not None
    assert spec.match_file("notebooks/3dep/original/page.md")
    assert spec.match_file("README.md") and spec.match_file("notebooks/3dep/README.md")
    assert spec.match_file("drafts/wip.md")
    assert not spec.match_file("foundations/history.md")
    assert site_exclude_spec(tmp_path / "nowhere") is None
    bare = tmp_path / "bare"
    bare.mkdir()
    (bare / "zensical.toml").write_text('[project]\nsite_name = "x"\n', encoding="utf-8")
    assert site_exclude_spec(bare) is None


def test_discover_markdown_applies_every_exclusion(repo: Path) -> None:
    found = [p.relative_to(repo).as_posix() for p in discover_markdown(repo)]
    assert found == [
        "docs/foundations/history.md",
        "docs/index.md",
        "docs/notebooks/research.md",
        "docs/okf/index.md",
        "okf/concepts/geometry/fractal.md",
        "okf/concepts/index.md",
        "okf/proofs/cantor-set-dimension.md",
    ]


def test_discover_markdown_without_zensical_toml_keeps_builtin_rules(repo: Path) -> None:
    (repo / "zensical.toml").unlink()
    found = {p.relative_to(repo).as_posix() for p in discover_markdown(repo)}
    # exclude_docs patterns no longer apply ...
    assert "docs/README.md" in found and "docs/notebooks/3dep/original/page.md" in found
    # ... but the built-in rules still do
    assert not any(".claude" in f or "_files/" in f for f in found)
    assert not any(f.startswith(("docs/okf/concepts/", "docs/okf/proofs/")) for f in found)
    assert "docs/okf/index.md" in found
    assert not any(f.endswith("log.md") for f in found)  # docs/log.md, okf/*/log.md
    assert "docs/notebooks/foundations/dla.md" not in found
    assert "docs/applications/empty.md" not in found


def test_discover_markdown_on_missing_repo_root_yields_nothing(tmp_path: Path) -> None:
    assert discover_markdown(tmp_path / "does-not-exist") == []


def test_discover_notebooks_scans_docs_and_dedupes(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    repo = tmp_path / "repo"
    docs = repo / "docs"
    in_corpus = _write_nb(corpus / "notebooks" / "demo.ipynb")
    _write_nb(corpus / "notebooks" / ".ipynb_checkpoints" / "demo-checkpoint.ipynb")
    in_docs = _write_nb(docs / "notebooks" / "foundations" / "fractals.ipynb")
    _write_nb(docs / "notebooks" / "foundations" / ".ipynb_checkpoints" / "fractals-checkpoint.ipynb")
    _write_nb(docs / "notebooks" / "3dep" / "modified" / "sites" / "harvard_forest" / "chm_harvard_forest.ipynb")
    kept_3dep = _write_nb(docs / "notebooks" / "3dep" / "modified" / "chm_forest_sites.ipynb")
    # the iRODS mirror also holds a copy of a repo notebook (symlink -> same resolved path)
    (corpus / "mirror").mkdir()
    (corpus / "mirror" / "fractals.ipynb").symlink_to(in_docs)

    found = discover_notebooks(corpus, repo)
    resolved = sorted(p.resolve() for p in found)
    assert resolved == sorted(p.resolve() for p in (in_corpus, in_docs, kept_3dep))
    assert len(found) == 3  # the symlinked duplicate was dropped

    # without a repo root only the corpus is scanned (legacy behaviour)
    legacy = discover_notebooks(corpus)
    assert {p.resolve() for p in legacy} == {in_corpus.resolve(), in_docs.resolve()}


def test_discover_notebooks_dedupes_mirrored_copies_by_content(tmp_path: Path) -> None:
    """A byte-identical copy in the corpus (not a symlink) is indexed once, from the repo."""
    corpus = tmp_path / "corpus"
    repo = tmp_path / "repo"
    in_docs = _write_nb(repo / "docs" / "notebooks" / "foundations" / "fractals.ipynb")
    mirrored = corpus / "mirror" / "docs" / "notebooks" / "foundations" / "fractals.ipynb"
    mirrored.parent.mkdir(parents=True)
    mirrored.write_bytes(in_docs.read_bytes())
    # same file name, different content: a genuinely different notebook, kept
    other = corpus / "elsewhere" / "fractals.ipynb"
    other.parent.mkdir(parents=True)
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_markdown_cell("# Other\n\nKoch curve.")]
    nbformat.write(nb, other.open("w"))

    found = discover_notebooks(corpus, repo)
    assert sorted(p.resolve() for p in found) == sorted(p.resolve() for p in (in_docs, other))
    assert in_docs in found and mirrored not in found  # the repo copy wins


def test_parse_source_notebooks_uses_repo_docs(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    repo = tmp_path / "repo"
    _write_nb(repo / "docs" / "notebooks" / "foundations" / "fractals.ipynb")
    settings = Settings(corpus_root=corpus, repo_root=repo, cache_dir=tmp_path / "cache")
    docs = list(parse_source("notebooks", settings=settings))
    assert len(docs) == 1
    assert docs[0].metadata["notebook_title"] == "Nb"


def test_parse_source_docs_carries_resource(repo: Path, tmp_path: Path) -> None:
    page = repo / "docs" / "foundations" / "history.md"
    page.write_text(
        "---\ntype: Chapter\ntitle: Chapter 1\ndescription: d\n"
        "resource: https://tyson-swetnam.github.io/fractal-notebooks/foundations/history/\n"
        "tags: [foundations]\nstatus: stable\n---\n\n# History\n\nHausdorff dimension.\n",
        encoding="utf-8",
    )
    settings = Settings(corpus_root=tmp_path / "corpus", repo_root=repo, cache_dir=tmp_path / "cache")
    docs = {d.metadata["path"]: d for d in parse_source("docs", settings=settings)}
    history = docs[str(page)]
    assert history.title == "Chapter 1"
    assert history.metadata["resource"].endswith("/foundations/history/")
    assert history.metadata["tags"] == ["foundations"]
    # the dry-run writer path still works end to end with the new discovery rules
    writer = DryRunWriter()
    report = run_ingest(["docs"], writer, settings=settings)
    assert {r.source: r.parsed_docs for r in report.runs}["docs"] == 7
