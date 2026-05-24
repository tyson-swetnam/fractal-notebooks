# fractal-rag

Weaviate-backed RAG stack for the Fractal Notebooks research corpus. Exposes an MCP server (`fractal-rag serve`) and ingestion CLI (`fractal-rag ingest`) per the design spec at `docs/superpowers/specs/2026-05-23-fractal-rag-agent-design.md`.

## Install

```bash
cd fractal_rag
pip install -e ".[dev,parsers]"
```

## Quick start

```bash
# 1. Bootstrap the Weaviate schema (idempotent)
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
