"""PDF text extraction via pdfminer.six.

Spec section 12 flags PDFs as optional for v1 (no PDFs are present in the current
corpus pull). When a PDF *is* provided, we extract plain text and emit one
RawDocument with a ``quality=fallback`` tag. Missing, corrupt or unreadable files
(whatever pdfminer or the filesystem raises) are logged and skipped (an empty list
is returned) so one bad file cannot abort an ingest run.
"""

from __future__ import annotations

import logging
from pathlib import Path

from . import RawDocument

log = logging.getLogger("fractal_rag.parsers.pdf")


def parse_pdf(path: Path) -> list[RawDocument]:
    try:
        from pdfminer.high_level import extract_text
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "PDF parsing requires the 'parsers' extra: pip install 'fractal-rag[parsers]'"
        ) from exc

    if not path.is_file():
        log.warning("pdf: %s does not exist; skipping", path)
        return []

    try:
        text = extract_text(str(path)) or ""
    except Exception as exc:
        # pdfminer raises far more than PSException on damaged files (KeyError, TypeError,
        # RecursionError, struct.error, ...); any of them means "skip this file".
        log.warning("pdf: could not extract text from %s (%s: %s); skipping", path, type(exc).__name__, exc)
        return []

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
