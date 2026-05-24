"""Parser for Jupyter notebooks.

Each notebook produces one RawDocument per cell. Markdown cells become
``source_type='notebook'`` with the LaTeX extractor applied; code cells become
``source_type='notebook'`` carrying ``tags=['code']`` in metadata.
"""

from __future__ import annotations

import re
from pathlib import Path

import nbformat

from . import RawDocument
from .markdown import extract_latex_equations


_CODE_TAG = "code"


def _cell_text(cell: nbformat.NotebookNode) -> str:
    src = cell.get("source") or ""
    if isinstance(src, list):
        return "".join(src)
    return src


def _notebook_title(path: Path, nb: nbformat.NotebookNode) -> str:
    """First H1 from the first markdown cell, falling back to the filename stem."""
    for cell in nb.cells:
        if cell.cell_type != "markdown":
            continue
        text = _cell_text(cell)
        for line in text.splitlines():
            m = re.match(r"^#\s+(.+?)\s*$", line)
            if m:
                return m.group(1).strip()
        break
    return path.stem.replace("_", " ")


def parse_notebook(path: Path) -> list[RawDocument]:
    """Walk a notebook's cells; emit one RawDocument per non-empty cell."""
    nb = nbformat.read(path.open("r", encoding="utf-8"), as_version=4)
    notebook_title = _notebook_title(path, nb)
    documents: list[RawDocument] = []

    for index, cell in enumerate(nb.cells):
        text = _cell_text(cell).strip()
        if not text:
            continue

        if cell.cell_type == "markdown":
            equations = extract_latex_equations(text)
            tags: list[str] = []
        elif cell.cell_type == "code":
            equations = []
            tags = [_CODE_TAG]
        else:
            continue

        documents.append(
            RawDocument(
                source_type="notebook",
                source_uri=f"file://{path.resolve()}#cell={index}",
                title=f"{notebook_title} — cell {index}",
                content=text,
                latex_equations=equations,
                metadata={
                    "notebook_path": str(path),
                    "notebook_title": notebook_title,
                    "cell_index": index,
                    "cell_type": cell.cell_type,
                    "tags": tags,
                },
            )
        )

    return documents
