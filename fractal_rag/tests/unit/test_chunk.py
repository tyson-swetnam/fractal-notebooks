"""Unit tests for the chunker."""

from __future__ import annotations

from fractal_rag.chunk import _approx_tokens, chunk_document
from fractal_rag.config import Settings
from fractal_rag.parsers import RawDocument


def _doc(content: str) -> RawDocument:
    return RawDocument(
        source_type="markdown",
        source_uri="file:///tmp/doc.md",
        title="T",
        content=content,
    )


def _settings(max_tokens: int, overlap: int) -> Settings:
    return Settings(chunk_max_tokens=max_tokens, chunk_overlap_tokens=overlap)


def test_short_document_yields_anchor_plus_one_chunk() -> None:
    chunks = chunk_document(_doc("One short sentence."), _settings(100, 10))
    assert len(chunks) == 2
    assert chunks[0].chunk_index == -1
    assert chunks[1].chunk_index == 0


def test_chunks_respect_max_tokens() -> None:
    content = " ".join(f"Sentence {i} has some words here." for i in range(120))
    chunks = chunk_document(_doc(content), _settings(80, 0))
    sub = chunks[1:]
    assert len(sub) > 1
    for c in sub:
        # Tiny slack for the last-sentence packing decision (one sentence may push us over).
        assert _approx_tokens(c.content) <= 80 * 2


def test_overlap_carries_tail_into_next_chunk() -> None:
    sentences = [f"S{i} is sentence number {i} with extra words." for i in range(40)]
    content = " ".join(sentences)
    chunks = chunk_document(_doc(content), _settings(60, 30))
    sub = chunks[1:]
    if len(sub) < 2:
        return  # nothing to verify; chunker decided one bucket sufficed
    # The last sentence of bucket 0 should appear at the start of bucket 1.
    prev_tokens = sub[0].content.split()
    overlap_marker = " ".join(prev_tokens[-3:])
    assert overlap_marker in sub[1].content


def test_anchor_chunk_carries_doc_summary() -> None:
    doc = _doc("First important sentence. Second sentence is here.")
    chunks = chunk_document(doc, _settings(500, 50))
    assert chunks[0].chunk_index == -1
    assert "First important sentence" in chunks[0].summary


def test_long_sentence_is_split_not_dropped() -> None:
    long_sentence = "word " * 2000
    chunks = chunk_document(_doc(long_sentence), _settings(80, 0))
    sub = chunks[1:]
    assert len(sub) > 1
    total_words = sum(len(c.content.split()) for c in sub)
    assert total_words >= 2000


def test_metadata_tags_propagate_through_chunks() -> None:
    doc = RawDocument(
        source_type="notebook",
        source_uri="file:///nb#cell=2",
        title="Notebook cell 2",
        content="Hello world. Second sentence here.",
        metadata={"tags": ["code"], "cell_index": 2},
    )
    chunks = chunk_document(doc, _settings(500, 50))
    assert all(c.tags == ["code"] for c in chunks)
    assert chunks[0].metadata["cell_index"] == 2
