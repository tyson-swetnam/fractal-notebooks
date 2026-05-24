"""Idempotent schema bootstrap for FractalArtifact and Concept collections.

Per the design spec §6: polymorphic FractalArtifact for all chunked content +
a Concept side-collection for ontology entries. Both collections use named
vectors so titles, summaries, and content can be searched independently.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from weaviate.classes.config import (
    Configure,
    DataType,
    Property,
    ReferenceProperty,
    Tokenization,
)
from weaviate.client import WeaviateClient

from .config import Settings, get_settings


@dataclass
class BootstrapResult:
    created: list[str]
    already_present: list[str]

    @property
    def total(self) -> int:
        return len(self.created) + len(self.already_present)


def _artifact_properties() -> list[Property]:
    return [
        Property(name="source_type", data_type=DataType.TEXT, tokenization=Tokenization.FIELD),
        Property(name="source_uri", data_type=DataType.TEXT, tokenization=Tokenization.FIELD),
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


def bootstrap(
    client: WeaviateClient,
    settings: Settings | None = None,
    *,
    drop_existing: bool = False,
) -> BootstrapResult:
    """Create the two collections if missing; reuse if present.

    Returns a BootstrapResult describing what changed. Safe to call repeatedly.
    """
    s = settings or get_settings()
    created: list[str] = []
    already: list[str] = []

    if drop_existing:
        for name in (s.artifact_collection, s.concept_collection):
            if client.collections.exists(name):
                client.collections.delete(name)

    if client.collections.exists(s.concept_collection):
        already.append(s.concept_collection)
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

    return BootstrapResult(created=created, already_present=already)
