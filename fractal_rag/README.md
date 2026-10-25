# fractal-rag

Weaviate-backed RAG stack for the Fractal Notebooks research corpus. Exposes an MCP server (`fractal-rag serve`) and ingestion CLI (`fractal-rag ingest`) per the design spec at `specs/2026-05-23-fractal-rag-agent-design.md` (repo root).

## Install

```bash
cd fractal_rag
pip install -e ".[dev,parsers]"
```

## Quick start

```bash
# 1. Bootstrap the Weaviate schema (idempotent; also adds newly declared properties)
fractal-rag schema bootstrap

# 2. Pull the corpus from iRODS
fractal-rag pull

# 3. Ingest everything
fractal-rag ingest --source all

# 4. Inspect counts
fractal-rag status

# 5. Run the MCP server (stdio transport — wired via .mcp.json)
fractal-rag serve
```

## Configuration

All settings are `FRACTAL_RAG_*` environment variables (see `config.py`). Two matter
for a local run:

- `FRACTAL_RAG_REPO_ROOT` - checkout of this repository; the `docs` source reads
  `docs/**/*.md` (Zensical pages with OKF v0.2 frontmatter) plus the canonical
  `okf/concepts` and `okf/proofs` bundles, and the `notebooks` source scans
  `docs/**/*.ipynb` in addition to the iRODS mirror. A missing path yields 0 documents
  rather than an error, so set it explicitly: `export FRACTAL_RAG_REPO_ROOT=$PWD`.
- `FRACTAL_RAG_CORPUS_ROOT` - the local iRODS mirror (`fractal-rag pull`).

Pages excluded from the site build (`exclude_docs` / `draft_docs` in `zensical.toml`),
the `docs/okf/concepts/` and `docs/okf/proofs/` build copies (the hand-written
`docs/okf/index.md` is indexed), rendered notebook pages (a `.md` next to its `.ipynb`)
and change logs (`log.md` at any depth) are not indexed as markdown. Notebooks are
de-duplicated by content hash across the repo and the iRODS mirror (the repo copy wins),
and cells of a notebook that has a rendered sibling page carry that page's `resource`.

### Schema changes on an existing index

`FractalArtifact` gained the `resource` property (the public page URL that
`fractal-rag ingest` now writes on every chunk). An index bootstrapped before that
needs one of:

```bash
fractal-rag schema bootstrap     # keeps the data; adds the missing property, reports it
                                 # under "properties_added", then `fractal-rag ingest`
                                 # fills it in (inserts are idempotent upserts)
fractal-rag schema bootstrap --drop && fractal-rag ingest --source all   # rebuild from scratch
```

## OKF concept bundle

`okf/concepts/` is generated from `src/fractal_rag/concepts/seed.yaml`:

```bash
fractal-rag okf export --out ../okf/concepts            # regenerate (stamps changed concepts with today)
fractal-rag okf export --out ../okf/concepts --check    # CI drift check: exit 1 when the bundle is stale
python -m fractal_rag.okf_export --out ../okf/concepts  # same, PyYAML-only (no Weaviate needed)
```

Options: `--seed`, `--date YYYY-MM-DD`, `--site-url`, `--prune-unknown`. The exporter deletes
only stale files it generated itself (never a `log.md`); any other Markdown file under `--out`
makes it refuse (exit 2) unless `--prune-unknown` is given. See `../okf/README.md`.

## Layout

```
src/fractal_rag/
  cli.py            # click entrypoint
  config.py         # Pydantic settings
  client.py         # Weaviate v4 client wrapper
  schema.py         # idempotent schema bootstrap
  concepts/         # seed.yaml + loader
  parsers/          # json_corpus, notebook, markdown, pdf
  chunk.py          # token-aware hierarchical chunker
  enrich.py         # concept tagging + summary heuristic
  ingest.py         # orchestrator
  pull.py           # gocmd wrapper
  server/mcp.py     # 8-tool MCP server
```
