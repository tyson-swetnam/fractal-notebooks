r"""Parser for the documentation site's Markdown pages (Zensical, OKF v0.2 frontmatter).

Each ``.md`` file becomes a single RawDocument. A leading YAML frontmatter block is
parsed and stripped from the indexed content: ``title`` comes from the frontmatter,
else the first H1, else the file stem, and the OKF fields ``type`` (stored as
``okf_type``), ``description``, ``tags``, ``status`` and ``resource`` (the page's public
URL, which agents should cite in preference to ``source_uri``) are carried in
``metadata``. ``source_uri`` stays the ``file://`` path of the source file.

LaTeX equations are extracted out-of-band (``$$...$$`` blocks, ``\[...\]`` blocks and
``\begin{equation}...\end{equation}``-style environments) so they can be indexed
independently of the prose.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

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
# A frontmatter block must open on the very first line and close on a line of three dashes.
_FRONTMATTER = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)

# OKF frontmatter keys copied into RawDocument.metadata (frontmatter key -> metadata key).
_OKF_SCALARS = {
    "type": "okf_type",
    "description": "description",
    "status": "status",
    "resource": "resource",
}


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


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return ``(frontmatter mapping, body)``; the mapping is empty when there is none.

    A block that does not parse as YAML, or parses to something other than a mapping
    (a list, a scalar, an empty document), is left in place (empty mapping, full text)
    rather than silently discarding content.
    """
    match = _FRONTMATTER.match(text)
    if not match:
        return {}, text
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}, text
    if not isinstance(data, dict):
        return {}, text
    return data, text[match.end() :].lstrip("\r\n")


def _clean_str(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return " ".join(value.split())
    return None


def _str_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, (list, tuple)):
        return [str(v).strip() for v in value if str(v).strip()]
    return []


def parse_markdown(path: Path) -> list[RawDocument]:
    text = path.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = split_frontmatter(text)
    if not body.strip():
        return []

    title = _clean_str(frontmatter.get("title"))
    if title is None:
        h1 = _H1.search(body)
        title = h1.group(1).strip() if h1 else path.stem.replace("-", " ").replace("_", " ")

    metadata: dict[str, Any] = {
        "path": str(path),
        "extension": path.suffix.lower(),
    }
    for key, meta_key in _OKF_SCALARS.items():
        value = _clean_str(frontmatter.get(key))
        if value is not None:
            metadata[meta_key] = value
    tags = _str_list(frontmatter.get("tags"))
    if tags:
        metadata["tags"] = tags

    return [
        RawDocument(
            source_type="markdown",
            source_uri=f"file://{path.resolve()}",
            title=title,
            content=body,
            latex_equations=extract_latex_equations(body),
            figure_refs=extract_figure_refs(body),
            metadata=metadata,
        )
    ]
