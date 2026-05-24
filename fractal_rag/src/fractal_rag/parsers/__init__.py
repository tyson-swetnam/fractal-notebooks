"""Source-format parsers — all yield :class:`RawDocument` instances."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RawDocument:
    """A pre-chunk, pre-enrichment representation of a source artifact.

    Parsers are pure: they read filesystem content and emit RawDocuments.
    Chunking, concept tagging, and vector ingestion happen downstream.

    Attributes:
        source_type: One of ``json_corpus``, ``notebook``, ``notebook_cell``,
            ``markdown``, ``pdf``. ``notebook_cell`` is reserved for the
            per-cell chunks emitted by the notebook parser.
        source_uri: Stable identifier (``file://``, ``irods://``, etc.).
        title: Document title (notebook filename, MD H1, PDF title, JSON id).
        content: Plain-text body. Markdown/LaTeX preserved; binary stripped.
        metadata: Free-form per-source metadata (cell_index, page, authors, ...).
        latex_equations: Equations extracted out-of-band for indexing.
        figure_refs: Filenames or asset URIs referenced by the document.
        year: Publication year if known.
        authors: Author names if known.
    """

    source_type: str
    source_uri: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    latex_equations: list[str] = field(default_factory=list)
    figure_refs: list[str] = field(default_factory=list)
    year: int | None = None
    authors: list[str] = field(default_factory=list)
