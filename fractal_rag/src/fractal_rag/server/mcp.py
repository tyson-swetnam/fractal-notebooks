"""MCP server (stdio) for the fractal-rag retrieval surface.

Read-only by design: every tool either retrieves artifacts or aggregates the
existing index. Per the design spec §8.2 we expose eight tools with stable
JSON payload shapes so the consuming agent doesn't need to renegotiate after
schema tweaks.

Error contract (spec §8.3): tool errors carry a stable ``code`` string in
their message so the agent can branch on it programmatically:
    not_found, invalid_argument, weaviate_error, unsupported, internal_error
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP
from weaviate.classes.query import Filter, MetadataQuery

from ..client import client_session
from ..config import Settings, get_settings


def _err(code: str, message: str) -> str:
    return f"{code}: {message}"


def _bound_limit(s: Settings, limit: int | None) -> int:
    if limit is None:
        return s.mcp_default_limit
    return max(1, min(int(limit), s.mcp_max_limit))


def _artifact_row(obj: Any) -> dict[str, Any]:
    props = obj.properties or {}
    meta = getattr(obj, "metadata", None)
    distance = getattr(meta, "distance", None) if meta is not None else None
    return {
        "uuid": str(obj.uuid),
        "title": props.get("title"),
        "summary": props.get("summary"),
        "source_type": props.get("source_type"),
        "source_uri": props.get("source_uri"),
        "parent_id": props.get("parent_id"),
        "chunk_index": props.get("chunk_index"),
        "year": props.get("year"),
        "authors": props.get("authors"),
        "tags": props.get("tags"),
        "latex_equations": props.get("latex_equations"),
        "distance": distance,
    }


def _concept_row(obj: Any) -> dict[str, Any]:
    props = obj.properties or {}
    return {
        "uuid": str(obj.uuid),
        "name": props.get("name"),
        "aliases": props.get("aliases"),
        "definition": props.get("definition"),
        "domain": props.get("domain"),
        "hausdorff_dim_range": props.get("hausdorff_dim_range"),
    }


def build_server(settings: Settings | None = None) -> FastMCP:
    """Build the FastMCP server with the eight retrieval tools."""
    s = settings or get_settings()
    mcp = FastMCP(
        name="fractal-rag",
        instructions=(
            "Read-only retrieval over the Fractal Notebooks corpus "
            "(Constellate JSONL, Jupyter notebooks, MkDocs markdown). "
            "Use search_artifacts for general queries; near_artifact to "
            "expand around a hit; list_concepts and get_concept for the "
            "ontology; artifacts_by_concept to filter by tag; corpus_stats "
            "for aggregates."
        ),
    )

    # ----- Tool 1: search_artifacts
    @mcp.tool(
        name="search_artifacts",
        description=(
            "Hybrid vector + keyword search over FractalArtifact. "
            "target_vector ∈ {content_vec, title_vec, summary_vec}. "
            "source_types filters to a subset of {json_corpus, notebook, markdown, pdf}."
        ),
    )
    def search_artifacts(
        query: str,
        limit: int | None = None,
        target_vector: str = "content_vec",
        alpha: float = 0.5,
        source_types: list[str] | None = None,
        year_min: int | None = None,
        year_max: int | None = None,
    ) -> str:
        if not query or not query.strip():
            raise ValueError(_err("invalid_argument", "query must be non-empty"))
        if target_vector not in {"content_vec", "title_vec", "summary_vec"}:
            raise ValueError(_err("invalid_argument", f"unknown target_vector {target_vector!r}"))

        filters = []
        if source_types:
            filters.append(Filter.by_property("source_type").contains_any(list(source_types)))
        if year_min is not None:
            filters.append(Filter.by_property("year").greater_or_equal(int(year_min)))
        if year_max is not None:
            filters.append(Filter.by_property("year").less_or_equal(int(year_max)))
        combined_filter = filters[0] if len(filters) == 1 else (
            Filter.all_of(filters) if filters else None
        )

        with client_session(s) as client:
            try:
                coll = client.collections.get(s.artifact_collection)
                response = coll.query.hybrid(
                    query=query,
                    limit=_bound_limit(s, limit),
                    target_vector=target_vector,
                    alpha=alpha,
                    filters=combined_filter,
                    return_metadata=MetadataQuery(distance=True),
                )
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(_err("weaviate_error", str(exc))) from exc

        return json.dumps([_artifact_row(o) for o in response.objects], indent=2)

    # ----- Tool 2: get_artifact
    @mcp.tool(
        name="get_artifact",
        description="Fetch a single artifact by UUID, returning full content.",
    )
    def get_artifact(uuid: str) -> str:
        with client_session(s) as client:
            try:
                coll = client.collections.get(s.artifact_collection)
                obj = coll.query.fetch_object_by_id(uuid)
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(_err("weaviate_error", str(exc))) from exc
        if obj is None:
            raise ValueError(_err("not_found", f"artifact {uuid} not found"))
        full = _artifact_row(obj)
        full["content"] = (obj.properties or {}).get("content")
        return json.dumps(full, indent=2)

    # ----- Tool 3: near_artifact
    @mcp.tool(
        name="near_artifact",
        description="Find artifacts whose content_vec is closest to a given artifact.",
    )
    def near_artifact(uuid: str, limit: int | None = None) -> str:
        with client_session(s) as client:
            try:
                coll = client.collections.get(s.artifact_collection)
                response = coll.query.near_object(
                    near_object=uuid,
                    limit=_bound_limit(s, limit),
                    target_vector="content_vec",
                    return_metadata=MetadataQuery(distance=True),
                )
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(_err("weaviate_error", str(exc))) from exc
        return json.dumps([_artifact_row(o) for o in response.objects], indent=2)

    # ----- Tool 4: artifacts_by_concept
    @mcp.tool(
        name="artifacts_by_concept",
        description="List artifacts referencing a concept by canonical name.",
    )
    def artifacts_by_concept(name: str, limit: int | None = None) -> str:
        with client_session(s) as client:
            try:
                concept_coll = client.collections.get(s.concept_collection)
                hits = concept_coll.query.fetch_objects(
                    filters=Filter.by_property("name").equal(name),
                    limit=1,
                )
                if not hits.objects:
                    raise ValueError(_err("not_found", f"concept {name!r} not found"))
                concept_uuid = str(hits.objects[0].uuid)

                art_coll = client.collections.get(s.artifact_collection)
                response = art_coll.query.fetch_objects(
                    filters=Filter.by_ref("concepts").by_id().equal(concept_uuid),
                    limit=_bound_limit(s, limit),
                )
            except ValueError:
                raise
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(_err("weaviate_error", str(exc))) from exc

        return json.dumps([_artifact_row(o) for o in response.objects], indent=2)

    # ----- Tool 5: list_concepts
    @mcp.tool(
        name="list_concepts",
        description="List all Concept entries (optionally filtered by domain).",
    )
    def list_concepts(domain: str | None = None, limit: int | None = None) -> str:
        with client_session(s) as client:
            try:
                coll = client.collections.get(s.concept_collection)
                filt = (
                    Filter.by_property("domain").contains_any([domain]) if domain else None
                )
                response = coll.query.fetch_objects(
                    filters=filt,
                    limit=_bound_limit(s, limit or s.mcp_max_limit),
                )
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(_err("weaviate_error", str(exc))) from exc
        return json.dumps([_concept_row(o) for o in response.objects], indent=2)

    # ----- Tool 6: get_concept
    @mcp.tool(
        name="get_concept",
        description="Fetch a Concept by canonical name (case-sensitive).",
    )
    def get_concept(name: str) -> str:
        with client_session(s) as client:
            try:
                coll = client.collections.get(s.concept_collection)
                hits = coll.query.fetch_objects(
                    filters=Filter.by_property("name").equal(name),
                    limit=1,
                )
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(_err("weaviate_error", str(exc))) from exc
        if not hits.objects:
            raise ValueError(_err("not_found", f"concept {name!r} not found"))
        return json.dumps(_concept_row(hits.objects[0]), indent=2)

    # ----- Tool 7: search_concepts
    @mcp.tool(
        name="search_concepts",
        description="Semantic search across Concept.name_vec and definition_vec.",
    )
    def search_concepts(
        query: str,
        limit: int | None = None,
        target_vector: str = "definition_vec",
    ) -> str:
        if target_vector not in {"name_vec", "definition_vec"}:
            raise ValueError(_err("invalid_argument", f"unknown target_vector {target_vector!r}"))
        with client_session(s) as client:
            try:
                coll = client.collections.get(s.concept_collection)
                response = coll.query.hybrid(
                    query=query,
                    limit=_bound_limit(s, limit),
                    target_vector=target_vector,
                    return_metadata=MetadataQuery(distance=True),
                )
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(_err("weaviate_error", str(exc))) from exc
        return json.dumps([_concept_row(o) for o in response.objects], indent=2)

    # ----- Tool 8: corpus_stats
    @mcp.tool(
        name="corpus_stats",
        description="Aggregate counts by collection and (for artifacts) by source_type.",
    )
    def corpus_stats() -> str:
        out: dict[str, Any] = {}
        with client_session(s) as client:
            try:
                for name in (s.artifact_collection, s.concept_collection):
                    if not client.collections.exists(name):
                        out[name] = {"total": None, "status": "missing"}
                        continue
                    coll = client.collections.get(name)
                    total = coll.aggregate.over_all(total_count=True).total_count
                    out[name] = {"total": total}

                # Per-source breakdown for artifacts.
                if client.collections.exists(s.artifact_collection):
                    art = client.collections.get(s.artifact_collection)
                    by_source: dict[str, int] = {}
                    for st in ("json_corpus", "notebook", "markdown", "pdf"):
                        agg = art.aggregate.over_all(
                            total_count=True,
                            filters=Filter.by_property("source_type").equal(st),
                        )
                        by_source[st] = agg.total_count
                    out[s.artifact_collection]["by_source_type"] = by_source
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(_err("weaviate_error", str(exc))) from exc
        return json.dumps(out, indent=2)

    return mcp


def serve_stdio(settings: Settings | None = None) -> None:
    """Entry point for `fractal-rag serve`."""
    mcp = build_server(settings)
    mcp.run(transport="stdio")
