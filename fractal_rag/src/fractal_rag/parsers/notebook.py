"""Parser for Jupyter notebooks.

Each notebook produces one RawDocument per cell. Markdown cells become
``source_type='notebook'`` with the LaTeX extractor applied; code cells become
``source_type='notebook'`` carrying ``tags=['code']`` in metadata. When the site has
pre-rendered the notebook into a Markdown page next to it (``<stem>.md`` with OKF
frontmatter), that page's ``resource`` (public URL) is carried in ``metadata['resource']``
so agents can cite the published page rather than the ``file://`` path.
"""

from __future__ import annotations

import re
from pathlib import Path

import nbformat

from . import RawDocument
from .markdown import extract_latex_equations, split_frontmatter

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


def _rendered_resource(path: Path) -> str | None:
    """``resource`` from the frontmatter of a rendered sibling ``<stem>.md``, if there is one."""
    sibling = path.with_suffix(".md")
    if not sibling.is_file():
        return None
    frontmatter, _ = split_frontmatter(sibling.read_text(encoding="utf-8", errors="replace"))
    value = frontmatter.get("resource")
    return value.strip() if isinstance(value, str) and value.strip() else None


def parse_notebook(path: Path) -> list[RawDocument]:
    """Walk a notebook's cells; emit one RawDocument per non-empty cell."""
    nb = nbformat.read(path.open("r", encoding="utf-8"), as_version=4)
    notebook_title = _notebook_title(path, nb)
    resource = _rendered_resource(path)
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

        metadata: dict[str, object] = {
            "notebook_path": str(path),
            "notebook_title": notebook_title,
            "cell_index": index,
            "cell_type": cell.cell_type,
            "tags": tags,
        }
        if resource is not None:
            metadata["resource"] = resource
        documents.append(
            RawDocument(
                source_type="notebook",
                source_uri=f"file://{path.resolve()}#cell={index}",
                title=f"{notebook_title} — cell {index}",
                content=text,
                latex_equations=equations,
                metadata=metadata,
            )
        )

    return documents
