"""Unit tests for the schema bootstrap.

These tests use a stub WeaviateClient — collection-existence checks toggle
between calls so we can assert idempotency without a live cluster.
"""

from __future__ import annotations

from typing import Any

import pytest

from fractal_rag.config import Settings
from fractal_rag.schema import bootstrap


class _FakeCollections:
    def __init__(self) -> None:
        self._existing: set[str] = set()
        self.create_calls: list[dict[str, Any]] = []
        self.delete_calls: list[str] = []

    def exists(self, name: str) -> bool:
        return name in self._existing

    def create(self, *, name: str, **kwargs: Any) -> None:
        if name in self._existing:
            raise RuntimeError(f"create called for already-existing collection {name}")
        self.create_calls.append({"name": name, **kwargs})
        self._existing.add(name)

    def delete(self, name: str) -> None:
        self.delete_calls.append(name)
        self._existing.discard(name)


class _FakeClient:
    def __init__(self) -> None:
        self.collections = _FakeCollections()


@pytest.fixture
def settings() -> Settings:
    return Settings(
        artifact_collection="FractalArtifact",
        concept_collection="Concept",
        vectorizer_module="text2vec-transformers",
    )


def test_bootstrap_creates_both_collections_first_time(settings: Settings) -> None:
    client = _FakeClient()
    result = bootstrap(client, settings)  # type: ignore[arg-type]
    assert set(result.created) == {"FractalArtifact", "Concept"}
    assert result.already_present == []
    assert len(client.collections.create_calls) == 2


def test_bootstrap_is_idempotent(settings: Settings) -> None:
    client = _FakeClient()
    bootstrap(client, settings)  # type: ignore[arg-type]
    second = bootstrap(client, settings)  # type: ignore[arg-type]
    assert second.created == []
    assert set(second.already_present) == {"FractalArtifact", "Concept"}


def test_bootstrap_drop_existing(settings: Settings) -> None:
    client = _FakeClient()
    bootstrap(client, settings)  # type: ignore[arg-type]
    result = bootstrap(client, settings, drop_existing=True)  # type: ignore[arg-type]
    assert set(result.created) == {"FractalArtifact", "Concept"}
    assert set(client.collections.delete_calls) == {"FractalArtifact", "Concept"}


def test_concept_collection_created_before_artifact(settings: Settings) -> None:
    """Artifact references Concept, so Concept must come first."""
    client = _FakeClient()
    bootstrap(client, settings)  # type: ignore[arg-type]
    names = [c["name"] for c in client.collections.create_calls]
    assert names.index("Concept") < names.index("FractalArtifact")


def test_unsupported_vectorizer_raises(settings: Settings) -> None:
    client = _FakeClient()
    bad = settings.model_copy(update={"vectorizer_module": "text2vec-openai"})
    with pytest.raises(ValueError, match="Unsupported vectorizer"):
        bootstrap(client, bad)  # type: ignore[arg-type]
