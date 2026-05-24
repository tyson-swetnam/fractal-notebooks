"""Concept tagging and summary heuristic.

A pre-compiled regex (longest-alias-first, case-insensitive, word-boundary)
walks chunk content and produces the set of concept names that appear. We
also pick a better summary than the chunk's first sentence by preferring
the sentence with the strongest concept density.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .chunk import Chunk
from .concepts.loader import ConceptRecord


_SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[\"'$])")


@dataclass
class ConceptIndex:
    """Pre-compiled matcher for the concept seed."""

    records: list[ConceptRecord]
    pattern: re.Pattern[str]
    term_to_name: dict[str, str]

    @classmethod
    def build(cls, records: list[ConceptRecord]) -> ConceptIndex:
        term_to_name: dict[str, str] = {}
        for r in records:
            for term in r.match_terms:
                # Longest-first ordering ensures "fractal dimension" maps before "fractal".
                term_to_name.setdefault(term, r.name)

        terms_sorted = sorted(term_to_name.keys(), key=len, reverse=True)
        escaped = [re.escape(t) for t in terms_sorted]
        pattern = re.compile(
            r"\b(?:" + "|".join(escaped) + r")\b",
            flags=re.IGNORECASE,
        )
        return cls(records=records, pattern=pattern, term_to_name=term_to_name)

    def tag(self, text: str) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for match in self.pattern.finditer(text):
            name = self.term_to_name.get(match.group(0).lower())
            if name and name not in seen:
                seen.add(name)
                ordered.append(name)
        return ordered

    def best_summary(self, text: str, fallback: str) -> str:
        sentences = [s.strip() for s in _SENTENCE.split(text.strip()) if s.strip()]
        if not sentences:
            return fallback
        first = sentences[0]
        scored = [(s, len(self.tag(s))) for s in sentences[1:]]
        if not scored:
            return first[:300]
        best, hits = max(scored, key=lambda kv: kv[1])
        if hits > 0:
            return f"{first} {best}"[:400]
        return first[:300]


def enrich(chunk: Chunk, index: ConceptIndex) -> Chunk:
    """Annotate a chunk with discovered concepts and an improved summary."""
    concepts = index.tag(chunk.content)
    chunk.metadata = dict(chunk.metadata)
    chunk.metadata["concepts"] = concepts
    if chunk.chunk_index == -1:
        chunk.summary = index.best_summary(chunk.content, chunk.summary)
    return chunk


def aggregate_doc_concepts(chunks: list[Chunk]) -> list[str]:
    """Union of concepts across a doc's sub-chunks (preserving order)."""
    seen: set[str] = set()
    out: list[str] = []
    for c in chunks:
        for name in c.metadata.get("concepts", []) or []:
            if name not in seen:
                seen.add(name)
                out.append(name)
    return out
