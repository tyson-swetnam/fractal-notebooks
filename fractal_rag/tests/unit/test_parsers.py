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
    from fractal_rag.parsers.pdf import parse_pdf

    fake = tmp_path / "ghost.pdf"
    fake.write_bytes(b"%PDF-1.4\n%fake\n")
    docs = parse_pdf(fake)
    assert isinstance(docs, list)
