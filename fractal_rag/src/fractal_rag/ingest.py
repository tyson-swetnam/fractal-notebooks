"""End-to-end ingest orchestrator.

Pipeline per source:
    discover files -> parse -> chunk -> enrich -> two-pass batch import.

Two-pass import:
  1. Upload all Concept records (idempotent on name) and remember UUIDs.
  2. Upload FractalArtifact chunks; attach ``concepts`` cross-refs in the
     same pass using the UUIDs from step 1.

Failures land in ``~/.cache/fractal-rag/failed_objects.jsonl`` so they can be
re-tried without re-parsing the corpus. Resume state lives in
``~/.cache/fractal-rag/state.json``.
"""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from .chunk import Chunk, chunk_document
from .concepts.loader import ConceptRecord, load_seed
from .config import Settings, get_settings
from .enrich import ConceptIndex, aggregate_doc_concepts, enrich
from .parsers import RawDocument

log = logging.getLogger("fractal_rag.ingest")


# ---------------------------------------------------------------------------
# Source discovery


def discover_notebooks(corpus_root: Path) -> list[Path]:
    return sorted(
        p
        for p in corpus_root.rglob("*.ipynb")
        if ".ipynb_checkpoints" not in p.parts
    )


def discover_markdown(repo_root: Path) -> list[Path]:
    return sorted(
        p
        for p in (repo_root / "docs").rglob("*.md")
        if p.stat().st_size > 0
    )


def discover_pdfs(corpus_root: Path) -> list[Path]:
    return sorted(corpus_root.rglob("*.pdf"))


def discover_jsonl(corpus_root: Path) -> list[Path]:
    return sorted(p for p in corpus_root.rglob("*.jsonl") if "embeddings" in p.parts)


# ---------------------------------------------------------------------------
# Parsing dispatch


def parse_source(
    source: str,
    *,
    settings: Settings,
    limit: int | None = None,
) -> Iterator[RawDocument]:
    """Yield RawDocuments for one of {json, notebooks, docs, pdfs}."""
    if source == "json":
        from .parsers.json_corpus import parse_jsonl

        for path in discover_jsonl(settings.corpus_root):
            yield from parse_jsonl(path, limit=limit)

    elif source == "notebooks":
        from .parsers.notebook import parse_notebook

        for path in discover_notebooks(settings.corpus_root):
            yield from parse_notebook(path)

    elif source == "docs":
        from .parsers.markdown import parse_markdown

        for path in discover_markdown(settings.repo_root):
            yield from parse_markdown(path)

    elif source == "pdfs":
        from .parsers.pdf import parse_pdf

        for path in discover_pdfs(settings.corpus_root):
            yield from parse_pdf(path)

    else:
        raise ValueError(f"unknown source {source!r}")


# ---------------------------------------------------------------------------
# Writer abstraction — concrete impl uses Weaviate; tests substitute a fake.


class ArtifactWriter(Protocol):
    def upsert_concept(self, record: ConceptRecord) -> str: ...
    def insert_artifact(self, chunk: Chunk, concept_uuids: list[str]) -> str: ...
    def count(self, collection: str) -> int: ...


@dataclass
class IngestStats:
    source: str
    parsed_docs: int = 0
    emitted_chunks: int = 0
    inserted_chunks: int = 0
    failed_chunks: int = 0
    concepts_upserted: int = 0
    started_at: str = ""
    finished_at: str = ""


@dataclass
class IngestReport:
    runs: list[IngestStats] = field(default_factory=list)

    def add(self, stats: IngestStats) -> None:
        self.runs.append(stats)

    def to_dict(self) -> dict[str, Any]:
        return {"runs": [stats.__dict__ for stats in self.runs]}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _record_failure(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


# ---------------------------------------------------------------------------
# Orchestrator


def run_ingest(
    sources: list[str],
    writer: ArtifactWriter,
    *,
    settings: Settings | None = None,
    seed_concepts: list[ConceptRecord] | None = None,
    limit_per_source: int | None = None,
) -> IngestReport:
    """Two-pass ingest: concepts first, then artifacts with cross-refs."""
    s = settings or get_settings()
    seeds = seed_concepts or load_seed(settings=s)
    index = ConceptIndex.build(seeds)
    report = IngestReport()

    # ----- Pass 1: concepts
    concept_uuid_by_name: dict[str, str] = {}
    concept_stats = IngestStats(source="concepts", started_at=_now())
    for rec in seeds:
        try:
            cuid = writer.upsert_concept(rec)
            concept_uuid_by_name[rec.name] = cuid
            concept_stats.concepts_upserted += 1
        except Exception as exc:  # noqa: BLE001
            log.error("concept upsert failed for %s: %s", rec.name, exc)
            _record_failure(
                s.failed_objects_path,
                {
                    "kind": "concept",
                    "name": rec.name,
                    "error": str(exc),
                    "at": _now(),
                },
            )
            concept_stats.failed_chunks += 1
    concept_stats.finished_at = _now()
    report.add(concept_stats)

    # ----- Pass 2: per-source artifact ingest
    for source in sources:
        stats = IngestStats(source=source, started_at=_now())
        try:
            doc_iter = parse_source(source, settings=s, limit=limit_per_source)
        except ImportError as exc:
            log.warning("skipping %s: %s", source, exc)
            stats.finished_at = _now()
            report.add(stats)
            continue

        for doc in doc_iter:
            stats.parsed_docs += 1
            chunks = chunk_document(doc, settings=s)
            for c in chunks:
                enrich(c, index)
            doc_concepts = aggregate_doc_concepts(chunks)
            # Attach the doc-level concept union to the anchor (chunk_index=-1)
            if chunks and chunks[0].chunk_index == -1:
                chunks[0].metadata["concepts"] = doc_concepts

            for c in chunks:
                stats.emitted_chunks += 1
                names = c.metadata.get("concepts") or []
                concept_uuids = [
                    concept_uuid_by_name[n] for n in names if n in concept_uuid_by_name
                ]
                try:
                    writer.insert_artifact(c, concept_uuids)
                    stats.inserted_chunks += 1
                except Exception as exc:  # noqa: BLE001
                    log.error(
                        "artifact insert failed for %s chunk=%d: %s",
                        c.parent_uri,
                        c.chunk_index,
                        exc,
                    )
                    stats.failed_chunks += 1
                    _record_failure(
                        s.failed_objects_path,
                        {
                            "kind": "artifact",
                            "parent_uri": c.parent_uri,
                            "chunk_index": c.chunk_index,
                            "source_type": c.source_type,
                            "error": str(exc),
                            "at": _now(),
                        },
                    )

        stats.finished_at = _now()
        report.add(stats)

    # Persist a small state file so reruns can show last-run summary.
    s.state_path.parent.mkdir(parents=True, exist_ok=True)
    s.state_path.write_text(json.dumps(report.to_dict(), indent=2))
    return report


# ---------------------------------------------------------------------------
# Weaviate-backed writer


class WeaviateWriter:
    """Concrete ArtifactWriter that targets a live Weaviate v4 client."""

    def __init__(self, client: Any, settings: Settings | None = None) -> None:
        self._client = client
        self._s = settings or get_settings()
        self._concepts = client.collections.get(self._s.concept_collection)
        self._artifacts = client.collections.get(self._s.artifact_collection)

    @staticmethod
    def _concept_uuid(name: str) -> str:
        # Deterministic UUID from canonical name so upserts are idempotent.
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"concept:{name.lower()}"))

    @staticmethod
    def _artifact_uuid(parent_uri: str, chunk_index: int) -> str:
        return str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"artifact:{parent_uri}#chunk={chunk_index}",
            )
        )

    def upsert_concept(self, record: ConceptRecord) -> str:
        cuid = self._concept_uuid(record.name)
        properties = {
            "name": record.name,
            "aliases": list(record.aliases),
            "definition": record.definition,
            "domain": list(record.domain),
            "hausdorff_dim_range": list(record.hausdorff_dim_range),
            "related_concept_ids": [],
        }
        if self._concepts.data.exists(cuid):
            self._concepts.data.update(uuid=cuid, properties=properties)
        else:
            self._concepts.data.insert(properties=properties, uuid=cuid)
        return cuid

    def insert_artifact(self, chunk: Chunk, concept_uuids: list[str]) -> str:
        auid = self._artifact_uuid(chunk.parent_uri, chunk.chunk_index)
        properties = {
            "source_type": chunk.source_type,
            "source_uri": chunk.parent_uri,
            "parent_id": chunk.parent_uri,
            "chunk_index": chunk.chunk_index,
            "title": chunk.title,
            "summary": chunk.summary,
            "content": chunk.content,
            "authors": chunk.authors,
            "year": chunk.year,
            "latex_equations": chunk.latex_equations,
            "figure_refs": chunk.figure_refs,
            "tags": chunk.tags,
            "ingested_at": _now(),
        }
        references = {"concepts": concept_uuids} if concept_uuids else None
        if self._artifacts.data.exists(auid):
            self._artifacts.data.update(uuid=auid, properties=properties, references=references)
        else:
            self._artifacts.data.insert(
                properties=properties, uuid=auid, references=references
            )
        return auid

    def count(self, collection: str) -> int:
        coll = self._client.collections.get(collection)
        return coll.aggregate.over_all(total_count=True).total_count


# ---------------------------------------------------------------------------
# Convenience: dry-run writer that just counts and prints — never touches net.


class DryRunWriter:
    def __init__(self) -> None:
        self.concepts: dict[str, str] = {}
        self.artifacts: list[tuple[str, int]] = []

    def upsert_concept(self, record: ConceptRecord) -> str:
        cuid = WeaviateWriter._concept_uuid(record.name)
        self.concepts[record.name] = cuid
        return cuid

    def insert_artifact(self, chunk: Chunk, concept_uuids: list[str]) -> str:
        self.artifacts.append((chunk.parent_uri, chunk.chunk_index))
        return WeaviateWriter._artifact_uuid(chunk.parent_uri, chunk.chunk_index)

    def count(self, collection: str) -> int:
        if collection.endswith("Concept"):
            return len(self.concepts)
        return len(self.artifacts)
