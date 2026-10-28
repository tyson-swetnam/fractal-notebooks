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

### Weaviate pod stays `0/1 Running` and exits every ten minutes

`kubectl -n ai-workloads logs deploy/weaviate --previous` ends with `could not
join raft join list: context deadline exceeded. Weaviate detected this node to
have state stored` after `RAFT_BOOTSTRAP_TIMEOUT` (600 s), and the readiness
probe returns 503 the whole time. Weaviate names its Raft node after the pod
unless `CLUSTER_HOSTNAME` is set, so a re-created pod (image change, node
reboot, `rollout restart`) cannot rejoin the single-voter cluster its
predecessor left on the volume. The hint in the message about raising the
timeout does not apply: the database is not loading, the node identity changed.

The base manifest pins `CLUSTER_HOSTNAME=node1` and sets
`RAFT_ENABLE_ONE_NODE_RECOVERY=true`, which lets a node whose name changed
rewrite the stored configuration to itself. Apply it and watch for the recovery
line:

```bash
kubectl apply -f k3s-deployment/base/weaviate-deployment.yaml
kubectl -n ai-workloads logs deploy/weaviate | grep -m1 'perform cluster recovery'
# ... "old_single_cluster_node_name":"weaviate-<old pod>","new_single_cluster_node_name":"node1" ...
```

On 2026-10-25 the pod was ready eleven seconds after the apply; the data on the
volume is untouched by the recovery. The name must then never change again:
Weaviate records the node that owns each shard in the schema metadata, and the
recovery renames only the Raft member. Renaming an existing cluster to `node1`
worked only until the next cold restart (next entry).

### Every query fails with `no read replica found`

`fractal-rag status` and the MCP tools fail with `aggregate: no read replica
found` (or `search index fractalartifact ... no read replica found`) while
`/v1/.well-known/ready` returns 200 and `/v1/nodes` shows the node `HEALTHY`
with zero shards. The shards endpoint names the problem:

```bash
curl -s localhost:30080/v1/schema/FractalArtifact/shards
# {"error":[{"message":"shard cWfwu30XY1Jf: resolve node name \"weaviate-58885945f5-c9b5w\" to host"}]}
```

The shard metadata still belongs to the node name the data was written under,
and the running node has a different `CLUSTER_HOSTNAME`. The data on the volume
is intact. Set the name back to the recorded one and let the one-node recovery
rename the Raft member (about fifteen seconds):

```bash
kubectl -n ai-workloads set env deploy/weaviate CLUSTER_HOSTNAME=<name from the shards error>
kubectl -n ai-workloads rollout status deploy/weaviate
curl -s localhost:30080/v1/schema/FractalArtifact/shards      # [{"name":"...","status":"READY",...}]
fractal-rag status
```

Then put the same value in your overlay so `kubectl apply -k` keeps it: the
`dgx-spark` overlay patches `weaviate-58885945f5-c9b5w` for the reference
cluster (2026-10-28). Pick a fixed name before the first ingest and never
change it; Weaviate has no supported rename.

### Keyword (BM25) scores are 0 and hybrid ranking looks arbitrary

Exact-title pages fall out of the top ten, every `search_artifacts` hit carries
the same score, and a direct probe returns matches whose score is exactly 0 on
the word-tokenized properties while the explanation still shows a term
frequency:

```bash
python -c "
from fractal_rag.client import client_session
from weaviate.classes.query import MetadataQuery
with client_session() as c:
    res = c.collections.get('FractalArtifact').query.bm25(
        query='lacunarity', query_properties=['content'], limit=3,
        return_metadata=MetadataQuery(score=True, explain_score=True))
    for o in res.objects: print(o.metadata.score, o.metadata.explain_score)
"
```

Weaviate before 1.35.3 writes a NaN average property length for a segment flush
that contains only deletions (weaviate/weaviate#10102); compaction spreads it
through the collection, and on arm64 the NaN becomes an average of 0, so the
BM25 term weight is 0 for every match in `title`, `summary`, `content` and
`authors` (`tags`, `source_type` and the other FIELD-tokenized properties keep
scoring). A `delete_many` of 97,762 objects on 2026-10-25 triggered it: the
keyword leg of every hybrid query became a flat bonus and the `Hurst Exponent`
concept page ranked 26th for its own title. The base manifest pins 1.35.23:
applying it restarted Weaviate on the patched release, whose loader recomputes
the averages from the stored per-document lengths, and the scores were back
without a rebuild (the concept page ranks first). On a version that cannot be
upgraded, `schema bootstrap --drop` plus a full re-ingest also clears the NaN
segments.

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

Watch `failed_chunks` per source in the JSON report that `fractal-rag ingest`
prints (the last run is also saved to `~/.cache/fractal-rag/state.json`;
`fractal-rag status` only prints collection counts) and tail the failures file:

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
old parser must be rebuilt, because every json UUID changes:

```bash
fractal-rag schema bootstrap --drop      # destructive: drops and recreates both collections
fractal-rag ingest --source all
```

Deleting only the json objects (`delete_many` filtered on `source_type ==
json_corpus`, repeated until `matches` is 0 because the server deletes at most
10,000 objects per call) and re-running `ingest --source json` saves the ten
minutes the docs and notebooks take, but only on Weaviate 1.35.3 or newer: on
1.35.0 the bulk delete zeroed every keyword score (see [Keyword scores are
0](#keyword-bm25-scores-are-0-and-hybrid-ranking-looks-arbitrary)). On the DGX
Spark the json re-ingest took two hours and left exactly 100,012 json objects
for 100,012 inserted chunks: an anchor chunk and one content chunk for each of
the 50,000 records (12 long records get a second content chunk).

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
- Or you declined the one-time approval for the project server: `claude mcp
  list` shows `⏸ Pending approval` or `Rejected`; run `claude mcp
  reset-project-choices` and reopen Claude Code.

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

### Claude Code on a local model fails with `Cannot connect to host`

Every turn ends in `API Error: 500 litellm.InternalServerError: ...
Hosted_vllmException - Cannot connect to host 127.0.0.1:<port>` while
`ANTHROPIC_BASE_URL` points at the LiteLLM gateway.

- The gateway accepted the model name and tried to reach the vLLM backend
  registered for it, and that backend is not listening. The address in the
  message is on the inference host, not on the RAG host, so nothing on the K3s
  side is wrong. Start (or wait for) the backend on the inference host; vLLM
  engines take minutes to load.
- Probe before opening Claude Code. The registered names:
  `curl -s -H "Authorization: Bearer $GATEWAY_KEY" http://127.0.0.1:8000/v1/models | jq -r '.data[].id'`.
  Whether a backend answers, on the path Claude Code uses:

    ```bash
    curl -sS -w '\n%{http_code}\n' -X POST http://127.0.0.1:8000/v1/messages \
      -H "Authorization: Bearer $GATEWAY_KEY" -H 'anthropic-version: 2023-06-01' \
      -H 'content-type: application/json' \
      -d '{"model":"<name>","max_tokens":1,"messages":[{"role":"user","content":"."}]}'
    ```

  A body starting `{"id":"msg_` means the backend answered; `500 ... Cannot
  connect to host` means registered but down; `400 Invalid model name passed in
  model=...` means the name is not registered with the gateway, so pick one
  from the list.
- A `401 Authentication Error, No api key passed in` means no credential
  reached the gateway: export `ANTHROPIC_AUTH_TOKEN` in the shell that starts
  Claude Code. LiteLLM reads it from `Authorization: Bearer`; it also reads
  `x-api-key` (which `ANTHROPIC_API_KEY` would set) and prefers `Authorization`
  when both arrive. A wrong key on a LiteLLM gateway that runs without a
  database comes back as `400 No connected db.`, because LiteLLM can only
  validate its master key locally: check the key file, not a database.
- Other `400`s naming `context_management`, `Extra inputs are not permitted`,
  `defer_loading` or `thinking` come from fields Claude Code sends that the
  gateway-to-vLLM translation does not accept: start Claude Code with
  `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1`, and see the [official gateway
  troubleshooting table](https://code.claude.com/docs/en/llm-gateway-connect#troubleshoot-gateway-errors)
  for the rest.

### Local model never calls the fractal-rag tools

The answer comes from the model's memory, or the tool call appears as text in
the reply.

- Claude Code defers MCP tools behind its `ToolSearch` tool by default, since
  v2.1.304 also through a gateway: the first request offers no
  `mcp__fractal-rag__*` tool at all, and a small model that never calls
  `ToolSearch` never sees them. Start Claude Code with
  `ENABLE_TOOL_SEARCH=false` so the eight schemas are sent directly.
- The vLLM server must be started with `--enable-auto-tool-choice` and a
  `--tool-call-parser` for its model family (for example `hermes` for Qwen3,
  `qwen3_coder` for the Qwen3.6 and Qwen3.8 models). Without them vLLM returns
  tool calls as plain text, and through the gateway Claude Code sees no tool use.
- Small models handle a short tool catalogue better than Claude Code's full
  one. For scripted runs pass `--tools "" --mcp-config .mcp.json
  --strict-mcp-config` with `ENABLE_TOOL_SEARCH=false`, so the request carries
  only the eight RAG tools: `--strict-mcp-config` by itself only keeps other MCP
  servers out, the built-in tools stay in the catalogue, and `--allowedTools`
  only pre-approves calls and removes nothing. Name the tool in the prompt
  ("use search_artifacts for ...").
- Check retrieval separately with `fractal-rag query "<question>"`: if the CLI
  returns good hits, the problem is the model or its tool-calling setup, not
  the index.

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
