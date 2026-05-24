"""PDF text extraction via pdfminer.six.

Spec §12 flags PDFs as optional for v1 (no PDFs are present in the current
corpus pull). When a PDF *is* provided, we extract plain text and emit one
RawDocument with a ``quality='fallback'`` tag.
"""

from __future__ import annotations

from pathlib import Path

from . import RawDocument


def parse_pdf(path: Path) -> list[RawDocument]:
    try:
        from pdfminer.high_level import extract_text
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "PDF parsing requires the 'parsers' extra: pip install 'fractal-rag[parsers]'"
        ) from exc

    text = extract_text(str(path)) or ""
    if not text.strip():
        return []

    return [
        RawDocument(
            source_type="pdf",
            source_uri=f"file://{path.resolve()}",
            title=path.stem.replace("_", " ").replace("-", " "),
            content=text,
            metadata={
                "path": str(path),
                "tags": ["quality=fallback"],
            },
        )
    ]
