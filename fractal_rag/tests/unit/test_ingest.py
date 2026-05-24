"""Unit tests for the ingest orchestrator with the DryRunWriter."""

from __future__ import annotations

import json
from pathlib import Path

import nbformat
import pytest

from fractal_rag.config import Settings
from fractal_rag.ingest import DryRunWriter, run_ingest


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
