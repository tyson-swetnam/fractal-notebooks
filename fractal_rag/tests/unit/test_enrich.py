"""Unit tests for the enricher."""

from __future__ import annotations

from fractal_rag.chunk import Chunk
from fractal_rag.concepts.loader import ConceptRecord, load_seed
from fractal_rag.enrich import ConceptIndex, aggregate_doc_concepts, enrich


def _index() -> ConceptIndex:
    return ConceptIndex.build(load_seed())


def _chunk(content: str, idx: int = 0) -> Chunk:
    return Chunk(
        parent_uri="doi:1.2/x",
        chunk_index=idx,
        source_type="json_corpus",
        title="t",
        content=content,
    )


def test_tagger_finds_concept_by_canonical_name() -> None:
    out = _index().tag("The Mandelbrot Set is a classic example.")
    assert "Mandelbrot Set" in out


def test_tagger_is_case_insensitive() -> None:
    out = _index().tag("the mandelbrot set, the julia set, and self-similar systems.")
    assert "Mandelbrot Set" in out
    assert "Julia Set" in out


def test_longest_alias_wins() -> None:
    records = [
        ConceptRecord(name="Fractal Dimension", aliases=(), definition="d", domain=()),
        ConceptRecord(name="Fractal", aliases=(), definition="d", domain=()),
    ]
    idx = ConceptIndex.build(records)
    out = idx.tag("Fractal dimension is more than just fractal.")
    assert "Fractal Dimension" in out


def test_word_boundaries_prevent_substring_matches() -> None:
    out = _index().tag("infractal is not a concept token.")
    assert "Fractal" not in out


def test_enrich_attaches_concepts_to_chunk_metadata() -> None:
    idx = _index()
    c = _chunk("Discussion of the Hausdorff dimension and the Mandelbrot set.")
    enrich(c, idx)
    assert set(c.metadata["concepts"]) >= {"Hausdorff Dimension", "Mandelbrot Set"}


def test_enrich_anchor_chooses_concept_rich_summary() -> None:
    idx = _index()
    content = (
        "Intro paragraph without any tagged terms here. "
        "Now we discuss the Hausdorff dimension and the box-counting dimension in depth."
    )
    anchor = Chunk(
        parent_uri="x",
        chunk_index=-1,
        source_type="markdown",
        title="t",
        content=content,
        summary="Intro paragraph without any tagged terms here.",
    )
    enrich(anchor, idx)
    assert "Hausdorff" in anchor.summary or "box-counting" in anchor.summary.lower()


def test_aggregate_doc_concepts_preserves_order_and_dedupes() -> None:
    idx = _index()
    chunks = [
        _chunk("Mandelbrot set and Julia set come first.", 0),
        _chunk("Now we revisit the Mandelbrot set and add the Cantor set.", 1),
    ]
    for c in chunks:
        enrich(c, idx)
    combined = aggregate_doc_concepts(chunks)
    assert combined[:3] == ["Mandelbrot Set", "Julia Set", "Cantor Set"]
    assert len(combined) == len(set(combined))
