"""Hierarchical, token-aware chunker.

Splits a :class:`RawDocument` into chunks of ~``chunk_max_tokens`` tokens with
``chunk_overlap_tokens`` of overlap. Chunks are produced by walking sentences
and packing them into a token budget; long sentences are split on whitespace
as a fallback so we never emit oversized chunks.

A doc-level "anchor" chunk with ``chunk_index=-1`` is always emitted first.
It carries the parent's title and a one-line summary so doc-level queries
(e.g. "what notebook discusses X?") still hit the artifact via title_vec /
summary_vec without depending on which sub-chunk happened to win retrieval.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .config import Settings, get_settings
from .parsers import RawDocument


_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[\"'$])")
_WS = re.compile(r"\s+")


@dataclass
class Chunk:
    """A token-budgeted slice of a RawDocument."""

    parent_uri: str
    chunk_index: int
    source_type: str
    title: str
    content: str
    summary: str = ""
    latex_equations: list[str] = field(default_factory=list)
    figure_refs: list[str] = field(default_factory=list)
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def _approx_tokens(text: str) -> int:
    """Cheap token estimate: ~4 chars per token (English heuristic).

    A real BPE tokenizer would be more accurate but adds a heavy dependency
    (transformers). For ingestion-time chunking this estimate is fine — we
    set chunk_max_tokens=500 and the embedding model's window is 8192.
    """
    return max(1, (len(text) + 3) // 4)


def _split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    parts = _SENTENCE_BOUNDARY.split(text)
    out: list[str] = []
    for part in parts:
        part = part.strip()
        if part:
            out.append(part)
    return out or [text]


def _split_long_sentence(sentence: str, max_tokens: int) -> list[str]:
    if _approx_tokens(sentence) <= max_tokens:
        return [sentence]
    words = sentence.split()
    pieces: list[str] = []
    cur: list[str] = []
    cur_tokens = 0
    for w in words:
        wt = _approx_tokens(w + " ")
        if cur and cur_tokens + wt > max_tokens:
            pieces.append(" ".join(cur))
            cur = [w]
            cur_tokens = wt
        else:
            cur.append(w)
            cur_tokens += wt
    if cur:
        pieces.append(" ".join(cur))
    return pieces


def _pack_sentences(sentences: list[str], max_tokens: int, overlap_tokens: int) -> list[str]:
    """Pack sentences into chunks, then add overlap from the prior chunk's tail."""
    bucketed: list[list[str]] = []
    cur: list[str] = []
    cur_tokens = 0
    for raw in sentences:
        for sentence in _split_long_sentence(raw, max_tokens):
            st = _approx_tokens(sentence)
            if cur and cur_tokens + st > max_tokens:
                bucketed.append(cur)
                cur = []
                cur_tokens = 0
            cur.append(sentence)
            cur_tokens += st
    if cur:
        bucketed.append(cur)

    if overlap_tokens <= 0 or len(bucketed) <= 1:
        return [" ".join(b) for b in bucketed]

    chunks: list[str] = []
    for i, bucket in enumerate(bucketed):
        if i == 0:
            chunks.append(" ".join(bucket))
            continue
        prev = bucketed[i - 1]
        # Walk previous chunk from end backwards until we hit overlap_tokens.
        tail: list[str] = []
        tail_tokens = 0
        for sentence in reversed(prev):
            st = _approx_tokens(sentence)
            if tail_tokens + st > overlap_tokens and tail:
                break
            tail.insert(0, sentence)
            tail_tokens += st
            if tail_tokens >= overlap_tokens:
                break
        chunks.append(" ".join(tail + bucket))
    return chunks


def _normalize(text: str) -> str:
    return _WS.sub(" ", text).strip()


def chunk_document(doc: RawDocument, settings: Settings | None = None) -> list[Chunk]:
    """Split a document into anchor + sub-chunks."""
    s = settings or get_settings()
    sentences = _split_sentences(doc.content)
    sub_texts = _pack_sentences(sentences, s.chunk_max_tokens, s.chunk_overlap_tokens) or [
        doc.content
    ]

    first_sentence = sentences[0] if sentences else doc.content.strip()
    doc_summary = _normalize(first_sentence)[:400]

    tags = list(doc.metadata.get("tags") or [])

    anchor = Chunk(
        parent_uri=doc.source_uri,
        chunk_index=-1,
        source_type=doc.source_type,
        title=doc.title,
        content=doc.content,
        summary=doc_summary,
        latex_equations=list(doc.latex_equations),
        figure_refs=list(doc.figure_refs),
        authors=list(doc.authors),
        year=doc.year,
        tags=tags,
        metadata=dict(doc.metadata),
    )

    chunks: list[Chunk] = [anchor]
    for i, body in enumerate(sub_texts):
        chunks.append(
            Chunk(
                parent_uri=doc.source_uri,
                chunk_index=i,
                source_type=doc.source_type,
                title=f"{doc.title} [{i + 1}/{len(sub_texts)}]" if len(sub_texts) > 1 else doc.title,
                content=body,
                summary=_normalize(body)[:200],
                latex_equations=[],
                figure_refs=[],
                authors=list(doc.authors),
                year=doc.year,
                tags=tags,
                metadata=dict(doc.metadata),
            )
        )
    return chunks
