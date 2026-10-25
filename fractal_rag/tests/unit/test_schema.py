"""Unit tests for the schema bootstrap.

These tests use a stub WeaviateClient — collection-existence checks toggle
between calls so we can assert idempotency without a live cluster.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from fractal_rag.config import Settings
from fractal_rag.schema import bootstrap


class _FakeConfig:
    """Mimics ``collection.config``: ``get().properties`` and ``add_property``."""

    def __init__(self, properties: list[Any]) -> None:
        self.properties = list(properties)
        self.added: list[str] = []

    def get(self) -> SimpleNamespace:
        return SimpleNamespace(properties=list(self.properties))

    def add_property(self, prop: Any) -> None:
        if any(p.name == prop.name for p in self.properties):
            raise RuntimeError(f"property {prop.name} already exists")
        self.properties.append(prop)
        self.added.append(prop.name)


class _FakeCollection:
    def __init__(self, properties: list[Any]) -> None:
        self.config = _FakeConfig(properties)


class _FakeCollections:
    def __init__(self) -> None:
        self._existing: dict[str, _FakeCollection] = {}
        self.create_calls: list[dict[str, Any]] = []
        self.delete_calls: list[str] = []

    def exists(self, name: str) -> bool:
        return name in self._existing

    def create(self, *, name: str, **kwargs: Any) -> None:
        if name in self._existing:
            raise RuntimeError(f"create called for already-existing collection {name}")
        self.create_calls.append({"name": name, **kwargs})
        self._existing[name] = _FakeCollection(kwargs.get("properties", []))

    def delete(self, name: str) -> None:
        self.delete_calls.append(name)
        self._existing.pop(name, None)

    def get(self, name: str) -> _FakeCollection:
        return self._existing[name]


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
    assert second.properties_added == {}  # nothing to add to an up-to-date collection
    assert client.collections.get("FractalArtifact").config.added == []


def test_bootstrap_adds_properties_missing_from_existing_collection(settings: Settings) -> None:
    """An index bootstrapped before `resource` existed gains the property without --drop."""
    client = _FakeClient()
    bootstrap(client, settings)  # type: ignore[arg-type]
    artifact = client.collections.get("FractalArtifact")
    artifact.config.properties = [p for p in artifact.config.properties if p.name != "resource"]
    assert "resource" not in {p.name for p in artifact.config.get().properties}

    result = bootstrap(client, settings)  # type: ignore[arg-type]
    assert result.created == []
    assert set(result.already_present) == {"FractalArtifact", "Concept"}
    assert result.properties_added == {"FractalArtifact": ["resource"]}
    assert artifact.config.added == ["resource"]
    assert "resource" in {p.name for p in artifact.config.get().properties}
    assert len(client.collections.create_calls) == 2  # no re-creation

    third = bootstrap(client, settings)  # type: ignore[arg-type]
    assert third.properties_added == {}
    assert artifact.config.added == ["resource"]  # not added twice


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
