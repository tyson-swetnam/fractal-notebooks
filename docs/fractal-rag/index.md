---
type: Index
title: "Fractal RAG Stack"
description: >-
  Overview of the self-hosted retrieval-augmented generation stack: Weaviate
  1.35 with a text2vec-transformers sidecar indexes 50K Constellate articles
  plus this site's notebooks and pages, queried through an MCP server by the
  fractal-explorer subagent.
resource: https://tyson-swetnam.github.io/fractal-notebooks/fractal-rag/
tags: [knowledge, rag, weaviate, mcp]
generated:
  by: human:tswetnam
  at: "2026-05-24T00:00:00Z"
status: stable
---

# Fractal RAG Stack

A self-hosted retrieval-augmented generation (RAG) stack that turns the
Fractal Notebooks research corpus — ~50K Constellate scholarly articles plus
this repository's Jupyter notebooks and documentation pages — into a vector index
you can query from Claude Code via a custom **`fractal-explorer`** subagent.

```mermaid
flowchart LR
  subgraph "Storage"
    iRODS[(CyVerse iRODS<br/>~30 GB corpus)]
  end
  subgraph "Compute (your laptop, a VM, or K3s)"
    Weaviate[(Weaviate 1.35<br/>FractalArtifact + Concept)]
    T2V[text2vec-transformers<br/>Arctic-embed-l-v2.0]
    MCP[fractal-rag<br/>MCP server]
  end
  subgraph "Client"
    CC[Claude Code]
    Agent[fractal-explorer<br/>subagent]
  end

  iRODS -->|gocmd pull| Local["/opt/tswetnam/fractal-notebooks/"]
  Local -->|fractal-rag ingest| Weaviate
  Weaviate <-->|vectorize| T2V
  MCP -->|weaviate-client v4| Weaviate
  CC -->|.mcp.json stdio| MCP
  CC --> Agent
  Agent -->|8 tools| MCP
```

## Pick your path

| If you are… | Read |
|---|---|
| A developer who wants to try the stack on a laptop without GPUs | **[Local setup](local-setup.md)** |
| An operator deploying to a CyVerse / Jetstream-2 / on-prem GPU node | **[Hosted VM (K3s)](hosted-vm.md)** |
| A researcher who already has it running and just wants to use it | **[Using the fractal-explorer agent](using-the-agent.md)** |
| Hitting an error | **[Troubleshooting](troubleshooting.md)** |

## What's in the box

| Component | Source | Purpose |
|---|---|---|
| `fractal_rag/` Python package | this repo | parsing, chunking, concept enrichment, ingest, MCP server |
| `k3s-deployment/*.yaml` | this repo | Weaviate 1.35 + GPU embedding sidecar manifests |
| `docker/fractal-rag/docker-compose.yaml` | this repo | Single-node local stack (CPU-only) |
| `.claude/agents/fractal-explorer.md` | this repo | Custom retrieval subagent definition |
| `.mcp.json` | this repo | Repo-local MCP server wiring |
| Constellate JSONL corpus | iRODS `/iplant/home/tswetnam/fractal-notebooks/` | 50K scholarly articles |

## Worked examples

Three Jupyter notebooks under [`notebooks/`](notebooks/01_quickstart.md), rendered here with their outputs,
exercise the index directly from Python — useful for prototyping queries
before you wire them into the subagent rubric:

1. [01 — Quickstart](notebooks/01_quickstart.md) — connect, list concepts, run your first hybrid search.
2. [02 — Hybrid search patterns](notebooks/02_hybrid_search.md) — `target_vector` tradeoffs, filters, `alpha` tuning.
3. [03 — Concept ontology](notebooks/03_concept_ontology.md) — walking the `Concept` side-collection and following cross-refs.

## See also

- [Design spec](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/specs/2026-05-23-fractal-rag-agent-design.md) — architecture, schema and tool-selection rubric (GitHub)
- [Verification checklist](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/specs/2026-05-23-fractal-rag-agent-verification.md) — the eight-prompt agent checklist (GitHub)
- [Knowledge bundles](../okf/index.md) — the OKF concept ontology exported from this stack's `seed.yaml`, and the proof bundle
- Package source — [`fractal_rag/`](https://github.com/tyson-swetnam/fractal-notebooks/tree/main/fractal_rag)
