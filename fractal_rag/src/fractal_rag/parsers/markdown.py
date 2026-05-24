r"""Parser for Markdown (and MkDocs) documents.

Each ``.md`` file becomes a single RawDocument. LaTeX equations are extracted
out-of-band (both ``$$...$$`` blocks and ``\begin{equation}...\end{equation}``
environments) so they can be indexed independently of the prose.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import RawDocument


_DOLLAR_BLOCK = re.compile(r"\$\$([\s\S]+?)\$\$")
_BRACKET_BLOCK = re.compile(r"\\\[([\s\S]+?)\\\]")
_LATEX_ENV = re.compile(
    r"\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}"
    r"([\s\S]+?)"
    r"\\end\{\1\}"
)
_IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
_H1 = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def extract_latex_equations(text: str) -> list[str]:
    equations: list[str] = []
    for match in _DOLLAR_BLOCK.finditer(text):
        eq = match.group(1).strip()
        if eq:
            equations.append(eq)
    for match in _BRACKET_BLOCK.finditer(text):
        eq = match.group(1).strip()
        if eq:
            equations.append(eq)
    for match in _LATEX_ENV.finditer(text):
        eq = match.group(2).strip()
        if eq:
            equations.append(eq)
    return equations


def extract_figure_refs(text: str) -> list[str]:
    return [m.group(1).strip() for m in _IMAGE.finditer(text) if m.group(1).strip()]


def parse_markdown(path: Path) -> list[RawDocument]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        return []

    h1 = _H1.search(text)
    title = h1.group(1).strip() if h1 else path.stem.replace("-", " ").replace("_", " ")

    return [
        RawDocument(
            source_type="markdown",
            source_uri=f"file://{path.resolve()}",
            title=title,
            content=text,
            latex_equations=extract_latex_equations(text),
            figure_refs=extract_figure_refs(text),
            metadata={
                "path": str(path),
                "extension": path.suffix.lower(),
            },
        )
    ]
