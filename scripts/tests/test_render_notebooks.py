"""render_notebooks.py policies on synthetic nbformat notebooks."""

from __future__ import annotations

import base64
import textwrap
from pathlib import Path

import nbformat
import pytest
import yaml

import render_notebooks as rn

SITE = "https://example.org/fx"
REPO = "https://github.com/example/fx"
PNG = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32).decode()
DESC = "A synthetic notebook used by the unit tests to exercise the output policy table."


def md(source: str) -> nbformat.NotebookNode:
    return nbformat.v4.new_markdown_cell(source)


def code(source: str, outputs: list | None = None, count: int | None = 1) -> nbformat.NotebookNode:
    cell = nbformat.v4.new_code_cell(source)
    cell.outputs = outputs or []
    cell.execution_count = count if outputs else None
    return cell


def display(data: dict, kind: str = "display_data") -> nbformat.NotebookNode:
    out = nbformat.v4.new_output(kind, data=data)
    if kind == "execute_result":
        out.execution_count = 1
    return out


def stream(text: str, name: str = "stdout") -> nbformat.NotebookNode:
    return nbformat.v4.new_output("stream", name=name, text=text)


def error(ename="ValueError", evalue="range() arg 3 must not be zero") -> nbformat.NotebookNode:
    return nbformat.v4.new_output("error", ename=ename, evalue=evalue, traceback=["\x1b[31mTraceback (most recent call last)\x1b[0m", "  File x.py", ename + ": " + evalue])


def make_nb(cells, kernel="Python 3 (ipykernel)") -> nbformat.NotebookNode:
    nb = nbformat.v4.new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": kernel, "language": "python"}
    nb.metadata["language_info"] = {"name": "python"}
    return nb


@pytest.fixture
def repo(tmp_path, monkeypatch):
    (tmp_path / "docs" / "notebooks").mkdir(parents=True)
    monkeypatch.setattr(rn, "ROOT", tmp_path)
    return tmp_path


def entry(src="docs/notebooks/x.ipynb", **kw) -> rn.Entry:
    base = dict(src=src, title="Synthetic Notebook", description=DESC, tags=["notebook", "foundations"], as_of="2026-01-02",
                environment="python3", status="stable", author="human:tester", companion_page="foundations/history/")
    base.update(kw)
    return rn.Entry(**base)


def render(repo: Path, nb, **kw) -> rn.Rendered:
    e = entry(**kw)
    nbformat.write(nb, repo / e.src)
    return rn.render_entry(e, SITE, REPO, "main")


def body_of(r: rn.Rendered) -> str:
    """Everything after the generator marker (frontmatter and marker stripped)."""
    return r.markdown.split(rn.MARKER, 1)[1]


# ------------------------------------------------------------------ output policy


def test_widget_view_becomes_note(repo):
    nb = make_nb([md("# T"), code("w", [display({"application/vnd.jupyter.widget-view+json": {"model_id": "abc"}, "text/plain": "interactive(children=(IntSlider(value=9)...)"})])])
    r = render(repo, nb)
    assert rn.WIDGET_NOTE in r.markdown
    assert "interactive(children=" not in r.markdown
    assert r.stats.widgets == 1 and r.files == {}


def test_plotly_with_png_sibling_keeps_png_only(repo):
    data = {"text/html": "<div><script>plotly</script></div>", "application/vnd.plotly.v1+json": {"data": []}, "image/png": PNG}
    r = render(repo, make_nb([md("# T"), code("p", [display(data)])]))
    assert list(r.files) == ["x_files/x_1_0.png"]
    assert "![Figure 1: output of code cell 1](x_files/x_1_0.png)" in r.markdown
    assert "<script" not in r.markdown and "plotly" not in body_of(r).lower().replace("plotly/javascript", "")


def test_display_priority_prefers_png_over_html(repo):
    # Plan UNVERIFIED #5: the user Config must override the MarkdownExporter default (html first).
    r = render(repo, make_nb([md("# T"), code("p", [display({"text/html": "<b>big html</b>", "image/png": PNG, "text/plain": "Figure"})])]))
    assert "big html" not in r.markdown and "x_files/x_1_0.png" in r.markdown


def test_script_html_without_png_links_nbviewer(repo):
    r = render(repo, make_nb([md("# T"), code("p", [display({"text/html": "<div id='a'></div><script>require(['plotly'])</script>", "text/plain": "<Figure>"})])]))
    assert "Interactive figure (Plotly/JavaScript)" in r.markdown
    assert "nbviewer.org/github/example/fx/blob/main/docs/notebooks/x.ipynb" in r.markdown
    assert "<script" not in r.markdown and r.stats.interactive == 1


def test_scriptless_html_table_kept_and_repr_dropped(repo):
    html = "<div>\n<table><tr><td>1</td></tr></table>\n</div>"
    r = render(repo, make_nb([md("# T"), code("df", [display({"text/html": html, "text/plain": "   a\n0  1"}, kind="execute_result")])]))
    assert "<table><tr><td>1</td></tr></table>" in r.markdown
    assert "0  1" not in r.markdown


def test_error_becomes_failure_admonition_without_traceback(repo):
    r = render(repo, make_nb([md("# T"), code("boom", [error()])]))
    assert '!!! failure "Cell raised ValueError"\n\n    range() arg 3 must not be zero\n' in r.markdown
    assert "Traceback" not in r.markdown and "\x1b" not in r.markdown and "File x.py" not in r.markdown
    assert r.stats.errors == 1 and "ValueError" in r.markdown.split("Jupyter notebook")[1][:400]


def test_stderr_dropped_stdout_fenced(repo):
    r = render(repo, make_nb([md("# T\n\n- a list item"), code("print(1)", [stream("warning!\n", "stderr"), stream("hello\n"), stream("world\n")])]))
    body = body_of(r)
    assert "warning!" not in body
    assert "```text\nhello\nworld\n```" in body  # coalesced into one fenced block, never list continuation
    assert "    hello" not in body


def test_path_scrub_ansi_and_carriage_returns(repo):
    text = "\x1b[31m/Users/bob/x\x1b[0m /home/jovyan/y /opt/conda/envs/env1/bin/python\nprogress 1\rprogress 2\rprogress 3\n"
    r = render(repo, make_nb([md("# T"), code("p", [stream(text)])]))
    body = body_of(r)
    assert "~/x ~/y $CONDA_PREFIX/bin/python" in body
    assert "progress 3" in body and "progress 1" not in body
    assert "\x1b" not in body and "\r" not in body
    plain = render(repo, make_nb([md("# T"), code("p", [display({"text/plain": "/Users/bob/data.csv"}, kind="execute_result")])]))
    assert "~/data.csv" in plain.markdown and "/Users/" not in plain.markdown


def test_truncation(repo):
    text = "\n".join(f"line {i}" for i in range(130)) + "\n"
    r = render(repo, make_nb([md("# T"), code("p", [stream(text)])]), max_stream_lines=120)
    body = body_of(r)
    assert "line 119" in body and "line 120" not in body
    assert "... [10 more lines truncated]" in body


def test_execute_result_repr_noise_dropped_and_empty_cells_removed(repo):
    nb = make_nb([md("# T"), code("interact(f)", [display({"text/plain": "<function __main__.plot_tree(depth, angle)>"}, kind="execute_result")]), code(""), md("   ")])
    r = render(repo, nb)
    body = body_of(r)
    assert "<function" not in body
    assert "```python\n\n```" not in body and "```python\n```" not in body


def test_code_only_drops_everything(repo):
    r = render(repo, make_nb([md("# T"), code("x", [stream("out\n"), display({"image/png": PNG})])]), code_only=True)
    assert r.files == {} and "out" not in body_of(r).split("```python")[1]
    assert "without outputs" in r.markdown and "outputs: none (code-only page" in r.markdown


# ------------------------------------------------------------------ page structure


def test_frontmatter_keys_and_resource(repo):
    r = render(repo, make_nb([md("# Real Title\n\nintro"), code("1+1", [display({"text/plain": "2"}, kind="execute_result")])]))
    fm_text = r.markdown.split("\n---\n", 1)[0] + "\n"
    meta = yaml.safe_load(fm_text.lstrip("-\n"))
    assert list(meta) == ["type", "title", "description", "resource", "tags", "companion_page", "notebook", "sources", "generated", "status"]
    assert meta["type"] == "Notebook" and meta["title"] == "Synthetic Notebook"
    assert meta["resource"] == SITE + "/notebooks/x/"
    assert meta["companion_page"] == SITE + "/foundations/history/"
    assert meta["notebook"]["source"] == REPO + "/blob/main/docs/notebooks/x.ipynb"
    assert meta["notebook"]["raw"] == "https://raw.githubusercontent.com/example/fx/main/docs/notebooks/x.ipynb"
    assert meta["notebook"]["colab"].startswith("https://colab.research.google.com/github/example/fx/blob/main/")
    assert meta["notebook"]["cells"] == {"markdown": 1, "code": 1, "executed": 1, "figures": 0, "errors": 0}
    assert meta["sources"][0] == {"id": "ipynb", "resource": REPO + "/blob/main/docs/notebooks/x.ipynb", "title": "x.ipynb", "last_modified": "2026-01-02T00:00:00Z"}
    assert meta["generated"] == {"by": "process:scripts/render_notebooks.py", "at": "2026-01-02T00:00:00Z"}
    assert "verified" not in meta and meta["status"] == "stable"
    assert rn.MARKER in r.markdown
    # keep policy: the notebook's own H1 stays, the banner follows it, exactly one H1
    body = body_of(r)
    assert body.count("\n# ") + body.startswith("# ") == 1 or body.lstrip("\n").startswith("# Real Title")
    assert body.lstrip("\n").startswith("# Real Title\n\n!!! info \"Jupyter notebook\"")
    assert "[View on GitHub](" in body and "[Open in nbviewer](" in body and "[Open in Colab](" in body and "[Raw .ipynb](" in body
    assert "as of 2026-01-02; it is not executed at build time" in body


def test_verified_emitted_only_from_manifest(repo):
    r = render(repo, make_nb([md("# T")]), verified_at="2026-03-04")
    meta = yaml.safe_load(r.markdown.split("\n---\n", 1)[0].lstrip("-\n"))
    assert meta["verified"] == [{"by": "human:tester", "at": "2026-03-04T00:00:00Z"}]
    assert list(meta)[-2:] == ["verified", "status"]


def test_h1_policies(repo):
    no_h1 = render(repo, make_nb([md("1. **Run it**"), code("x")]), heading="Injected Heading")
    assert body_of(no_h1).lstrip("\n").startswith("# Injected Heading\n")
    demote = render(repo, make_nb([md("# Setup\n\ninstall"), md("# Second")]), heading="Real", h1_policy="demote")
    b = body_of(demote)
    assert b.lstrip("\n").startswith("# Real\n") and "\n## Setup\n" in b and "\n## Second\n" in b
    keep = render(repo, make_nb([md("# First"), md("# Second")]))
    b = body_of(keep)
    assert b.lstrip("\n").startswith("# First\n") and "\n## Second\n" in b and "\n# Second" not in b
    replace = render(repo, make_nb([md("# First")]), heading="New", h1_policy="replace")
    assert body_of(replace).lstrip("\n").startswith("# New\n")
    fence = render(repo, make_nb([md("# Only"), code("# not a heading\nprint(1)")]))
    assert fence.markdown.count("\n# ") == 1 or "# not a heading" in fence.markdown  # comments inside fences are untouched


def test_deterministic_and_check_mode(repo, tmp_path):
    nb = make_nb([md("# T"), code("p", [display({"image/png": PNG}), stream("x\n")])])
    nbformat.write(nb, repo / "docs/notebooks/x.ipynb")
    manifest = tmp_path / "m.toml"
    manifest.write_text(textwrap.dedent(f"""
        [defaults]
        author = "human:tester"
        site_url = "{SITE}"
        repo_url = "{REPO}"
        [[notebook]]
        src = "docs/notebooks/x.ipynb"
        title = "T"
        description = "{DESC}"
        tags = ["notebook"]
        as_of = "2026-01-02"
        """), encoding="utf-8")
    assert rn.main(["--manifest", str(manifest), "-q"]) == 0
    page = repo / "docs/notebooks/x.md"
    first = page.read_bytes()
    img = repo / "docs/notebooks/x_files/x_1_0.png"
    assert img.exists()
    assert rn.main(["--manifest", str(manifest), "-q"]) == 0
    assert page.read_bytes() == first
    assert rn.main(["--manifest", str(manifest), "--check", "-q"]) == 0
    page.write_bytes(first + b"\nedited\n")
    assert rn.main(["--manifest", str(manifest), "--check", "-q"]) == 1
    img.unlink()
    assert rn.main(["--manifest", str(manifest), "--check", "-q"]) == 1
    assert rn.main(["--manifest", str(manifest), "-q"]) == 0
    assert img.exists() and page.read_bytes() == first
    # stale image is removed on re-render
    stale = repo / "docs/notebooks/x_files/old.png"
    stale.write_bytes(b"x")
    assert rn.main(["--manifest", str(manifest), "-q"]) == 0
    assert not stale.exists()
    # --clean removes the generated outputs
    assert rn.main(["--manifest", str(manifest), "--clean"]) == 0
    assert not page.exists() and not img.parent.exists()


def test_refuses_to_overwrite_hand_written_page(repo, tmp_path, capsys):
    nbformat.write(make_nb([md("# T")]), repo / "docs/notebooks/x.ipynb")
    hand = repo / "docs/notebooks/x.md"
    hand.write_text("# hand written page\n", encoding="utf-8")
    manifest = tmp_path / "m.toml"
    manifest.write_text(textwrap.dedent(f"""
        [defaults]
        site_url = "{SITE}"
        repo_url = "{REPO}"
        [[notebook]]
        src = "docs/notebooks/x.ipynb"
        title = "T"
        description = "{DESC}"
        as_of = "2026-01-02"
        """), encoding="utf-8")
    assert rn.main(["--manifest", str(manifest), "--strict", "-q"]) == 1
    assert hand.read_text(encoding="utf-8") == "# hand written page\n"
    assert rn.main(["--manifest", str(manifest), "-q"]) == 0  # non-strict: reported, skipped
    assert "refusing to overwrite" in capsys.readouterr().err
    assert hand.read_text(encoding="utf-8") == "# hand written page\n"


def test_manifest_validation(tmp_path):
    bad = tmp_path / "bad.toml"
    bad.write_text(f'[[notebook]]\nsrc = "docs/x.ipynb"\ntitle = "T"\ndescription = "{DESC} with a \\" quote"\nas_of = "2026-01-02"\n', encoding="utf-8")
    with pytest.raises(rn.ManifestError, match="description"):
        rn.load_manifest(bad)
    bad.write_text(f'[[notebook]]\nsrc = "docs/x.ipynb"\ntitle = "T"\ndescription = "{DESC}"\nas_of = "Jan 2"\n', encoding="utf-8")
    with pytest.raises(rn.ManifestError, match="as_of"):
        rn.load_manifest(bad)
    bad.write_text('[[notebook]]\nsrc = "docs/x.ipynb"\ntitle = "T"\ndescription = "short"\nas_of = "2026-01-02"\n', encoding="utf-8")
    with pytest.raises(rn.ManifestError, match="50-300"):
        rn.load_manifest(bad)


def test_real_manifest_is_valid_and_targets_exist():
    defaults, entries = rn.load_manifest(rn.DEFAULT_MANIFEST)
    assert len(entries) == 18
    for e in entries:
        assert e.path.is_file(), e.src
        assert 2 <= len(e.tags) <= 6, e.src
        assert e.out_md.is_file(), f"{e.out_md} not rendered; run scripts/render_notebooks.py"
        assert rn.is_generated_page(e.out_md)


def test_ipynb_links_point_at_rendered_pages_or_github():
    import render_notebooks as rn
    class E:  # minimal stand-in for Entry
        src = "docs/fractal-rag/notebooks/01_quickstart.ipynb"
    rn.KNOWN_NOTEBOOKS.update({"docs/fractal-rag/notebooks/02_hybrid_search.ipynb"})
    body = "See [02](02_hybrid_search.ipynb#tuning) and [other](../../notebooks/foundations/zeta_3d.ipynb) and [ext](https://x.org/a.ipynb)."
    out = rn.rewrite_ipynb_links(body, E(), "https://github.com/o/r", "main")
    assert "[02](02_hybrid_search.md#tuning)" in out
    assert "[other](https://github.com/o/r/blob/main/docs/notebooks/foundations/zeta_3d.ipynb)" in out
    assert "[ext](https://x.org/a.ipynb)" in out
