"""Unit tests for the four source-format parsers."""

from __future__ import annotations

import json
from pathlib import Path

import nbformat
import pytest

from fractal_rag.parsers import RawDocument
from fractal_rag.parsers.json_corpus import parse_jsonl
from fractal_rag.parsers.markdown import (
    extract_figure_refs,
    extract_latex_equations,
    parse_markdown,
    split_frontmatter,
)
from fractal_rag.parsers.notebook import parse_notebook

# ---------------------------------------------------------------------------
# JSON corpus parser

def _make_constellate_record(idx: int) -> dict:
    return {
        "id": f"ark://27927/record{idx}",
        "doi": f"10.1234/test.{idx}",
        "title": f"Fractal study {idx}",
        "creator": ["Alice", "Bob"],
        "publicationYear": 2020 + idx,
        "isPartOf": "Journal of Test Fractals",
        "publisher": "Test Press",
        "docType": "article",
        "url": f"http://doi.org/10.1234/test.{idx}",
        "wordCount": 1000 + idx,
        "keyphrase": ["fractal dimension", "self-similarity"],
        "tdmCategory": ["Mathematics"],
        "unigramCount": {"fractal": 50, "dimension": 30, "the": 200},
        "bigramCount": {"fractal dimension": 25, "self-similar set": 10},
        "trigramCount": {"the fractal dimension": 12},
    }


def test_parse_jsonl_yields_one_doc_per_record(tmp_path: Path) -> None:
    p = tmp_path / "corpus.jsonl"
    with p.open("w") as f:
        for i in range(3):
            f.write(json.dumps(_make_constellate_record(i)) + "\n")

    docs = list(parse_jsonl(p))
    assert len(docs) == 3
    assert all(isinstance(d, RawDocument) for d in docs)
    assert docs[0].title == "Fractal study 0"
    assert docs[0].source_type == "json_corpus"
    assert docs[0].source_uri == "doi:10.1234/test.0"
    assert docs[0].year == 2020
    assert docs[0].authors == ["Alice", "Bob"]
    assert "fractal dimension" in docs[0].content
    assert docs[0].metadata["journal"] == "Journal of Test Fractals"


def test_parse_jsonl_respects_limit(tmp_path: Path) -> None:
    p = tmp_path / "corpus.jsonl"
    with p.open("w") as f:
        for i in range(10):
            f.write(json.dumps(_make_constellate_record(i)) + "\n")

    docs = list(parse_jsonl(p, limit=4))
    assert len(docs) == 4


def test_parse_jsonl_skips_blank_lines(tmp_path: Path) -> None:
    p = tmp_path / "corpus.jsonl"
    with p.open("w") as f:
        f.write(json.dumps(_make_constellate_record(0)) + "\n")
        f.write("\n")
        f.write(json.dumps(_make_constellate_record(1)) + "\n")
    docs = list(parse_jsonl(p))
    assert len(docs) == 2


# ---------------------------------------------------------------------------
# Notebook parser

def _write_notebook(tmp_path: Path) -> Path:
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        nbformat.v4.new_markdown_cell("# Mandelbrot Notebook\n\nIntro text."),
        nbformat.v4.new_markdown_cell("Equation: $$ z_{n+1} = z_n^2 + c $$"),
        nbformat.v4.new_code_cell("import numpy as np\nprint('hi')"),
        nbformat.v4.new_markdown_cell(""),  # blank cell, must be dropped
    ]
    p = tmp_path / "mandelbrot.ipynb"
    nbformat.write(nb, p.open("w"))
    return p


def test_parse_notebook_emits_per_cell_docs(tmp_path: Path) -> None:
    p = _write_notebook(tmp_path)
    docs = parse_notebook(p)
    assert len(docs) == 3  # blank cell dropped
    titles = [d.metadata["cell_type"] for d in docs]
    assert titles == ["markdown", "markdown", "code"]
    assert "Mandelbrot Notebook" in docs[0].title
    assert "z_{n+1}" in docs[1].latex_equations[0]
    assert docs[2].metadata["tags"] == ["code"]


def test_parse_notebook_falls_back_to_filename_title(tmp_path: Path) -> None:
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell("x = 1")]
    p = tmp_path / "fractal_demo.ipynb"
    nbformat.write(nb, p.open("w"))
    docs = parse_notebook(p)
    assert "fractal demo" in docs[0].metadata["notebook_title"]
    assert "resource" not in docs[0].metadata  # no rendered sibling page


def test_parse_notebook_carries_resource_from_rendered_sibling(tmp_path: Path) -> None:
    """A pre-rendered <stem>.md next to the notebook lends its OKF resource URL to every cell."""
    p = _write_notebook(tmp_path)
    url = "https://tyson-swetnam.github.io/fractal-notebooks/notebooks/foundations/mandelbrot/"
    p.with_suffix(".md").write_text(
        f"---\ntype: Notebook\ntitle: Mandelbrot (notebook)\nresource: {url}\n---\n\n# Mandelbrot\n",
        encoding="utf-8",
    )
    docs = parse_notebook(p)
    assert len(docs) == 3
    assert all(d.metadata["resource"] == url for d in docs)
    assert docs[0].source_uri.startswith("file://")  # source_uri still points at the .ipynb

    # a sibling without a usable resource adds nothing
    p.with_suffix(".md").write_text("# Plain page, no frontmatter\n", encoding="utf-8")
    assert all("resource" not in d.metadata for d in parse_notebook(p))


# ---------------------------------------------------------------------------
# Markdown parser

MD_SAMPLE = """# Sample Doc

Some intro paragraph.

$$
\\zeta(s) = \\sum_{n=1}^\\infty n^{-s}
$$

\\begin{equation}
D_H = \\inf \\{ d : H^d(S) = 0 \\}
\\end{equation}

![fig1](images/foo.png)
![alt](images/bar.svg)
"""


def test_parse_markdown_extracts_title_and_equations(tmp_path: Path) -> None:
    p = tmp_path / "doc.md"
    p.write_text(MD_SAMPLE)
    docs = parse_markdown(p)
    assert len(docs) == 1
    d = docs[0]
    assert d.title == "Sample Doc"
    assert len(d.latex_equations) == 2
    assert any("zeta" in eq for eq in d.latex_equations)
    assert any("D_H" in eq for eq in d.latex_equations)
    assert sorted(d.figure_refs) == ["images/bar.svg", "images/foo.png"]


def test_parse_markdown_skips_empty(tmp_path: Path) -> None:
    p = tmp_path / "empty.md"
    p.write_text("   \n")
    assert parse_markdown(p) == []


MD_WITH_FRONTMATTER = """---
type: Chapter
title: "Chapter 1: History of Fractal Mathematics"
description: How fractal geometry emerged from nineteenth-century analysis.
resource: https://tyson-swetnam.github.io/fractal-notebooks/foundations/history/
tags: [foundations, part-i, geometry]
sources:
  - id: mandelbrot-1982
    resource: https://example.org/mandelbrot
    title: The Fractal Geometry of Nature
generated:
  by: human:tswetnam
  at: "2025-01-01T00:00:00Z"
status: stable
---

# History of Fractal Mathematics

Cantor built his dust in 1883. $$D = \\frac{\\log 2}{\\log 3}$$
"""


def test_parse_markdown_strips_frontmatter_and_carries_okf_metadata(tmp_path: Path) -> None:
    p = tmp_path / "history.md"
    p.write_text(MD_WITH_FRONTMATTER, encoding="utf-8")
    docs = parse_markdown(p)
    assert len(docs) == 1
    d = docs[0]
    assert d.title == "Chapter 1: History of Fractal Mathematics"  # frontmatter title wins over H1
    assert d.content.startswith("# History of Fractal Mathematics")
    assert "okf_version" not in d.content and "generated:" not in d.content
    assert d.source_uri == f"file://{p.resolve()}"  # unchanged by frontmatter
    assert d.metadata["okf_type"] == "Chapter"
    assert d.metadata["description"] == "How fractal geometry emerged from nineteenth-century analysis."
    assert d.metadata["tags"] == ["foundations", "part-i", "geometry"]
    assert d.metadata["status"] == "stable"
    assert d.metadata["resource"] == "https://tyson-swetnam.github.io/fractal-notebooks/foundations/history/"
    assert d.metadata["path"] == str(p) and d.metadata["extension"] == ".md"
    assert any("log 2" in eq for eq in d.latex_equations)


def test_parse_markdown_title_falls_back_to_h1_then_stem(tmp_path: Path) -> None:
    p = tmp_path / "with_h1.md"
    p.write_text("---\ntype: Guide\ntags: [apps]\n---\n# From The Heading\n\nBody.\n", encoding="utf-8")
    d = parse_markdown(p)[0]
    assert d.title == "From The Heading"
    assert d.metadata["okf_type"] == "Guide"
    assert "resource" not in d.metadata and "description" not in d.metadata

    q = tmp_path / "react-apps_page.md"
    q.write_text("Just a paragraph, no heading.\n", encoding="utf-8")
    assert parse_markdown(q)[0].title == "react apps page"


def test_parse_markdown_frontmatter_only_page_is_skipped(tmp_path: Path) -> None:
    p = tmp_path / "stub.md"
    p.write_text("---\ntype: Index\ntitle: Stub\n---\n", encoding="utf-8")
    assert parse_markdown(p) == []


def test_parse_markdown_keeps_unparseable_frontmatter_as_content(tmp_path: Path) -> None:
    p = tmp_path / "broken.md"
    p.write_text("---\ntitle: [unclosed\n---\n# Real Title\n\nText.\n", encoding="utf-8")
    d = parse_markdown(p)[0]
    assert d.title == "Real Title"
    assert d.content.startswith("---\ntitle: [unclosed")  # nothing silently dropped
    assert "okf_type" not in d.metadata


def test_split_frontmatter_isolated() -> None:
    assert split_frontmatter("# No frontmatter\n") == ({}, "# No frontmatter\n")
    fm, body = split_frontmatter("---\na: 1\ntags: [x, y]\n---\nbody\n")
    assert fm == {"a": 1, "tags": ["x", "y"]} and body == "body\n"
    # a parseable block that is not a mapping is kept as content, like an unparseable one
    not_mapping = "---\n- not a mapping\n---\nbody\n"
    assert split_frontmatter(not_mapping) == ({}, not_mapping)
    scalar = "---\njust a string\n---\nbody\n"
    assert split_frontmatter(scalar) == ({}, scalar)
    # a horizontal rule later in the document is not frontmatter
    assert split_frontmatter("text\n\n---\n\nmore\n")[0] == {}


def test_parse_markdown_keeps_non_mapping_frontmatter_as_content(tmp_path: Path) -> None:
    p = tmp_path / "listy.md"
    p.write_text("---\n- alpha\n- beta\n---\n# Real Title\n\nText.\n", encoding="utf-8")
    d = parse_markdown(p)[0]
    assert d.title == "Real Title"
    assert d.content.startswith("---\n- alpha")  # nothing silently dropped
    assert "okf_type" not in d.metadata


def test_extract_latex_equations_isolated() -> None:
    eqs = extract_latex_equations("$$a=b$$ middle $$c=d$$")
    assert eqs == ["a=b", "c=d"]


def test_extract_figure_refs_isolated() -> None:
    refs = extract_figure_refs("![](a.png) and ![alt](b.jpg) inline")
    assert refs == ["a.png", "b.jpg"]


# ---------------------------------------------------------------------------
# PDF parser — exercised only when pdfminer.six is available.

try:
    import pdfminer.high_level  # noqa: F401

    _HAS_PDFMINER = True
except ImportError:  # pragma: no cover
    _HAS_PDFMINER = False


@pytest.mark.skipif(not _HAS_PDFMINER, reason="pdfminer.six not installed")
def test_parse_pdf_handles_missing_file(tmp_path: Path) -> None:
    """A path that does not exist is logged and skipped, not raised."""
    from fractal_rag.parsers.pdf import parse_pdf

    ghost = tmp_path / "ghost.pdf"
    assert not ghost.exists()
    docs = parse_pdf(ghost)
    assert docs == []


@pytest.mark.skipif(not _HAS_PDFMINER, reason="pdfminer.six not installed")
def test_parse_pdf_skips_corrupt_file(tmp_path: Path) -> None:
    """A truncated PDF (pdfminer raises PDFSyntaxError: no /Root) yields no documents."""
    from fractal_rag.parsers.pdf import parse_pdf

    fake = tmp_path / "corrupt.pdf"
    fake.write_bytes(b"%PDF-1.4\n%fake\n")
    docs = parse_pdf(fake)
    assert docs == []


@pytest.mark.skipif(not _HAS_PDFMINER, reason="pdfminer.six not installed")
def test_parse_pdf_skips_file_on_any_extraction_error(tmp_path: Path, monkeypatch) -> None:
    """pdfminer raises many exception types on damaged files; every one of them means skip."""
    import pdfminer.high_level

    from fractal_rag.parsers.pdf import parse_pdf

    class Boom(Exception):
        pass

    def exploding_extract_text(*args, **kwargs):
        raise Boom("unexpected object structure")

    monkeypatch.setattr(pdfminer.high_level, "extract_text", exploding_extract_text)
    pdf = tmp_path / "weird.pdf"
    pdf.write_bytes(_minimal_pdf(b"text"))
    assert parse_pdf(pdf) == []


@pytest.mark.skipif(not _HAS_PDFMINER, reason="pdfminer.six not installed")
def test_parse_pdf_extracts_text_from_minimal_pdf(tmp_path: Path) -> None:
    from fractal_rag.parsers.pdf import parse_pdf

    pdf = tmp_path / "fractal_dims.pdf"
    pdf.write_bytes(_minimal_pdf(b"Hausdorff dimension of the Koch curve"))
    docs = parse_pdf(pdf)
    assert len(docs) == 1
    assert docs[0].source_type == "pdf"
    assert docs[0].title == "fractal dims"
    assert "Hausdorff" in docs[0].content
    assert docs[0].metadata["tags"] == ["quality=fallback"]


def _minimal_pdf(text: bytes) -> bytes:
    """Hand-assembled single-page PDF with one Helvetica text object and a valid xref."""
    stream = b"BT /F1 12 Tf 72 720 Td (" + text + b") Tj ET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    return bytes(out)
