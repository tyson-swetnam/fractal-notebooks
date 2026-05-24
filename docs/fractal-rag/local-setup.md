# Local Setup (Laptop, No GPU)

This page walks you through running the entire Fractal RAG stack on a single
machine without GPUs. The local stack uses Docker Compose to run Weaviate
plus a small CPU-only embedding sidecar, and ingests a **slice** of the
corpus rather than the full 30 GB pull — enough to drive the
`fractal-explorer` subagent against real data while you iterate.

## Prerequisites

| Need | Version | Notes |
|---|---|---|
| Docker + Docker Compose v2 | recent | `docker compose version` should print v2.x |
| Python | 3.10+ | for the `fractal-rag` CLI and MCP server |
| Disk free | ~5 GB | Weaviate volume + a JSONL slice + cached embed model |
| RAM | 8 GB+ | the BGE-small CPU model fits in ~1 GB resident |
| Claude Code | latest | to use the subagent |
| (optional) `gocmd` v0.11.5+ | latest | only if you want to pull from iRODS yourself |

The default local profile ships with `baai-bge-small-en-v1.5` (~135 MB,
384-dim) instead of the GPU-only `arctic-embed-l-v2.0` from the K3s manifests.
Retrieval quality is lower on long technical passages but adequate for
exploring the surface and iterating on the agent prompt.

## 1. Bring up Weaviate + the CPU sidecar

From the repo root:

```bash
docker compose -f docker/fractal-rag/docker-compose.yaml up -d
docker compose -f docker/fractal-rag/docker-compose.yaml ps
```

Wait until both services are `running` and Weaviate reports ready:

```bash
curl -s http://localhost:8080/v1/.well-known/ready    # 200 OK
curl -s http://localhost:8080/v1/meta | python -m json.tool | grep -i text2vec
#   "text2vec-transformers": { ... }
```

## 2. Install the `fractal-rag` package

```bash
cd fractal_rag
pip install -e ".[dev,parsers]"
fractal-rag --version              # fractal-rag, version 0.1.0
fractal-rag concepts validate      # OK: 31 concepts validated
```

## 3. Point the CLI at the local Weaviate

The defaults in `fractal_rag/src/fractal_rag/config.py` target the K3s NodePort
(`30080`). For the docker-compose stack you want the standard `8080`. Export
the override once per shell:

```bash
export FRACTAL_RAG_WEAVIATE_HTTP_PORT=8080
export FRACTAL_RAG_WEAVIATE_GRPC_PORT=50051
```

Or persist them in a `.env` file at the repo root:

```bash
cat > .env <<'EOF'
FRACTAL_RAG_WEAVIATE_HTTP_PORT=8080
FRACTAL_RAG_WEAVIATE_GRPC_PORT=50051
EOF
```

## 4. Bootstrap the schema

```bash
fractal-rag schema bootstrap
# { "created": ["Concept", "FractalArtifact"], "already_present": [] }

fractal-rag schema bootstrap          # second run is idempotent
# { "created": [], "already_present": ["FractalArtifact", "Concept"] }
```

## 5. Ingest a slice

For local iteration, **skip the 30 GB iRODS pull** and ingest just the repo's
own markdown + notebooks (a few hundred chunks), plus an optional small
JSONL sample:

```bash
# Repo docs and notebooks — fast, no external corpus needed.
fractal-rag ingest --source docs
fractal-rag ingest --source notebooks
```

If you do have the JSONL on disk and want a representative subset:

```bash
# 500 Constellate articles is enough to drive every agent rubric.
fractal-rag ingest --source json --limit 500
```

Confirm:

```bash
fractal-rag status
# { "FractalArtifact": 837, "Concept": 31 }
```

You can sanity-check retrieval from the CLI without booting Claude Code:

```bash
fractal-rag query "Hausdorff dimension of the Cantor set" --limit 3
```

## 6. Wire Claude Code to the local MCP server

The repo already ships `.mcp.json` pointing at `fractal-rag serve`. Open
Claude Code in the repo root and run `/mcp` — you should see `fractal-rag`
listed as connected. Then invoke the subagent:

```text
> Use the fractal-explorer agent: "What does the corpus say about
  diffusion-limited aggregation in biological systems?"
```

See [Using the fractal-explorer agent](using-the-agent.md) for the full tool
rubric and example transcripts.

## 7. Try the worked notebooks

The three notebooks under
[`docs/fractal-rag/notebooks/`](notebooks/01_quickstart.ipynb) connect
directly to the local Weaviate over the same `8080`/`50051` ports and give
you a Python-level handle on the index — useful when you want to prototype a
new query pattern before teaching it to the agent.

## Teardown

```bash
docker compose -f docker/fractal-rag/docker-compose.yaml down          # keep data volume
docker compose -f docker/fractal-rag/docker-compose.yaml down -v       # nuke data volume
```

## Where to go next

- Run more queries via the agent → [Using the fractal-explorer agent](using-the-agent.md)
- Move to the full GPU deployment → [Hosted VM (K3s)](hosted-vm.md)
- Something broke → [Troubleshooting](troubleshooting.md)
