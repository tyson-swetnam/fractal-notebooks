"""Unit tests for the concept seed loader."""

from __future__ import annotations

from fractal_rag.concepts.loader import ConceptRecord, load_seed


def test_seed_loads_expected_count() -> None:
    records = load_seed()
    # Spec calls for ~30 hand-curated entries.
    assert 20 <= len(records) <= 60


def test_seed_records_are_unique() -> None:
    records = load_seed()
    names = [r.name.lower() for r in records]
    assert len(names) == len(set(names))


def test_record_match_terms_longest_first() -> None:
    r = ConceptRecord(
        name="Fractal Dimension",
        aliases=("fractal", "dim"),
        definition="x",
        domain=(),
    )
    terms = r.match_terms
    assert terms == tuple(sorted(terms, key=len, reverse=True))
    assert terms[0] == "fractal dimension"


def test_every_record_has_definition() -> None:
    for r in load_seed():
        assert r.definition.strip(), f"empty definition for {r.name}"
        assert r.name.strip(), "blank concept name in seed"


def test_known_concepts_present() -> None:
    names = {r.name for r in load_seed()}
    must_have = {"Mandelbrot Set", "Hausdorff Dimension", "Box-Counting Dimension",
                 "Riemann Zeta Function", "Hurst Exponent"}
    missing = must_have - names
    assert not missing, f"seed is missing required concepts: {missing}"
