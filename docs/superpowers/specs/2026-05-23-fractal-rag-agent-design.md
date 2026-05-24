# Spec — Fractal RAG Stack (v1)

- **Date:** 2026-05-23
- **Status:** Approved for implementation planning
- **Author:** Tyson Swetnam (tswetnam@arizona.edu) with Claude Code (Opus 4.7)
- **Sibling specs (future):**
  - Spec #2 — AVU Metadata Layer (mesa-mcp + mesa-ducklake integration)
  - Spec #3 — CAISP Hypothesis-Test Integration (AI co-scientist)

---

## 1. Overview

A self-contained, locally-hosted research-RAG stack for fractal mathematics literature, running on a single-node K3s cluster on the user's workstation. It comprises:

1. **Weaviate 1.35** vector database with a local `text2vec-transformers` embedding sidecar
2. A Python ingestion pipeline (`fractal_rag` package) that pulls a JSON corpus from the CyVerse Data Store, parses Jupyter notebooks, MkDocs markdown, and reference PDFs, hierarchically chunks them, tags canonical fractal concepts, and bulk-loads Weaviate
3. A custom **Python MCP server** exposing eight `fractal_*` tools tailored to fractal-research RAG
4. A `fractal-explorer` Claude Code subagent that reasons over those tools to answer multi-turn research questions with source citations

The user's success scenario: from a fresh shell, open Claude Code in this repo, ask a question like *"What's the predicted mass dimension for vascular plants under WBE, and how does that compare to Lapidus's complex-dimension framework?"*, and receive a cited, conceptually-grounded answer drawn from the local Weaviate index — and be able to use `/loop` to iterate on follow-up research questions.

## 2. Goals and success criteria

### Goals
- Stand up a reproducible local Weaviate stack on K3s with GPU-accelerated local embeddings.
- Provide a single Python CLI (`fractal-rag`) for pulling, parsing, chunking, and ingesting four content types.
- Expose retrieval over MCP with tool ergonomics tuned for fractal research (concept maps, citation context, hybrid search with filters).
- Ship a `fractal-explorer` subagent definition that any Claude Code session in this repo can invoke.
- Establish architectural foundations that Spec #2 (AVU metadata layer) and Spec #3 (CAISP) can build on without re-architecture.

### Done = all of:
1. `kubectl -n ai-workloads get pods` shows `weaviate`, `t2v-transformers` healthy.
2. `fractal-rag ingest --source all` completes successfully and `fractal-rag status` reports objects across the four `source_type` values plus `Concept` records.
3. From a fresh shell in the repo, `claude` with the project's `.mcp.json` enabled answers an example research question (see §8 verification checklist) with a cited result.
4. The `fractal-explorer` subagent performs ≥3 retrievals for a multi-step research prompt and synthesizes a structured answer.
5. The 8-item manual verification checklist (§8) passes.

### Non-goals (v1)
- LLM-based concept extraction (string-match only in v1)
- Cross-encoder reranking
- Multi-modal/figure embeddings
- iRODS AVU writes (Spec #2)
- Web ingestion (Spec #2)
- Multi-user auth (anonymous local dev only)
- Observability stack (Spec #3 will adopt CAISP's pattern when needed)
- AI co-scientist hypothesis testing (Spec #3)

## 3. Constraints and environment

- **Hardware (local workstation, verified):** 3× NVIDIA A100 80GB, AMD EPYC 7713 (256 vCPU), 503 GB RAM, 21 TB disk (5.5 TB free on `/opt`).
- **Software (verified):** `gocmd` v0.11.5 with iRODS auth at `~/.irods/`. NVIDIA driver 560.35.03, CUDA 12.6.
- **Repo policy:** the project `CLAUDE.md` requires committing after every successful prompt that modifies files. Implementation will follow this rule.
- **Data source:** JSON corpus at `/iplant/home/tswetnam/fractal-notebooks/` on CyVerse Data Store (not in iRODS shared, so must be pulled via `gocmd`, not via the iRODS MCP server).
- **Local data target:** `/opt/tswetnam/fractal-notebooks/`.
- **K3s:** already installed on workstation per existing `k3s-deployment/` manifests; we will refresh, not redeploy from scratch.

## 4. Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ User workstation (local)                                            │
│                                                                     │
│  ┌────────────────────┐       ┌──────────────────────────────────┐  │
│  │  Claude Code (CLI) │──MCP──│ fractal_rag.server.mcp (stdio)   │  │
│  │  + fractal-        │ tools └────────────────┬─────────────────┘  │
│  │  explorer subagent │                        │ weaviate-client v4 │
│  └────────────────────┘                        ▼                    │
│                                                                     │
│         ┌─────────────────────────  K3s (ai-workloads ns) ────────┐ │
│         │                                                         │ │
│         │  ┌────────────────────┐   ┌────────────────────────┐    │ │
│         │  │ Weaviate 1.35      │──▶│ t2v-transformers       │    │ │
│         │  │ (REST :8080,       │   │ sidecar                │    │ │
│         │  │  gRPC :50051,      │   │ (Arctic-embed-l-v2.0)  │    │ │
│         │  │  PVC 50Gi)         │   │ GPU 0                  │    │ │
│         │  └─────────┬──────────┘   └────────────────────────┘    │ │
│         │            ▲                                            │ │
│         │            │ batch import                               │ │
│         └────────────┼────────────────────────────────────────────┘ │
│                      │                                              │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ fractal_rag CLI (Python, in repo's venv)                    │    │
│  │   pull → parse → chunk → enrich → batch import              │    │
│  │   reads: /opt/tswetnam/fractal-notebooks/   (gocmd pulls)   │    │
│  │   reads: ./docs/notebooks/, ./docs/, ./papers/              │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

## 5. Infrastructure (K3s)

All in `ai-workloads` namespace, in the repo's `k3s-deployment/` directory.

### 5.1 Changes to existing manifests

| File | Change |
|------|--------|
| `weaviate-deployment.yaml` | Image bump `1.27.0` → `1.35.x` (latest patch). Add env `ENABLE_MODULES=text2vec-transformers`, `DEFAULT_VECTORIZER_MODULE=text2vec-transformers`, `TRANSFORMERS_INFERENCE_API=http://t2v-transformers.ai-workloads.svc.cluster.local:8080`. Bump resource limits to CPU 8 / 16 Gi. |
| `weaviate-pvc.yaml` | Increase storage `10Gi` → `50Gi`. |
| `weaviate-service.yaml` | No change (NodePort 30080 still works). |
| `jupyterlab-to-weaviate.yaml` | Network policy unchanged. |

### 5.2 New manifests

| File | Purpose |
|------|---------|
| `t2v-transformers-deployment.yaml` | Deployment running `cr.weaviate.io/semitechnologies/transformers-inference:snowflake-snowflake-arctic-embed-l-v2.0` (or equivalent), single replica, requesting `nvidia.com/gpu: 1`, node selector for A100. Liveness/readiness probes on `:8080/.well-known/ready`. |
| `t2v-transformers-service.yaml` | ClusterIP service exposing port 8080 inside the namespace. |

### 5.3 Embedding model choice

**Default:** `Snowflake/snowflake-arctic-embed-l-v2.0` (568M params, MTEB-leading, long context support up to 8192 tokens, multilingual).

**Documented alternative (one-flag swap):** `nomic-ai/nomic-embed-text-v2-moe` — a battle-tested fallback if Arctic v2 underperforms on the fractal domain or operational issues arise.

Both fit comfortably on one A100 80GB with substantial headroom for concurrent batch inference.

### 5.4 Storage and durability

- Local-path provisioner for the Weaviate PVC.
- PVC reclaim policy stays `Delete` for v1 (re-ingest is fast). A backup design lands in Spec #2.

## 6. Weaviate schema (Approach C: polymorphic + concept side-collection)

### 6.1 `FractalArtifact` collection

```python
properties = [
    Property("source_type", DataType.TEXT),      # paper | notebook_cell | doc_page | json_entry
    Property("source_uri",  DataType.TEXT),      # iRODS path, local path, or DOI
    Property("parent_id",   DataType.TEXT),      # UUID of parent doc (for hierarchical chunks)
    Property("chunk_index", DataType.INT),
    Property("title",       DataType.TEXT),
    Property("summary",     DataType.TEXT),      # short auto-summary for fast scan
    Property("content",     DataType.TEXT),      # the chunk text
    Property("authors",     DataType.TEXT_ARRAY),
    Property("year",        DataType.INT),
    Property("latex_equations", DataType.TEXT_ARRAY),
    Property("figure_refs", DataType.TEXT_ARRAY),
    Property("tags",        DataType.TEXT_ARRAY),
    Property("ingested_at", DataType.DATE),
]

references = [
    ReferenceProperty("concepts", target_collection="Concept"),
]

vectorizer_config = [
    Configure.NamedVectors.text2vec_transformers(
        name="content_vec",
        source_properties=["content"],
        vectorize_collection_name=False,
    ),
    Configure.NamedVectors.text2vec_transformers(
        name="title_vec",
        source_properties=["title"],
        vectorize_collection_name=False,
    ),
    Configure.NamedVectors.text2vec_transformers(
        name="summary_vec",
        source_properties=["summary"],
        vectorize_collection_name=False,
    ),
]

inverted_index_config = Configure.inverted_index(
    bm25_b=0.75, bm25_k1=1.2,
    index_property_length=True,
    index_timestamps=True,
)
```

### 6.2 `Concept` collection

```python
properties = [
    Property("name",       DataType.TEXT),
    Property("aliases",    DataType.TEXT_ARRAY),
    Property("definition", DataType.TEXT),
    Property("domain",     DataType.TEXT),       # geometry | biology | dynamics | spectral | ...
    Property("hausdorff_dim_range", DataType.TEXT),
    Property("related_concept_ids", DataType.TEXT_ARRAY),  # other Concept UUIDs
]

vectorizer_config = [
    Configure.NamedVectors.text2vec_transformers(name="name_vec", source_properties=["name"]),
    Configure.NamedVectors.text2vec_transformers(name="definition_vec", source_properties=["definition"]),
]
```

### 6.3 Chunking strategy

- **Hierarchical:** document → ~500-token chunks with 50-token overlap.
- Each chunk gets `parent_id` pointing to the document-level record (which itself is also a chunk, with `chunk_index = -1`, holding the title/summary/full-doc concepts).
- Sentence-boundary aware (no mid-sentence splits).
- Tokenizer matches the embedding model's tokenizer (Arctic v2 uses BERT WordPiece; we use the model's tokenizer via `tokenizers` lib).

### 6.4 Concept seeding

- Bootstrap with ~30 hand-curated canonical concepts in `fractal_rag/concepts/seed.yaml`, drawn from `docs/foundations/`, `docs/glossary.md`, and the user's existing notebooks.
- Initial domains: `geometry`, `dynamics`, `biology`, `spectral`, `algorithms`, `physics`.
- v1 concept extraction is **string-match over aliases** (case-insensitive, word-boundary, longest-match-first).
- LLM-based extraction is deferred to Spec #2 once we have feedback on the v1 quality.

## 7. Ingestion pipeline (`fractal_rag` Python package)

### 7.1 Package layout

```
fractal_rag/
├── pyproject.toml
├── README.md
├── src/fractal_rag/
│   ├── __init__.py
│   ├── cli.py                    # `fractal-rag {pull|ingest|query|status|serve}`
│   ├── config.py                 # Pydantic settings, env + YAML
│   ├── client.py                 # Weaviate v4 client wrapper
│   ├── schema.py                 # idempotent schema bootstrap
│   ├── concepts/
│   │   ├── seed.yaml
│   │   └── loader.py
│   ├── parsers/
│   │   ├── json_corpus.py        # parses the CyVerse JSON
│   │   ├── notebook.py           # nbformat → text + code cell chunks
│   │   ├── markdown.py           # mistune + LaTeX equation extraction
│   │   └── pdf.py                # marker (default); pdfminer.six fallback
│   ├── chunk.py                  # hierarchical, token-aware chunker
│   ├── enrich.py                 # concept tagging (string match), summary gen
│   ├── ingest.py                 # orchestrator
│   ├── pull.py                   # gocmd wrapper for iRODS pull
│   └── server/
│       └── mcp.py                # MCP server (§9)
└── tests/
    ├── unit/
    │   ├── test_chunk.py
    │   ├── test_parsers.py
    │   ├── test_concepts.py
    │   └── test_schema.py
    └── integration/
        └── test_ingest_smoke.py   # testcontainers-weaviate
```

### 7.2 CLI subcommands

| Command | Behavior |
|---------|----------|
| `fractal-rag pull` | Idempotent `gocmd get -fr /iplant/home/tswetnam/fractal-notebooks/ /opt/tswetnam/fractal-notebooks/`. Uses gocmd's built-in checksum-based skip. |
| `fractal-rag ingest --source {json|notebooks|docs|pdfs|all}` | Parse → chunk → enrich → batch import. Progress bar via `rich`. Resume-on-failure state in `~/.cache/fractal-rag/state.json`. |
| `fractal-rag query "<text>" [--source-type X] [--alpha 0.5] [--limit 10]` | CLI hybrid search, prints results in a table. For debugging without the MCP. |
| `fractal-rag status` | Object counts per `source_type`; concept count; last-ingested timestamp; Weaviate health. |
| `fractal-rag serve` | Launches the MCP server over stdio (used by Claude Code via `.mcp.json`). |

### 7.3 Ingest orchestration

For each `source_type`:
1. **Discover** files (recursive globs over the configured paths).
2. **Parse** to a list of `RawDocument` dataclasses (`title`, `content`, `metadata`, `source_uri`).
3. **Chunk** into a list of `Chunk` dataclasses (token-bounded with overlap, parent-aware).
4. **Enrich**: string-match concepts; generate per-chunk summary via heuristic (first sentence + the sentence containing the strongest concept hit; deterministic — no LLM in v1).
5. **Batch import** via `client.batch.dynamic()` with 100-object batches.
6. **Concept cross-refs** added in a second pass once Concept UUIDs are known.
7. **Failure handling:** per-object retry (3×, exponential backoff). Final failures appended to `failed_objects.jsonl` with reason; ingest continues. No silent swallowing.

### 7.4 Hierarchical chunk semantics

- Doc-level record: `chunk_index=-1`, `parent_id=null`, `content=<full doc text or summary>`, all concepts gathered from children.
- Child chunks: `chunk_index=0..N`, `parent_id=<doc UUID>`, `content=<chunk text>`, concepts limited to the chunk's own matches.
- Retrieval can request either chunks (default), or chunks + parent context.

## 8. MCP server (`fractal_rag.server.mcp`)

### 8.1 Transport and configuration

- **Transport:** stdio.
- **Launcher:** `fractal-rag serve` (also runnable as `python -m fractal_rag.server.mcp`).
- **Wiring:** repo-local `.mcp.json` declares the server; Claude Code auto-loads when opened in this repo.
- **SDK:** official Anthropic Python MCP SDK (`pip install mcp`).
- **Config source order:** CLI flag → env (`FRACTAL_RAG_*`) → `~/.config/fractal-rag/config.yaml` → defaults (`http://localhost:8080`, anonymous).

### 8.2 Tools

| Tool | Args (typed) | Returns |
|------|--------------|---------|
| `fractal_search` | `query: str, limit: int = 10, source_type: str? = None, year_range: tuple[int, int]? = None, alpha: float = 0.5` | List of `{object_id, source_uri, score, title, snippet, parent_id, source_type, concepts}` |
| `fractal_neighbors` | `object_id: str, limit: int = 10` | Same shape as `fractal_search` |
| `fractal_get` | `object_id: str, include_chunks: bool = False` | Full object + (optionally) sibling chunks |
| `fractal_aggregate` | `group_by: str, filter: dict? = None` | List of `{value, count}` |
| `fractal_concept_search` | `query: str, limit: int = 10` | List of `{concept_id, name, aliases, definition, domain, score}` |
| `fractal_concept_map` | `concept_name: str, depth: int = 1` | `{nodes: [Concept], edges: [{from, to}]}` |
| `fractal_citation_context` | `object_id: str` | Formatted citation block: surrounding chunks, equations, concepts |
| `fractal_status` | (none) | `{weaviate_health, object_counts, concept_count, last_ingested_at}` |

### 8.3 Hard contracts

- All tools return **structured JSON only** — no free text.
- Every retrieval result includes `object_id`, `source_uri`, and a `score` so the agent can always cite and rank.
- Errors are raised as `ToolError(code, message, details?)` with a stable `code` enum: `not_found`, `weaviate_unreachable`, `invalid_filter`, `invalid_object_id`, `weaviate_timeout`.
- No silent failures: any partial degradation (e.g., concept cross-ref lookup fails) returns the available data with a `warnings: [...]` field.

### 8.4 Performance targets

- `fractal_search` p95 latency under 1 s (single-shot retrieval).
- `fractal_aggregate` p95 under 2 s.
- `fractal_concept_map(depth=2)` under 3 s.

## 9. Subagent: `fractal-explorer`

### 9.1 File: `.claude/agents/fractal-explorer.md`

```yaml
---
name: fractal-explorer
description: Use proactively for any question about fractal mathematics, dimensions, biological scaling, complex dimensions, MST/WBE, DLA, or content in the project's notebooks/docs. Performs grounded retrieval over the local Weaviate corpus and returns cited answers.
tools: mcp__fractal-rag__*, Read
---

You are a research librarian for fractal mathematics literature.

# Corpus
The Weaviate index (via the fractal_rag MCP server) contains four kinds of
artifacts:
- `paper` — passages extracted from reference PDFs (WBE, Mandelbrot,
  Lapidus, etc.)
- `notebook_cell` — markdown + code cells from the repo's Jupyter notebooks
- `doc_page` — chunks from the MkDocs documentation (foundations,
  metabolic-scaling, spectral-geometry, biological-geometry, hypotheses)
- `json_entry` — entries from the historical fractal-research JSON pulled
  from the CyVerse Data Store
Plus a `Concept` collection with canonical concepts (Mandelbrot set, WBE,
DLA, Apollonian packing, Lapidus complex dimensions, Hurst exponent, ...).

# Tool selection
- Broad question → `fractal_search` (hybrid, default alpha=0.5)
- "What is X?" / definitional → `fractal_concept_search` first, then
  `fractal_search` for examples
- "Show me work related to <result Y>" → `fractal_neighbors(object_id_of_Y)`
- "Cite chapter and verse" → `fractal_citation_context(object_id)`
- "How is concept A related to concept B?" → `fractal_concept_map(A)`,
  then `fractal_concept_map(B)`, then intersect
- "How much of the corpus covers X?" → `fractal_aggregate(group_by, filter)`

# Multi-step research patterns
For comparative questions, do at least 3 retrievals:
1. Concept search for each side of the comparison
2. Hybrid search anchored on each concept's name
3. Aggregate to gauge coverage; report gaps honestly

# Citation discipline
Every claim in your answer that is sourced from the corpus must have:
- An inline citation `[1]`, `[2]`, ...
- A "Sources" section at the end listing `object_id`, `source_uri`, and a
  one-line snippet for each citation
Never invent sources. If retrieval returned nothing relevant, say so.

# Asking the user for clarification
Ask one specific clarifying question only when the user's question is
ambiguous in a way that materially changes which tool you'd reach for
(e.g., "Do you mean DLA in 2D or 3D?"). Don't ask out of caution.

# When to escalate to the main session
If the user asks something the corpus can't answer (e.g., needs live web
data, or asks you to write code), return a short answer indicating the gap
rather than guessing.
```

### 9.2 Allowed tools

- `mcp__fractal-rag__*` — the eight MCP tools defined in §8.2.
- `Read` — for the agent to follow up on a `source_uri` that points into the local repo (e.g., open a notebook to read more context).

**Not allowed:** Bash, Write, Edit, Agent, WebFetch, WebSearch. Read-only by design (matches §3 R/W decision).

### 9.3 Invocation patterns

- `Agent({ subagent_type: "fractal-explorer", prompt: "..." })` from any Claude Code session in the repo.
- `/loop "<research question>"` for self-paced iterative research dives.
- Multi-agent parallel dispatch when the main session needs to compare positions across literature (e.g., spawn one explorer per author/framework, then synthesize).

## 10. Testing and verification

### 10.1 Unit tests (`pytest`, no infrastructure)
- `tests/unit/test_chunk.py` — chunker produces stable, token-bounded chunks; respects sentence boundaries; overlap correctness.
- `tests/unit/test_parsers.py` — fixture-based: tiny notebook, tiny markdown, small JSON sample, tiny PDF. Each parser returns the expected record count and `source_type`.
- `tests/unit/test_concepts.py` — string-match concept extraction over a fixture passage finds the expected concept IDs and skips false-positive substrings.
- `tests/unit/test_schema.py` — schema bootstrap is idempotent; second run is a no-op.

### 10.2 Integration tests (`pytest -m integration`)
- `tests/integration/test_ingest_smoke.py` — spins up `weaviate-local` via testcontainers, runs schema bootstrap, ingests a 10-doc fixture, exercises each MCP tool against it, asserts payload shapes.

### 10.3 Manual verification checklist (run before declaring v1 done)

Documented in `docs/superpowers/specs/2026-05-23-fractal-rag-agent-verification.md` (created during execution). Eight prompts the user runs through Claude Code with expected qualitative behavior:

1. *"What's the predicted mass dimension for vascular plants under WBE?"* → cites `docs/metabolic-scaling/methods.md` or `2_mst_equations.ipynb`; value matches WBE prediction.
2. *"What does Lapidus mean by 'complex dimensions'?"* → cites `docs/spectral-geometry/` content.
3. *"Show me all the notebooks that touch DLA."* → uses `fractal_search` with `source_type=notebook_cell` and DLA concept filter; returns ≥3 results.
4. *"How are Apollonian packings related to forest canopy gaps?"* → uses `fractal_concept_map` for both concepts, returns a synthesis with cited bridge content.
5. *"Which authors appear most often in the corpus?"* → uses `fractal_aggregate(group_by="authors")`.
6. *"Find me unfamiliar work near Mandelbrot's 1977 self-affinity paper."* → uses concept search then `fractal_neighbors`.
7. *"What's the fractal dimension of DLA in 2D vs 3D?"* → returns distinct values per dimension with citations.
8. *"Summarize the three testable research hypotheses framework."* → cites `docs/hypotheses/` content.

### 10.4 Verification gate
Before reporting v1 complete, run the `superpowers:verification-before-completion` skill: execute the checklist and capture transcripts.

## 11. Implementation phases (high-level)

The detailed implementation plan is the next deliverable, produced by `superpowers:writing-plans` after this spec is approved. At a high level, the phases will be:

1. **Phase A — Infra refresh:** update + apply K3s manifests; verify Weaviate 1.35 and t2v-transformers come up healthy.
2. **Phase B — Schema + scaffolding:** create the `fractal_rag` Python package, schema bootstrap, config, concept seed.
3. **Phase C — Pull + parsers:** `pull` subcommand and four parsers with unit tests.
4. **Phase D — Chunker + enricher:** hierarchical chunker, concept string-match, summary heuristic.
5. **Phase E — Ingest orchestrator + first end-to-end run:** ingest the four sources into Weaviate; debug; tune.
6. **Phase F — MCP server:** eight tools, with integration tests.
7. **Phase G — Subagent + repo wiring:** `.claude/agents/fractal-explorer.md` and `.mcp.json`.
8. **Phase H — Verification:** run the eight-question checklist, capture transcripts, fix any retrieval-quality issues.

Each phase ends with a commit. Phases C, D, F, and G are good candidates for parallel sub-agent execution under the `superpowers:subagent-driven-development` skill. Phase H benefits from `/loop`.

## 12. Open issues to resolve during implementation

- **JSON shape unknown until pull:** the CyVerse JSON's exact structure (whether it's a Weaviate v3 export with vectors, a flat list of records, or something else) won't be known until `fractal-rag pull` runs. The `parsers/json_corpus.py` will need to be written *after* the first inspection. Phase C carries this risk and may need a short discovery sub-step.
- **PDF source inventory:** we have no canonical list of which reference PDFs to ingest. During Phase C, we'll either (a) curate a short list (~10–20) from `docs/references.md` and store DOIs + retrieval method, or (b) skip PDFs from v1 if curation drags. Skipping PDFs only weakens citation grounding; it doesn't break the rest.
- **Embedding model swap mechanic:** if Arctic-embed-l-v2.0 underperforms on technical mathematics passages, swapping to nomic-embed-text-v2 requires re-pulling a different sidecar image and a full re-embed. The CLI will support `--force-reembed` for this case.

## 13. Architectural decisions that enable Spec #2 and #3

These choices are deliberate so the future specs don't need re-architecture:

- **Concept side-collection:** the natural integration point for OBO/OLS ontology terms in mesa-mcp (Spec #2). Each `Concept` can carry an `iri: str?` property in v2 that links to an OLS term.
- **`source_uri` on every artifact:** when an artifact is an iRODS object, the URI is the iRODS path, which is what `mesa-ducklake` needs to record AVU history (Spec #2).
- **MCP transport stdio in Python:** matches mesa-mcp's stack exactly, so the two MCPs can be co-installed in the same Claude Code session and (eventually) share a config schema.
- **Read-only v1 surface:** when Spec #2 adds writes, the new tools (`fractal_tag`, `fractal_annotate`) will go through `mesa-mcp` so AVU writes get DuckLake history automatically. The fractal MCP stays focused on retrieval.

## 14. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GPU contention if other workloads are running | Low | High | Pin t2v-transformers to a specific GPU via `NVIDIA_VISIBLE_DEVICES=0`. 3 A100s available, only need 1. |
| Weaviate 1.35 schema API differs from 1.27 in subtle ways | Medium | Medium | Use the v4 Python client throughout (it pins API). Run schema bootstrap as the first test of the new cluster. |
| The CyVerse JSON is much larger or much different in shape than expected | Medium | Medium | Discovery sub-step in Phase C before writing the parser. If huge, stream-parse instead of load-into-memory. |
| String-match concept extraction misses too much | Medium | Low | v1 quality bar is "useful, not perfect." Spec #2 adds LLM extraction. |
| PDF parsing flakiness (marker fails on math-heavy PDFs) | High | Low | PDFs are an optional source. Fall back to pdfminer.six with a quality flag in the metadata. |

---

*End of spec. Next step: `superpowers:writing-plans` produces the detailed implementation plan from this document.*
