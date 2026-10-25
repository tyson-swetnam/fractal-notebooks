"""Idempotent schema bootstrap for FractalArtifact and Concept collections.

Per the design spec §6: polymorphic FractalArtifact for all chunked content +
a Concept side-collection for ontology entries. Both collections use named
vectors so titles, summaries, and content can be searched independently.

Re-running the bootstrap against an existing index also appends any property the
code declares that the live collection lacks (Weaviate allows adding properties,
never changing them), so a schema addition such as ``resource`` reaches indexes
created before it existed without ``--drop``.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass, field

from weaviate.classes.config import (
    Configure,
    DataType,
    Property,
    ReferenceProperty,
    Tokenization,
)
from weaviate.client import WeaviateClient

from .config import Settings, get_settings

log = logging.getLogger("fractal_rag.schema")


@dataclass
class BootstrapResult:
    created: list[str]
    already_present: list[str]
    # collection name -> properties appended to an already-existing collection
    properties_added: dict[str, list[str]] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return len(self.created) + len(self.already_present)


def _artifact_properties() -> list[Property]:
    return [
        Property(name="source_type", data_type=DataType.TEXT, tokenization=Tokenization.FIELD),
        Property(name="source_uri", data_type=DataType.TEXT, tokenization=Tokenization.FIELD),
        # Public URL: the OKF `resource` of documentation pages and rendered notebooks, the
        # https://doi.org/ link of Constellate records that have a DOI; null otherwise.
        Property(name="resource", data_type=DataType.TEXT, tokenization=Tokenization.FIELD),
        Property(name="parent_id", data_type=DataType.TEXT, tokenization=Tokenization.FIELD),
        Property(name="chunk_index", data_type=DataType.INT),
        Property(name="title", data_type=DataType.TEXT),
        Property(name="summary", data_type=DataType.TEXT),
        Property(name="content", data_type=DataType.TEXT),
        Property(name="authors", data_type=DataType.TEXT_ARRAY),
        Property(name="year", data_type=DataType.INT),
        Property(name="latex_equations", data_type=DataType.TEXT_ARRAY),
        Property(name="figure_refs", data_type=DataType.TEXT_ARRAY),
        Property(name="tags", data_type=DataType.TEXT_ARRAY, tokenization=Tokenization.FIELD),
        Property(name="ingested_at", data_type=DataType.DATE),
    ]


def _concept_properties() -> list[Property]:
    return [
        Property(name="name", data_type=DataType.TEXT),
        Property(name="aliases", data_type=DataType.TEXT_ARRAY),
        Property(name="definition", data_type=DataType.TEXT),
        Property(name="domain", data_type=DataType.TEXT_ARRAY, tokenization=Tokenization.FIELD),
        Property(name="hausdorff_dim_range", data_type=DataType.NUMBER_ARRAY),
        Property(name="related_concept_ids", data_type=DataType.TEXT_ARRAY),
    ]


def _named_vectors(fields: Iterable[str], vectorizer_module: str):
    """Build named-vector configs that vectorize the given source properties."""
    if vectorizer_module != "text2vec-transformers":
        raise ValueError(
            f"Unsupported vectorizer module {vectorizer_module!r}; "
            "spec assumes text2vec-transformers."
        )
    return [
        Configure.NamedVectors.text2vec_transformers(
            name=f"{field}_vec",
            source_properties=[field],
        )
        for field in fields
    ]


def _add_missing_properties(
    client: WeaviateClient, name: str, wanted: list[Property]
) -> list[str]:
    """Append to collection ``name`` every property in ``wanted`` it lacks; return their names.

    Objects already in the collection carry a null value for a new property until they
    are re-ingested (``fractal-rag ingest`` upserts by deterministic UUID, so a plain
    re-run fills it in).
    """
    collection = client.collections.get(name)
    present = {prop.name for prop in collection.config.get().properties}
    added: list[str] = []
    for prop in wanted:
        if prop.name not in present:
            collection.config.add_property(prop)
            added.append(prop.name)
            log.info("schema: added property %r to existing collection %s", prop.name, name)
    return added


def bootstrap(
    client: WeaviateClient,
    settings: Settings | None = None,
    *,
    drop_existing: bool = False,
) -> BootstrapResult:
    """Create the two collections if missing; reuse if present.

    An existing collection is brought up to date by appending the properties the code
    declares and it lacks (reported in ``properties_added``). Returns a BootstrapResult
    describing what changed. Safe to call repeatedly.
    """
    s = settings or get_settings()
    created: list[str] = []
    already: list[str] = []
    properties_added: dict[str, list[str]] = {}

    if drop_existing:
        for name in (s.artifact_collection, s.concept_collection):
            if client.collections.exists(name):
                client.collections.delete(name)

    if client.collections.exists(s.concept_collection):
        already.append(s.concept_collection)
        added = _add_missing_properties(client, s.concept_collection, _concept_properties())
        if added:
            properties_added[s.concept_collection] = added
    else:
        client.collections.create(
            name=s.concept_collection,
            description="Curated fractal-mathematics concepts used to tag artifacts.",
            properties=_concept_properties(),
            vectorizer_config=_named_vectors(
                ["name", "definition"], s.vectorizer_module
            ),
        )
        created.append(s.concept_collection)

    if client.collections.exists(s.artifact_collection):
        already.append(s.artifact_collection)
        added = _add_missing_properties(client, s.artifact_collection, _artifact_properties())
        if added:
            properties_added[s.artifact_collection] = added
    else:
        client.collections.create(
            name=s.artifact_collection,
            description=(
                "Polymorphic chunk/doc record for notebooks, markdown, PDFs, and "
                "the CyVerse JSON corpus."
            ),
            properties=_artifact_properties(),
            references=[
                ReferenceProperty(
                    name="concepts",
                    target_collection=s.concept_collection,
                ),
            ],
            vectorizer_config=_named_vectors(
                ["content", "title", "summary"], s.vectorizer_module
            ),
        )
        created.append(s.artifact_collection)

    return BootstrapResult(
        created=created, already_present=already, properties_added=properties_added
    )
