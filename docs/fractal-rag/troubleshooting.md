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
    kubectl apply -f k3s-deployment/weaviate-pvc.yaml
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

### Ingest is dropping a lot of objects

Watch `failed_chunks` per source in `fractal-rag status` and tail the
failures file:

```bash
tail -f ~/.cache/fractal-rag/failed_objects.jsonl
```

Common causes:

- **Embedding sidecar saturated:** GPU OOM or 429 backoff. Reduce
  concurrency by lowering `FRACTAL_RAG_BATCH_CONCURRENCY` (default 4).
- **Property too large:** a single chunk above ~64 KiB will fail with a
  Weaviate validation error. Reduce `chunk_max_tokens` or fix the upstream
  parser that's emitting a giant blob.
- **Concept reference unknown:** an artifact references a Concept UUID that
  wasn't created in pass 1. This shouldn't happen with the deterministic
  `uuid5(...)` scheme; if it does, rerun pass 1 (`fractal-rag schema
  bootstrap` + reseed).

### Ingest takes forever on the JSONL corpus

The 50K-article JSONL is ~17 GB and dominates wall clock. Options:

- Ingest a slice first: `fractal-rag ingest --source json --limit 5000`.
- Bump `FRACTAL_RAG_BATCH_SIZE` from 100 → 256 (Weaviate handles it; the
  bottleneck is the GPU embed call).
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
- Read the design spec
  (`docs/superpowers/specs/2026-05-23-fractal-rag-agent-design.md`) — the
  "Risks / mitigations" section calls out known weak spots.
- File an issue with the failing CLI command, the relevant log snippet, and
  the output of `fractal-rag status`.
