"""Load and validate the curated concept seed YAML."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ..config import Settings, get_settings


@dataclass(frozen=True)
class ConceptRecord:
    name: str
    aliases: tuple[str, ...]
    definition: str
    domain: tuple[str, ...]
    hausdorff_dim_range: tuple[float, ...] = field(default_factory=tuple)

    @property
    def match_terms(self) -> tuple[str, ...]:
        """Names + aliases, lowercased, sorted by length descending.

        Longest-first ordering matters for the enricher's greedy matcher so
        'fractal dimension' is matched before bare 'fractal'.
        """
        terms = {self.name.lower(), *(a.lower() for a in self.aliases)}
        return tuple(sorted(terms, key=len, reverse=True))


def load_seed(path: Path | None = None, settings: Settings | None = None) -> list[ConceptRecord]:
    """Parse the YAML seed file into ConceptRecord instances."""
    s = settings or get_settings()
    seed_path = path or s.concepts_seed_path
    if not seed_path.exists():
        raise FileNotFoundError(f"Concept seed file not found: {seed_path}")

    with seed_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, list):
        raise ValueError(
            f"Seed file {seed_path} must be a YAML list at top level, got {type(raw).__name__}"
        )

    records: list[ConceptRecord] = []
    seen_names: set[str] = set()
    for i, entry in enumerate(raw):
        if not isinstance(entry, dict) or "name" not in entry or "definition" not in entry:
            raise ValueError(
                f"Concept seed entry {i} is missing required 'name' or 'definition' fields"
            )
        name = entry["name"].strip()
        if name.lower() in seen_names:
            raise ValueError(f"Duplicate concept name in seed: {name!r}")
        seen_names.add(name.lower())

        records.append(
            ConceptRecord(
                name=name,
                aliases=tuple(entry.get("aliases") or ()),
                definition=" ".join(entry["definition"].split()),
                domain=tuple(entry.get("domain") or ()),
                hausdorff_dim_range=tuple(entry.get("hausdorff_dim_range") or ()),
            )
        )

    return records
