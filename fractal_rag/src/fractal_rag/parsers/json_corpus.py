"""Parser for the Constellate-style JSONL article export.

Source shape (from ``embeddings/constellate_fractals.jsonl`` on iRODS):
50K scholarly articles with title, creators, DOI, publication year, journal,
keyphrases, and unigram/bigram/trigram frequency dicts. **No full text**, so
we synthesize a content blob from title + keyphrases + top n-grams.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

from . import RawDocument


def _top_terms(counts: dict[str, int] | None, k: int) -> list[str]:
    if not counts:
        return []
    return [t for t, _ in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:k]]


def _synthesize_content(record: dict) -> str:
    """Synthesize searchable text from the article's structured fields."""
    parts: list[str] = []
    title = (record.get("title") or "").strip()
    if title:
        parts.append(title)
    journal = (record.get("isPartOf") or "").strip()
    if journal:
        parts.append(f"Published in: {journal}")
    keyphrases = record.get("keyphrase") or []
    if keyphrases:
        parts.append("Keyphrases: " + ", ".join(keyphrases))
    top_uni = _top_terms(record.get("unigramCount"), 40)
    if top_uni:
        parts.append("Top terms: " + ", ".join(top_uni))
    top_bi = _top_terms(record.get("bigramCount"), 20)
    if top_bi:
        parts.append("Top bigrams: " + ", ".join(top_bi))
    return "\n\n".join(parts)


def _doi_or_id(record: dict) -> str:
    doi = (record.get("doi") or "").strip()
    if doi:
        return f"doi:{doi}"
    return record.get("id") or "<unknown>"


def parse_jsonl(path: Path, *, limit: int | None = None) -> Iterator[RawDocument]:
    """Yield one RawDocument per JSONL record.

    Streams the file to keep memory bounded — the production corpus is ~17 GB.
    """
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit is not None and i >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            uri = _doi_or_id(record)
            title = (record.get("title") or "").strip() or uri
            year = record.get("publicationYear")
            authors = list(record.get("creator") or [])
            content = _synthesize_content(record)
            if not content.strip():
                continue

            yield RawDocument(
                source_type="json_corpus",
                source_uri=uri,
                title=title,
                content=content,
                year=int(year) if isinstance(year, int) else None,
                authors=authors,
                metadata={
                    "doi": record.get("doi"),
                    "journal": record.get("isPartOf"),
                    "publisher": record.get("publisher"),
                    "docType": record.get("docType"),
                    "url": record.get("url"),
                    "word_count": record.get("wordCount"),
                    "keyphrases": record.get("keyphrase") or [],
                    "tdm_category": record.get("tdmCategory") or [],
                    "constellate_id": record.get("id"),
                },
            )


def parse_file(path: Path, *, limit: int | None = None) -> list[RawDocument]:
    """Eager-list wrapper around :func:`parse_jsonl`."""
    return list(parse_jsonl(path, limit=limit))
