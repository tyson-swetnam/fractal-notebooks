---
type: Guide
title: "Fractal RAG: Troubleshooting"
description: >-
  Failure modes of the Fractal RAG stack by layer: Weaviate and GPU sidecar
  pods, schema bootstrap, ingest paths including FRACTAL_RAG_REPO_ROOT and
  CORPUS_ROOT, MCP wiring in Claude Code, agent quality, and the re-index recipe
  after a docs reorganisation.
resource: https://tyson-swetnam.github.io/fractal-notebooks/fractal-rag/troubleshooting/
tags: [knowledge, rag, weaviate, mcp]
generated:
  by: human:tswetnam
  at: "2026-05-24T00:00:00Z"
status: stable
---

# Troubleshooting

Common failure modes and how to root-cause them. Issues are grouped by the
layer they originate in: infrastructure → ingest → MCP → agent.

## Infrastructure

### Weaviate pod is `CrashLoopBackOff`

```bash
kubectl -n ai-workloads logs deploy/weaviate --tail=80
```

Look for:

- `failed to load schema`: PVC state is incompatible with a new image
  version. If you just upgraded from 1.27 to 1.35 and don't care about old
  data, delete the PVC and reapply:

    ```bash
    kubectl -n ai-workloads delete pvc weaviate-pvc
    kubectl apply -f k3s-deployment/base/weaviate-pvc.yaml
    kubectl -n ai-workloads rollout restart deploy/weaviate
    ```

- `module text2vec-transformers not enabled`: the env var didn't land. Double
  check the deployment manifest has both
  `ENABLE_MODULES=text2vec-transformers` and `DEFAULT_VECTORIZER_MODULE`.

### `t2v-transformers` pod is `Pending` forever

```bash
kubectl -n ai-workloads describe pod -l app=t2v-transformers | tail -40
```

If you see `0/1 nodes are available: 1 Insufficient nvidia.com/gpu`:

- Confirm the GPU plugin is running: `kubectl -n kube-system get pods | grep nvidia-device-plugin`
- Confirm GPUs are visible: `kubectl describe node | grep nvidia.com/gpu` should show capacity ≥1.
- Check that the manifest's `resources.requests.nvidia.com/gpu` isn't asking for more GPUs than exist.

### `t2v-transformers` runs but inference is slow

`kubectl -n ai-workloads exec deploy/t2v-transformers -- nvidia-smi` — if no
GPU is listed, the container fell back to CPU. Usual cause: the NVIDIA
runtime isn't the default. Either set
`spec.runtimeClassName: nvidia` in the deployment or fix the K3s NVIDIA
runtime config (see `nvidia-device-plugin-daemonset.yaml`).

### Weaviate is up but `curl localhost:30080/v1/.well-known/ready` fails

If you used the docker-compose stack instead of K3s, the port is `8080`, not
`30080`. Either fix the URL or set the env override:

```bash
export FRACTAL_RAG_WEAVIATE_HTTP_PORT=8080
export FRACTAL_RAG_WEAVIATE_GRPC_PORT=50051
```

## Schema

### `schema bootstrap` returns `Unsupported vectorizer module`

`config.py` defaults to `text2vec-transformers`. If your Weaviate doesn't
have that module enabled, the bootstrap fails fast. Re-check the
`ENABLE_MODULES` env var on the Weaviate pod / container.

### Second `schema bootstrap` is **not** idempotent

That means the prior run partially failed and left only one of the two
collections. Inspect:

```bash
fractal-rag status        # one of the collections will show null
```

Either delete the orphan and rerun, or use the destructive flag:

```bash
fractal-rag schema bootstrap --drop
```

## Ingest

### `fractal-rag pull` fails with `gocmd: not found`

`gocmd` isn't on PATH for the user running the CLI. Install per
[GoCommands docs](https://github.com/cyverse/gocommands) and make sure
`~/.irods/` is initialized (`gocmd ls /iplant/home/<you>`).

### `pull` succeeds but `ingest --source json` reports `parsed_docs: 0`

The corpus path doesn't match what `ingest.discover_jsonl` is looking for —
specifically, any `*.jsonl` whose path contains `embeddings/`. Either move
your file under `embeddings/` or override the default `corpus_root` to point
at the JSONL's parent:

```bash
export FRACTAL_RAG_CORPUS_ROOT=/where/you/actually/put/it
```

### `ingest --source docs` (or `notebooks`) reports `parsed_docs: 0`

The markdown source walks `<repo_root>/docs/**/*.md`, and `repo_root`
defaults to the K3s host path `/opt/tswetnam/github/fractal-notebooks`
(`config.py`). On a laptop, a CI runner or any other checkout location that
directory does not exist, and `rglob` on a missing path is **not** an error —
it silently yields zero documents. Point the setting at your checkout:

```bash
export FRACTAL_RAG_REPO_ROOT=/path/to/your/fractal-notebooks   # or $PWD from the repo root
fractal-rag ingest --source docs
```

The `notebooks` source scans `<repo_root>/docs/**/*.ipynb` as well (skipping the
generated per-site 3DEP notebooks), so the same `FRACTAL_RAG_REPO_ROOT` covers it;
`FRACTAL_RAG_CORPUS_ROOT` (the iRODS mirror) only adds the mirrored copies and may
be absent. Do not point `CORPUS_ROOT` at the checkout: that tree is scanned without
the site's exclusion rules. To make the setting stick, put it in a gitignored `.env`
at the repo root together with any port overrides; `Settings` reads `.env` from the
directory you run `fractal-rag` in, so run the CLI from the repo root.

### Re-index after a reorganisation

Object UUIDs are derived from file paths and `ingest` upserts without ever
pruning, so moving, renaming or deleting pages (as the docs reorganisation
into Foundations, Research, Notebooks, Apps and Knowledge tabs did) leaves
stale objects under the old paths. Rebuild from scratch:

```bash
export FRACTAL_RAG_REPO_ROOT=$PWD        # the checkout whose docs/ you want indexed
fractal-rag schema bootstrap --drop      # destructive: drops and recreates both collections
fractal-rag ingest --source docs
fractal-rag ingest --source notebooks
fractal-rag status
```

Expect the `Concept` count to be unchanged and the `FractalArtifact` count to
drop to the current page set. Searching for text that only existed on a
deleted page should then return no hits.

### Ingest is dropping a lot of objects

Watch `failed_chunks` per source in `fractal-rag status` and tail the
failures file:

```bash
tail -f ~/.cache/fractal-rag/failed_objects.jsonl
```

Common causes:

- **Embedding sidecar saturated:** GPU OOM or 429 backoff in the sidecar log.
  The ingest sends one chunk at a time, so this points at an undersized pod
  memory limit rather than at load (`FRACTAL_RAG_BATCH_CONCURRENCY` is read
  but not used by the current loop).
- **Property too large:** a single chunk above ~64 KiB will fail with a
  Weaviate validation error. Reduce `chunk_max_tokens` or fix the upstream
  parser that's emitting a giant blob.
- **Concept reference unknown:** an artifact references a Concept UUID that
  wasn't created in pass 1. This shouldn't happen with the deterministic
  `uuid5(...)` scheme; if it does, rerun pass 1 (`fractal-rag schema
  bootstrap` + reseed).

### `status` shows fewer json objects than `inserted_chunks`

Object UUIDs derive from `source_uri` plus the chunk index, so two records with
the same `source_uri` overwrite each other while the loop counts both as
inserted. The json parser keys records on the Constellate `id` (a Portico
`ark://` identifier or a JSTOR stable URL), which is unique across the export;
before 2026-10-25 it keyed them on the DOI, and DOIs are shared by book
chapters, reprints and corrigenda: 1,125 of the 50,000
records repeated an earlier DOI (48,875 distinct), so that run reported 100,012
inserted chunks and `status` showed 97,762 json objects. An index built with the
old parser is fixed by deleting its json objects and re-ingesting the source,
because every json UUID changes:

```bash
python -c "
from fractal_rag.client import client_session
from weaviate.classes.query import Filter
with client_session() as c:
    art = c.collections.get('FractalArtifact')
    while art.data.delete_many(where=Filter.by_property('source_type').equal('json_corpus')).matches:
        pass   # the server deletes at most 10,000 objects per call
"
fractal-rag ingest --source json
```

On the DGX Spark the re-ingest took two hours and left exactly 100,012 json
objects for 100,012 inserted chunks: an anchor chunk and one content chunk for
each of the 50,000 records (12 long records get a second content chunk).

### Ingest takes forever on the JSONL corpus

The 50K-article JSONL is ~17 GB and dominates wall clock. Options:

- Ingest a slice first: `fractal-rag ingest --source json --limit 5000`.
- Run two sidecar replicas: `kubectl -n ai-workloads scale deploy/t2v-transformers
  --replicas=2` took a DGX Spark from 8 to 14 chunks per second (the full
  corpus then takes about two hours). `FRACTAL_RAG_BATCH_SIZE` is not
  consulted by the current one-chunk-at-a-time loop, so raising it changes
  nothing.
- Run the ingest in `screen`/`tmux`; it's resumable because the deterministic
  UUID scheme upserts rather than appends.

## MCP / Claude Code

### `/mcp` doesn't list `fractal-rag`

- You're not in the repo root, or the repo's `.mcp.json` isn't being picked
  up. Run `cat .mcp.json` to confirm.
- Or `fractal-rag` isn't on PATH for the Claude Code process. In a fresh
  terminal: `which fractal-rag`. If empty, re-run `pip install -e .` and
  reopen Claude Code so it picks up your shell's PATH.

### MCP server starts but returns `weaviate_error: connection refused`

- Weaviate isn't running on the host/port the server expects. Check
  `FRACTAL_RAG_WEAVIATE_HTTP_PORT` — defaults to `30080` (K3s NodePort).
  Local docker-compose users need `8080`.
- The gRPC port is configured separately (`FRACTAL_RAG_WEAVIATE_GRPC_PORT`).
  Weaviate v4 SDK uses both REST and gRPC.

### MCP tool returns `not_found` for a concept you "know" is there

Concept names are **case-sensitive** in `artifacts_by_concept` and
`get_concept`. Use `list_concepts()` or `search_concepts(query)` first to
find the canonical name. The agent already does this — if you're hitting
this manually from the CLI, the same rule applies.

### SSH-tunneled MCP server (remote VM) drops connection

- Use keys-only auth; a password prompt corrupts the stdio stream.
- Add `-o ServerAliveInterval=30` to the SSH args in `.mcp.json` to keep
  long retrievals alive.
- Pre-warm the venv: SSH connection setup + Python import can take ~3 s on
  cold start, which Claude Code may flag as a startup timeout. Bumping the
  MCP server start timeout (in Claude Code settings) helps.

## Agent quality

### Agent says "I couldn't find anything" but the topic obviously exists

1. Check the index actually has content for that source type:

    ```bash
    fractal-rag status
    ```

2. Run the same query directly against the index:

    ```bash
    fractal-rag query "<the question>" --limit 10
    ```

3. If the CLI returns hits but the agent doesn't, the agent's tool selection
   is wrong. Re-prompt with an explicit nudge: "Use `search_artifacts` with
   `target_vector='content_vec'` and `alpha=0.3` for that question." If that
   fixes it, codify the rubric in `.claude/agents/fractal-explorer.md`.

### Agent invents citations

The agent shouldn't do this — the citation discipline section of the
subagent file forbids it. If it slips, two fixes:

- Tighten the prompt: add an explicit "If a tool returned no objects, say
  so plainly and STOP — do not synthesize." line.
- Verify the returned `source_uri` actually resolves (`Read` it from disk).
  The agent has the `Read` tool for exactly this.

### Re-embedding after a model swap takes too long

After swapping the embedding model image, you need to re-vectorize every
object. The reusable trick is to scope the schema drop to artifacts only,
keep concepts (they're tiny), and rerun ingest:

```bash
python -c "
from fractal_rag.client import client_session
with client_session() as c: c.collections.delete('FractalArtifact')"
fractal-rag schema bootstrap
fractal-rag ingest --source all
```

## Still stuck?

- Check `kubectl -n ai-workloads get events --sort-by=.lastTimestamp | tail`
  for cluster-level signals.
- Read the [design spec](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/specs/2026-05-23-fractal-rag-agent-design.md) — the
  "Risks / mitigations" section calls out known weak spots.
- File an issue with the failing CLI command, the relevant log snippet, and
  the output of `fractal-rag status`.
