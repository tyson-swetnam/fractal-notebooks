---
type: Guide
title: "Fractal RAG: Hosted VM (K3s + GPU)"
description: >-
  Deploy the Fractal RAG stack on any NVIDIA GPU host with K3s (reference: a
  DGX Spark; Jetstream2 as an option), ingest the corpus, then use the index
  from the shell, Claude Code, local vLLM models behind a LiteLLM gateway, or
  Python.
resource: https://tyson-swetnam.github.io/fractal-notebooks/fractal-rag/hosted-vm/
tags: [knowledge, rag, weaviate, cuda, mcp]
sources:
  - id: jetstream2-flavors
    resource: https://docs.jetstream-cloud.org/general/vmsizes/
    title: Jetstream2 documentation, Instance Flavors
  - id: jetstream2-gpu-faq
    resource: https://docs.jetstream-cloud.org/faq/gpu/
    title: Jetstream2 documentation, GPU FAQ
  - id: access-jetstream2-gpu
    resource: https://support.access-ci.org/documentation/resources/jetstream2-gpu
    title: ACCESS, Jetstream2 GPU resource
  - id: claude-code-gateway
    resource: https://code.claude.com/docs/en/llm-gateway-connect
    title: Claude Code documentation, Connect Claude Code to an LLM gateway
  - id: claude-code-subagents
    resource: https://code.claude.com/docs/en/sub-agents
    title: Claude Code documentation, Subagents
  - id: vllm-tool-calling
    resource: https://docs.vllm.ai/en/latest/features/tool_calling/
    title: vLLM documentation, Tool Calling
  - id: litellm-anthropic-messages
    resource: https://docs.litellm.ai/docs/anthropic_unified
    title: LiteLLM documentation, /v1/messages
generated:
  by: human:tswetnam
  at: "2026-05-24T00:00:00Z"
status: stable
---

# Hosted VM (K3s + GPU)

This page covers the full deployment: one host with an NVIDIA GPU running K3s,
Weaviate 1.35 and an arctic-embed text2vec-transformers sidecar pinned to the
GPU (arctic-embed-l v2.0 in the locally built DGX Spark image; the published
`snowflake-snowflake-arctic-embed-l-latest` image in the base, which serves the
original arctic-embed-l model), holding the whole corpus: about 104,000 chunks
from the 50,000 Constellate articles, the notebooks and the site pages. It is
the topology the kustomize manifests under `k3s-deployment/` target. The first
half brings the stack up and ingests the corpus; the second half, from
[Use the index](#7-use-the-index) on, is the user guide: querying from the
shell, from Claude Code, from local vLLM models behind a gateway, and from
Python.

Nothing here depends on one particular machine. The reference deployment is an
NVIDIA DGX Spark (`sparky-1`) whose language models are served by vLLM on a
second DGX Spark (`sparky-2`); before 2026-10-25 the stack ran on an x86 server
with A100 GPUs, and a Jetstream2 GPU instance works as well. Host-specific
notes are collected at the [end of the page](#dgx-spark-arm64-notes).

## Where it runs

| Platform | Status | Manifests |
|---|---|---|
| NVIDIA DGX Spark (GB10, arm64, 128 GB unified memory) | reference deployment since 2026-10-25 | `k3s-deployment/overlays/dgx-spark`, with a locally built arctic-embed-l v2.0 sidecar image ([notes](#dgx-spark-arm64-notes)) |
| x86 server with NVIDIA GPUs (the original host: AMD EPYC, 3× A100 80 GB) | no longer used | `k3s-deployment/base` as is (published arctic-embed-l image); the measurements in the 2026-05 specs come from it |
| Jetstream2 GPU instance (NSF ACCESS) | option, not run by us | `k3s-deployment/base` as is on an x86 `g3` flavor ([notes](#jetstream2-notes)) |

The GPU work is small. The embedding sidecar holds about 3 GB of GPU memory per
replica, and the ingest loop rather than the GPU bounds throughput, so any
current NVIDIA GPU with 8 GB free is enough for the index. Weaviate runs on the
CPU: budget 8 vCPU, 32 GB RAM and 100 GB of disk (the iRODS mirror is 31 GB,
the Weaviate volume 50 GB). Language-model inference is a separate workload
with its own GPU budget; it can share the host or, as in the reference
deployment, run on another machine (see [local models through a
gateway](#use-local-vllm-models-through-a-gateway)).

## Prerequisites

| Need | Notes |
|---|---|
| Python 3.10+, git, `jq` | `python3-venv` on Ubuntu; `jq` only for the smoke tests below |
| NVIDIA driver + container toolkit | `nvidia-smi` must work and the NVIDIA Container Toolkit must be installed; K3s detects `nvidia-container-runtime` at start-up and creates the `nvidia` RuntimeClass the GPU pods request |
| K3s v1.36 | the install command below, run after `/etc/rancher/k3s/config.yaml` is in place (no Traefik, kubeconfig mode and group, loopback-only NodePorts); embedded containerd, not `--docker`. Details in `k3s-deployment/README.md` |
| `kubectl` | installed by K3s into `/usr/local/bin`; `export KUBECONFIG=/etc/rancher/k3s/k3s.yaml` |
| `gocmd` v0.11.5+ | for the iRODS pull; `~/.irods/` must already be authenticated, and the collection shared with you (step 5) |
| `helm` (optional) | not required by these manifests |

### Keep Weaviate off the network

Weaviate runs with anonymous access, and a Kubernetes NodePort answers on every
address of the host, not only on loopback (on the reference host
`curl http://<any host address>:30080/v1/.well-known/ready` returns 200), so
anyone who can reach ports 30080 or 30051 can read, write and delete the index.
Every client on this page talks to `localhost`, so restrict the NodePorts to
loopback in the K3s configuration before the install:

```yaml
# /etc/rancher/k3s/config.yaml (the full example is in k3s-deployment/README.md)
disable:
  - traefik
write-kubeconfig-mode: "0640"
write-kubeconfig-group: "docker"
kube-proxy-arg:
  - nodeport-addresses=127.0.0.0/8   # NodePorts answer on loopback only
```

An existing cluster takes the same lines followed by `sudo systemctl restart k3s`
(running pods are kept). On a cloud instance also admit only SSH in the security
group, and if `ufw` is enforcing allow the two cluster CIDRs as the README shows.
Then install K3s:

```bash
curl -sfL https://get.k3s.io | sudo env INSTALL_K3S_VERSION=v1.36.5+k3s1 sh -s - server
```

Quick host checks:

```bash
nvidia-smi                                 # GPUs visible to the OS
sudo systemctl status k3s                  # active (running)
kubectl get nodes -o wide                  # node Ready, GPU label present
```

## 1. Apply the stack

The manifests are a kustomize base, `k3s-deployment/base/` (namespace, NVIDIA
device plugin with its time-slicing config, Weaviate, the embedding sidecar), plus
host overlays under `k3s-deployment/overlays/`. On an x86 GPU node the base is all
you need; K3s itself provides the `nvidia` RuntimeClass and the `local-path`
StorageClass the PVC requests. The Service publishes the NodePorts the moment it
is applied, so [Keep Weaviate off the network](#keep-weaviate-off-the-network)
comes first.

```bash
kubectl label node <node> nvidia.com/gpu.present=true   # the device plugin's nodeSelector
kubectl apply -k k3s-deployment/base                     # or: -k k3s-deployment/overlays/dgx-spark
kubectl -n kube-system rollout status daemonset/nvidia-device-plugin-daemonset
```

Verify GPUs are now schedulable:

```bash
kubectl get node -o jsonpath='{.items[0].status.allocatable.nvidia\.com/gpu}{"\n"}'
# 2 on a single-GPU host: the base ConfigMap time-slices every GPU in two
```

## 2. Wait for Weaviate + the embedding sidecar

```bash
# First start pulls ~6 GB of images and the sidecar loads the model before it
# reports Ready; budget 5-10 minutes.
kubectl -n ai-workloads rollout status deployment/t2v-transformers --timeout=15m
kubectl -n ai-workloads rollout status deployment/weaviate --timeout=15m
kubectl -n ai-workloads get pods -o wide
```

Smoke-test from the host:

```bash
curl -s localhost:30080/v1/.well-known/ready                                # 200 OK
curl -s localhost:30080/v1/meta | jq '.modules | has("text2vec-transformers")'   # true
```

And from inside the cluster, confirm the sidecar is also healthy:

```bash
kubectl -n ai-workloads exec deploy/weaviate -- \
  wget -qO- http://t2v-transformers:8080/.well-known/ready
# prints nothing and exits 0: the sidecar answers 204 No Content (add -S to see the status line)
```

## 3. Install the `fractal-rag` package on the host

```bash
git clone https://github.com/tyson-swetnam/fractal-notebooks.git && cd fractal-notebooks   # "<checkout>" below means this directory
python3 -m venv .venv && .venv/bin/pip install -e "./fractal_rag[dev,parsers]"
.venv/bin/fractal-rag concepts validate            # OK: 32 concepts validated
```

The defaults in `config.py` target the NodePorts `30080`/`30051` exposed by
`weaviate-service.yaml`, so no connection settings are needed on the host. The
path defaults (`repo_root`, `corpus_root`) still point at the original host's
`/opt/tswetnam/...` layout: on any other machine put the paths in a gitignored
`.env` at the repo root, which is read whenever you run `fractal-rag` from
there. When `repo_root` does not exist the `docs` source indexes nothing and
the `notebooks` source indexes only the corpus mirror, both without an error.

```bash
cat > .env <<EOF
FRACTAL_RAG_REPO_ROOT=$PWD
FRACTAL_RAG_CORPUS_ROOT=$HOME/fractal-rag-corpus
FRACTAL_RAG_IRODS_ROOT=/iplant/home/tswetnam/projects/fractal-notebooks/
EOF
```

## 4. Bootstrap the schema

```bash
.venv/bin/fractal-rag schema bootstrap
# { "created": ["Concept", "FractalArtifact"], "already_present": [], "properties_added": {} }
```

## 5. Pull the corpus from iRODS

```bash
.venv/bin/fractal-rag pull
# Mirrors FRACTAL_RAG_IRODS_ROOT (/iplant/home/tswetnam/projects/fractal-notebooks/)
# into FRACTAL_RAG_CORPUS_ROOT. ~31 GB; resumable, gocmd skips files whose checksums match.
```

The collection is a CyVerse user collection: ask the maintainer for read access
before `pull`, or skip the pull and point `FRACTAL_RAG_CORPUS_ROOT` at your own
copy of the export (JSONL under an `embeddings/` directory, see
[Troubleshooting](troubleshooting.md#pull-succeeds-but-ingest-source-json-reports-parsed_docs-0)).

## 6. Run the full ingest

```bash
.venv/bin/fractal-rag ingest --source all 2>&1 | tee ~/fractal-rag-ingest.log
```

Measured on the DGX Spark (2026-10-25): the docs finish in about a minute, the
notebooks in about five, and the 50,000 JSONL records take about two hours at
14 chunks per second with two sidecar replicas (every chunk is three vectors).
The ingest inserts one chunk at a time, so the GPU is not the bottleneck; the
second replica, which uses the second GPU time slice, is the only cheap lever
(the sidecar's 24 Gi memory limit is per pod, so the second replica needs no
manifest change):

```bash
kubectl -n ai-workloads scale deploy/t2v-transformers --replicas=2
```

The manifests declare one replica, so any later `kubectl apply -k` scales the
sidecar back to one; repeat the command before the next long ingest.

Watch progress with:

```bash
kubectl -n ai-workloads logs -f deploy/t2v-transformers
.venv/bin/fractal-rag status             # repeat to see counts climbing
```

When it finishes, sanity-check that all four source types landed. The json
object count should equal the `inserted_chunks` of the json report; if it is
smaller, the index was built by the pre-2026-10-25 parser that keyed records on
the DOI (see [Troubleshooting](troubleshooting.md#status-shows-fewer-json-objects-than-inserted_chunks)).

```bash
.venv/bin/fractal-rag status
# { "FractalArtifact": 104061, "Concept": 32 }   # 2026-10-25: 512 docs + 3,537 notebook + 100,012 json chunks

# Inspect by source_type:
.venv/bin/python -c "
from fractal_rag.client import client_session
from fractal_rag.config import get_settings
from weaviate.classes.query import Filter

s = get_settings()
with client_session(s) as c:
    art = c.collections.get(s.artifact_collection)
    for st in ('json_corpus', 'notebook', 'markdown', 'pdf'):
        n = art.aggregate.over_all(
            total_count=True,
            filters=Filter.by_property('source_type').equal(st),
        ).total_count
        print(f'{st}: {n}')
"
```

## 7. Use the index

Everything below runs on the K3s host unless stated otherwise, from the repo
root (so the `.env` applies) and with the `.venv` from step 3 on `PATH`:

```bash
cd <checkout> && export PATH=$PWD/.venv/bin:$PATH
fractal-rag status      # e.g. { "FractalArtifact": 104065, "Concept": 32 } on 2026-10-26; grows with each docs re-ingest
```

### From the shell

`fractal-rag query` runs a hybrid (vector plus keyword) search against
`content_vec` and prints the matching chunks as JSON (uuid, title, source
type, `source_uri`, summary). It is also the quickest way to separate
retrieval problems from agent problems
([Using the agent](using-the-agent.md#iterating-on-agent-quality)):

```bash
fractal-rag query "Hurst exponent of river discharge" --limit 5
```

Filtered searches (`source_types`, `year_min`/`year_max`, another
`target_vector`, the hybrid `alpha`) and the `resource` field (the public page,
DOI or JSTOR link to cite) are a Python session away: the [worked
notebooks](notebooks/01_quickstart.md) connect over the same NodePorts and show
the patterns.

### From Claude Code with Anthropic models

The `.mcp.json` at the repo root declares `fractal-rag serve` (stdio) as a
project MCP server, and the `fractal-explorer` subagent is scoped to its eight
tools plus read-only `Read`. The first interactive Claude Code session in the
checkout asks once whether to run the server (answer yes; `claude mcp list`
shows `⏸ Pending approval` until then, and `claude mcp reset-project-choices`
asks again); `-p` runs load it without asking.

**On the host.** Make sure `fractal-rag` is on `PATH` (otherwise the server
fails with `ENOENT`, see
[Troubleshooting](troubleshooting.md#mcp-doesnt-list-fractal-rag)), open
Claude Code in the repo root, run `/mcp` to confirm `fractal-rag` is connected,
then ask questions as described in [Using the fractal-explorer
agent](using-the-agent.md).

**From a workstation.** Register the remote server at user scope, wrapped in
SSH so its stdio shows up locally; this leaves the repository's `.mcp.json`
untouched:

```bash
claude mcp add --scope user fractal-rag -- ssh -T -o ServerAliveInterval=30 \
  user@your-gpu-host.example.org "cd <checkout on the GPU host> && .venv/bin/fractal-rag serve"
```

The MCP protocol runs over stdin/stdout, so SSH, which forwards exactly those,
needs no extra setup. Keys-only auth is required; a password prompt breaks the
connection.

### Use local vLLM models through a gateway

The index does not care which language model reads it. Claude Code talks to the
`fractal-rag` MCP server over stdio and to its model over HTTP, and the model
endpoint is configurable; Claude Code speaks the Anthropic Messages API
(`/v1/messages`), so the endpoint must serve that format. In the reference
deployment the models are [vLLM](https://docs.vllm.ai/) servers on the second
DGX Spark (`sparky-2`), fronted by a [LiteLLM](https://docs.litellm.ai/)
gateway that exposes one OpenAI-compatible endpoint over all of them and
translates [`/v1/messages`](https://docs.litellm.ai/docs/anthropic_unified)
requests for any backend. The gateway binds loopback on its own host; the RAG
host pulls it onto its own loopback with an SSH tunnel kept alive by a user
systemd unit (`ssh -N -L 127.0.0.1:8000:127.0.0.1:8000 <user>@sparky-2`), so on
the RAG host `http://127.0.0.1:8000` *is* the gateway. That address appears in
every command below: substitute your gateway's URL.

With a bare vLLM server and no gateway, either put LiteLLM in front
(`pip install "litellm[proxy]"`, a one-entry `model_list` with
`model: hosted_vllm/<served-model-name>` and
`api_base: http://<vllm-host>:<port>/v1`, then `litellm --config <file> --port 8000`)
or use the [Python loop below](#from-python-or-any-openai-compatible-agent),
which talks to the OpenAI endpoint directly. Current vLLM also serves
`/v1/messages` itself, but it validates requests more strictly than LiteLLM
does, and in the reference deployment Claude Code only ran reliably through
the gateway. Either way the vLLM server must run with
`--enable-auto-tool-choice` and a `--tool-call-parser` for its model family
([vLLM tool calling](https://docs.vllm.ai/en/latest/features/tool_calling/)):
tool calling is what lets a model use the MCP tools.

Check the gateway and list the models it serves. The key is the gateway's own;
keep it in a file outside the repository, for example
`~/.config/fractal-rag/gateway.key` with mode 600, and never in a committed
settings file:

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/v1/models   # 401: reached the gateway, no key yet
export GATEWAY_KEY=$(cat ~/.config/fractal-rag/gateway.key)                 # the file you chose above
curl -s -H "Authorization: Bearer $GATEWAY_KEY" http://127.0.0.1:8000/v1/models | jq -r '.data[].id'
```

Then start Claude Code with the gateway as its API endpoint (the variables are
those of Claude Code's [LLM gateway
guide](https://code.claude.com/docs/en/llm-gateway-connect)) and one of those
model names, from the repo root so `.mcp.json` loads the `fractal-rag` server:

```bash
cd <checkout> && export PATH=$PWD/.venv/bin:$PATH
export ANTHROPIC_BASE_URL=http://127.0.0.1:8000       # your gateway URL
export ANTHROPIC_AUTH_TOKEN=$GATEWAY_KEY               # sent as "Authorization: Bearer", which LiteLLM reads
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=131072           # the model's max_model_len; Claude Code assumes 200K otherwise
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192              # stay under the model's output limit
export ENABLE_TOOL_SEARCH=false                        # offer the eight RAG tool schemas directly, not behind ToolSearch
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1      # no update checks or telemetry from a closed network
claude --model <gateway model name>
```

Inside the session, `/status` shows an `Anthropic base URL` line pointing at the
gateway and `/mcp` lists `fractal-rag` as connected; from there the
`fractal-explorer` agent should behave as in [Using the
agent](using-the-agent.md). On 2026-10-28 this recipe ran end to end on a
Qwen3-8B backend: Claude Code called `search_artifacts` through the gateway
and answered with cited titles in 18 seconds. The Qwen3.6 and Qwen3.8 backends
rejected every request with `400 System message must be at the beginning.`:
Claude Code 2.1.310 places a `system`-role entry after the user turn (upstream
issue [#77698](https://github.com/anthropics/claude-code/issues/77698)) and
those models' chat templates refuse it, so pick a model whose template accepts
it or use the [Python loop below](#from-python-or-any-openai-compatible-agent),
which worked on every backend. The subagent declares no `model`, so by Claude Code's
[subagent model order](https://code.claude.com/docs/en/sub-agents) it runs on
the session's model (set `CLAUDE_CODE_SUBAGENT_MODEL` to pick another gateway
model for it). An interactive session shows the banner `Model "<name>" isn't
recognized · context assumed to be 200k tokens`, and a `-p` run prints a
`[claude-code:unrecognized_model]` line on stderr; neither is a failure, nor is
the notice that claude.ai connectors are disabled, but the first two are why
`CLAUDE_CODE_MAX_CONTEXT_TOKENS` and `CLAUDE_CODE_MAX_OUTPUT_TOKENS` are set
above: Claude Code otherwise assumes a 200K window and a 32,000-token output
default for a model it does not know. If the gateway answers a context-length
error in its own words, Claude Code does not recognise it as prompt-too-long
and will not compact and retry: run `/compact` yourself.

For a scripted run, offer the model only the RAG tools: `--tools ""` drops the
built-in set, `--strict-mcp-config` loads only the server in `.mcp.json`, and
`--allowedTools` lets the two the prompt needs run without a permission prompt
(it grants permission and removes nothing):

```bash
echo "Use search_artifacts for 'Hurst exponent' (limit 3) and list the titles with their resource URLs." |
  ENABLE_TOOL_SEARCH=false claude -p --model <gateway model name> --tools "" \
    --mcp-config .mcp.json --strict-mcp-config \
    --allowedTools "mcp__fractal-rag__search_artifacts" "mcp__fractal-rag__get_artifact"
```

A `500` from the gateway that reads `Cannot connect to host 127.0.0.1:<port>`
means the gateway is up but the vLLM backend behind that model is not; start
the backend on the inference host (see
[Troubleshooting](troubleshooting.md#claude-code-on-a-local-model-fails-with-cannot-connect-to-host),
which also covers the other gateway errors). Other MCP-capable coding agents
that accept an OpenAI-compatible provider (OpenCode, Codex CLI) can be pointed
at the same gateway and at `fractal-rag serve`; the Python loop below is the
dependency-light version of that.

### From Python or any OpenAI-compatible agent

Without Claude Code the pattern is about seventy lines: offer the MCP tools to
the model as OpenAI function tools and execute the calls it makes. Run it from
the repo root with the `.venv` from step 3 (`.venv/bin/pip install openai` adds
the client; the `mcp` SDK is already a dependency of the package), with `MODEL`
set to one of the names `/v1/models` lists:

```python
"""Ask a local model a question grounded in the Fractal RAG index."""
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

llm = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL", "http://127.0.0.1:8000/v1"),
    api_key=os.environ.get("OPENAI_API_KEY", "none"),  # gateway key; any value for vLLM without --api-key
)
MODEL = os.environ.get("MODEL") or sys.exit("set MODEL to one of the names /v1/models lists")
SYSTEM = (
    "Answer only from the fractal-rag tools. Cite the resource URL of every chunk you use "
    "(fall back to source_uri), and say so when the index has nothing on the question."
)
# The MCP SDK starts the server with a minimal environment: pass the FRACTAL_RAG_* settings through.
SERVER = StdioServerParameters(
    command="fractal-rag",
    args=["serve"],
    env={k: v for k, v in os.environ.items() if k.startswith("FRACTAL_RAG_")},
)


async def main(question: str) -> None:
    async with stdio_client(SERVER) as (read, write), ClientSession(read, write) as rag:
        await rag.initialize()
        tools = [
            {"type": "function", "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": getattr(t, "input_schema", None) or t.inputSchema,
            }}
            for t in (await rag.list_tools()).tools
        ]
        messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
        for _ in range(8):  # at most eight tool rounds, then a final answer
            reply = llm.chat.completions.create(model=MODEL, messages=messages, tools=tools)
            msg = reply.choices[0].message
            if not msg.tool_calls:
                print(msg.content or "(the model returned no text)")
                return
            messages.append({
                "role": "assistant", "content": msg.content or "",
                "tool_calls": [c.model_dump(exclude_none=True) for c in msg.tool_calls],
            })
            for call in msg.tool_calls:
                try:
                    args = json.loads(call.function.arguments or "{}")
                except json.JSONDecodeError as exc:
                    text = f"invalid_argument: tool arguments were not valid JSON ({exc})"
                else:
                    result = await rag.call_tool(call.function.name, args)
                    text = "\n".join(
                        c.text for c in result.content if getattr(c, "type", "") == "text"
                    )
                    if len(text) > 60000:
                        text = text[:60000] + "\n[truncated]"
                messages.append({"role": "tool", "tool_call_id": call.id, "content": text})
        final = llm.chat.completions.create(
            model=MODEL, messages=messages, tools=tools, tool_choice="none"
        )
        print(final.choices[0].message.content or "(the model returned no text)")


asyncio.run(main(" ".join(sys.argv[1:]) or "What does the corpus say about the Hurst exponent?"))
```

```bash
OPENAI_API_KEY=$GATEWAY_KEY MODEL=<gateway model name> .venv/bin/python rag_agent.py \
  "What does the corpus say about the Hurst exponent?"
# bare vLLM server instead of the gateway: add OPENAI_BASE_URL=http://<vllm-host>:<port>/v1
```

`search_artifacts`, `near_artifact` and `artifacts_by_concept` return JSON
arrays of rows with `uuid` (the handle for `get_artifact` and `near_artifact`),
`title`, `summary`, `source_type`, `source_uri`, `resource`, `parent_id`,
`chunk_index`, `year`, `authors`, `tags`, `latex_equations` and `distance`;
`get_artifact` returns one such row plus the full `content`; the concept tools
return concept entries and `corpus_stats` the collection counts.
`search_artifacts` accepts `query`, `limit`, `target_vector`, `alpha`,
`source_types`, `year_min` and `year_max`. The same loop drives anything that
speaks the OpenAI API (vLLM directly, LiteLLM, a hosted model), which is what
keeps the index independent of where inference runs.

## 8. Walk the verification checklist

The eight-prompt checklist lives in the repository's
[verification spec](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/specs/2026-05-23-fractal-rag-agent-verification.md). Target
≥7/8 prompts producing well-cited answers via the `fractal-explorer` agent.
Iteration tips (parser tweaks, swapping the embedding model) are at the
bottom of that doc.

## Operations playbook

### Logs

```bash
kubectl -n ai-workloads logs -f deploy/weaviate
kubectl -n ai-workloads logs -f deploy/t2v-transformers
```

### Restart after a node reboot

```bash
sudo systemctl restart k3s                # if K3s wasn't enabled-on-boot
kubectl -n ai-workloads rollout restart deploy/weaviate
kubectl -n ai-workloads rollout restart deploy/t2v-transformers
```

The manifests pin Weaviate's Raft node name (`CLUSTER_HOSTNAME`), so a
re-created pod rejoins its own single-node cluster; a pod created before that
setting existed recovers through `RAFT_ENABLE_ONE_NODE_RECOVERY` (see
[Troubleshooting](troubleshooting.md#weaviate-pod-stays-01-running-and-exits-every-ten-minutes)).
The name must stay the one the data was written under: Weaviate records it in
each shard's metadata, and a different name makes every read fail with `no read
replica found` after a restart ([Troubleshooting](troubleshooting.md#every-query-fails-with-no-read-replica-found)).
The base says `node1`; the `dgx-spark` overlay patches the reference cluster's
original name.

### Upgrade Weaviate

Change the image tag in `k3s-deployment/base/weaviate-deployment.yaml` and apply
that file alone: the deployment uses the `Recreate` strategy, so the old pod
releases the volume before the new one mounts it, and a full `kubectl apply -k`
would also reset the sidecar to one replica.

```bash
kubectl apply -f k3s-deployment/base/weaviate-deployment.yaml
kubectl -n ai-workloads rollout status deploy/weaviate
curl -s localhost:30080/v1/meta | python -c "import json, sys; print(json.load(sys.stdin)['version'])"
```

Stay at 1.35.3 or newer: 1.35.0 zeroes every keyword score after a bulk delete
(see [Troubleshooting](troubleshooting.md#keyword-bm25-scores-are-0-and-hybrid-ranking-looks-arbitrary)).
The 2026-10-25 move from 1.35.0 to 1.35.23 kept the 104,061 objects and repaired
the scores on restart.

### Re-ingest after a schema change

```bash
fractal-rag schema bootstrap --drop      # destructive: nukes both collections
fractal-rag schema bootstrap
fractal-rag ingest --source all
```

### Swap the embedding model

Edit `k3s-deployment/base/t2v-transformers-deployment.yaml` to change the image
tag (e.g. to `transformers-inference:sentence-transformers-all-mpnet-base-v2`
or `nomic-embed-text-v2-moe`), or the `images:` entry of your overlay, then:

```bash
kubectl apply -k k3s-deployment/base          # or your overlay
kubectl -n ai-workloads rollout status deploy/t2v-transformers
fractal-rag schema bootstrap --drop      # vectors are model-specific
fractal-rag ingest --source all
```

## DGX Spark (arm64) notes

The published `transformers-inference` images are multi-arch, but on arm64 they
ship a CPU-only PyTorch, so the sidecar must be built locally on a CUDA 13 base
(`docker/t2v-transformers-cuda-arm64/build.sh`, arctic-embed-l-v2.0 baked in),
imported into K3s's containerd and selected through the `dgx-spark` overlay:

```bash
bash docker/t2v-transformers-cuda-arm64/build.sh
docker save fractal-rag/t2v-transformers:arctic-embed-l-v2.0-cu130-arm64 | sudo k3s ctr -n k8s.io images import -
kubectl apply -k k3s-deployment/overlays/dgx-spark
```

The device plugin must be v0.17.4 or newer on the GB10 (the base ships v0.20.1),
`nvidia-smi` reports memory as `N/A` on this unified-memory platform, and a pod's
memory limit also caps its GPU allocations. On a GB10 the sidecar embeds about 16
long or 50 short texts per second; a full ingest ran at about 8 chunks per second
with one replica and 14 with two. See `k3s-deployment/README.md` for the full recipe.

## Jetstream2 notes

[Jetstream2](https://docs.jetstream-cloud.org/) is the NSF ACCESS cloud. GPU
instances need an allocation that includes the **Indiana Jetstream2 GPU**
resource ([ACCESS resource page](https://support.access-ci.org/documentation/resources/jetstream2-gpu);
CPU-only allocations carry no GPUs), and instances are launched from Exosphere
or another OpenStack interface. The nodes are x86, so the kustomize base
applies unchanged: follow the host prerequisites in `k3s-deployment/README.md`
(NVIDIA Container Toolkit, the K3s config file including the loopback-only
NodePorts, then the install command) on an Ubuntu featured image. The A100
flavors, from the [instance flavors
page](https://docs.jetstream-cloud.org/general/vmsizes/):

| Flavor | vCPUs | RAM | GPU | GPU memory | SU per hour |
|---|---|---|---|---|---|
| `g3.medium` | 8 | 30 GB | 25% of an A100 (vGPU) | 10 GB | 16 |
| `g3.large` | 16 | 60 GB | 50% of an A100 (vGPU) | 20 GB | 32 |
| `g3.xl` | 32 | 120 GB | one A100 (PCI passthrough) | 40 GB | 64 |

`g4` (L40S, 48 GB per card) and `g5` (H100, 80 GB per card) flavors also exist
but are not available by default: every one of them, single-card included,
needs a justified request to the Jetstream2 help desk. What matters for this
stack:

- Keep the database off the internet. The default Exosphere security group
  admits all inbound traffic and no host firewall is enabled, so an instance
  deployed as-is publishes an anonymous, writable Weaviate on its public
  address. Apply a security group that admits only SSH (plus the ports
  Exosphere's Web Shell or Web Desktop need, if you use them), and put the
  `kube-proxy-arg` from [Keep Weaviate off the
  network](#keep-weaviate-off-the-network) in the K3s config before installing.
- The index alone fits the smallest flavor: the sidecar needs about 3 GB of GPU
  memory and Weaviate runs on the CPU. The 60 GB local disk is too small for the
  31 GB mirror plus the 50 GB Weaviate volume, so attach a volume (or launch the
  instance volume-backed) and put `FRACTAL_RAG_CORPUS_ROOT` and K3s's
  `local-path` directory (`/var/lib/rancher/k3s/storage`) on it before
  installing K3s.
- The partial flavors run NVIDIA vGPU with a proprietary driver preinstalled; the
  full-card `g3.xl` installs the generic NVIDIA driver during its first boot and
  takes longer to appear. We have only run the device plugin against full GPUs
  (the GB10 and A100s), so prefer `g3.xl`, or a `g4`/`g5` flavor once it has
  been granted, and treat the vGPU flavors as untested with these manifests.
- Do not suspend GPU instances (a libvirt bug, per the
  [GPU FAQ](https://docs.jetstream-cloud.org/faq/gpu/)): shelve them when idle
  instead. Jetstream2 also deters resizing full-card instances, so launch a new
  instance on the other flavor rather than resizing.
- Serving a language model next to the index needs more GPU memory than the
  index: the 30B-class NVFP4 models in the reference deployment hold over 20 GB
  of weights before any KV cache. Use a `g4`/`g5` instance for inference once
  granted, or keep inference elsewhere and tunnel the gateway exactly as in
  [Use local vLLM models through a gateway](#use-local-vllm-models-through-a-gateway).

## Where to go next

- Ask the corpus questions → [Using the fractal-explorer agent](using-the-agent.md)
- Pod stuck Pending? GPU not visible? Local model not answering? → [Troubleshooting](troubleshooting.md)
- Move to a lighter local setup for iteration → [Local setup](local-setup.md)
