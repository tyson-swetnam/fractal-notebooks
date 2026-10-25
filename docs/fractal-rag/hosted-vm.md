---
type: Guide
title: "Fractal RAG: Hosted VM (K3s + GPU)"
description: >-
  Production deployment of the Fractal RAG stack on a single GPU VM with K3s:
  NVIDIA device plugin, Weaviate 1.35 and the arctic-embed sidecar manifests,
  iRODS corpus pull, full ingest, remote MCP over SSH and an operations
  playbook.
resource: https://tyson-swetnam.github.io/fractal-notebooks/fractal-rag/hosted-vm/
tags: [knowledge, rag, weaviate, cuda, mcp]
generated:
  by: human:tswetnam
  at: "2026-05-24T00:00:00Z"
status: stable
---

# Hosted VM (K3s + GPU)

This page covers the production-grade deployment: a single VM (CyVerse
Jetstream-2, an on-prem GPU node, or any host with NVIDIA drivers) running
K3s, with Weaviate 1.35 and the `snowflake-arctic-embed-l-v2.0`
text2vec-transformers sidecar pinned to a GPU.

This is the topology the `k3s-deployment/*.yaml` manifests in this repo
target. Once it's up you ingest the full ~50K-article corpus and either
run Claude Code on the same host, or expose the MCP server to a remote
workstation over SSH.

## Reference hardware

The repo was originally built and tested on:

- AMD EPYC 7713 (256 vCPU), 503 GB RAM
- 3× NVIDIA A100 80 GB
- 5.5+ TB free on `/opt`
- Ubuntu 22.04 / 24.04

You can run on far less. Minimum: 1 modern NVIDIA GPU with ≥16 GB VRAM,
8 vCPU, 32 GB RAM, 100 GB free disk.

## Prerequisites

| Need | Notes |
|---|---|
| K3s | `curl -sfL https://get.k3s.io \| sudo env INSTALL_K3S_VERSION=v1.36.5+k3s1 sh -s - server`, with `/etc/rancher/k3s/config.yaml` written first (no Traefik, kubeconfig mode and group) and, only if `ufw` is enforcing, the two cluster-CIDR rules; embedded containerd, not `--docker`. Details in `k3s-deployment/README.md` |
| NVIDIA driver + container toolkit | `nvidia-smi` must work and the NVIDIA Container Toolkit must be installed; K3s detects `nvidia-container-runtime` at start-up and creates the `nvidia` RuntimeClass the GPU pods request |
| `kubectl` | installed by K3s into `/usr/local/bin`; `export KUBECONFIG=/etc/rancher/k3s/k3s.yaml` |
| `gocmd` v0.11.5+ | for the iRODS pull; `~/.irods/` must already be authenticated |
| `helm` (optional) | not required by these manifests |

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
StorageClass the PVC requests.

```bash
kubectl label node <node> nvidia.com/gpu.present=true   # the device plugin's nodeSelector
kubectl apply -k k3s-deployment/base
kubectl -n kube-system rollout status daemonset/nvidia-device-plugin-daemonset
```

Verify GPUs are now schedulable:

```bash
kubectl describe node | grep -A2 "nvidia.com/gpu"
#  Allocatable:
#   nvidia.com/gpu:  3
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
curl -s localhost:30080/v1/.well-known/ready              # 200 OK
curl -s localhost:30080/v1/meta | jq '.modules | keys'    # ["text2vec-transformers"]
```

And from inside the cluster, confirm the sidecar is also healthy:

```bash
kubectl -n ai-workloads exec deploy/weaviate -- \
  wget -qO- http://t2v-transformers:8080/.well-known/ready
# {"status":"ready"}
```

## 3. Install the `fractal-rag` package on the host

```bash
cd /opt/tswetnam/github/fractal-notebooks/fractal_rag
pip install -e ".[dev,parsers]"
fractal-rag concepts validate            # OK: 32 concepts validated
```

The default `config.py` already targets the NodePort `30080`/`30051` exposed
by `weaviate-service.yaml`, and `repo_root` defaults to
`/opt/tswetnam/github/fractal-notebooks`, so a checkout at that path needs no
environment overrides. If the repository lives anywhere else, set
`FRACTAL_RAG_REPO_ROOT` before `ingest --source docs` or `--source notebooks`,
for example in a gitignored `.env` at the repo root, which is read when you run
`fractal-rag` from there. Those two sources index nothing, without an error,
when the path does not exist.

## 4. Bootstrap the schema

```bash
fractal-rag schema bootstrap
# { "created": ["Concept", "FractalArtifact"], "already_present": [] }
```

## 5. Pull the corpus from iRODS

```bash
fractal-rag pull
# Mirrors /iplant/home/tswetnam/projects/fractal-notebooks/ -> /opt/tswetnam/fractal-notebooks/
# (override with FRACTAL_RAG_IRODS_ROOT / FRACTAL_RAG_CORPUS_ROOT, e.g. when /opt is not writable)
# ~30 GB. Resumable; gocmd skips files whose checksums already match.
```

## 6. Run the full ingest

```bash
fractal-rag ingest --source all 2>&1 | tee ~/fractal-rag-ingest.log
```

Measured on the DGX Spark (2026-10-25): the docs finish in about a minute, the
notebooks in about five, and the 50,000 JSONL records take about two hours at
14 chunks per second with two sidecar replicas (every chunk is three vectors).
The ingest inserts one chunk at a time, so the GPU is not the bottleneck; the
second replica, which uses the second GPU time slice, is the only cheap lever:

```bash
kubectl -n ai-workloads scale deploy/t2v-transformers --replicas=2
```

Watch progress with:

```bash
kubectl -n ai-workloads logs -f deploy/t2v-transformers
fractal-rag status                       # repeat to see counts climbing
```

When it finishes, sanity-check that all four source types landed. Expect fewer
json objects than the `inserted_chunks` the run reports: on 2026-10-25 the run
wrote 100,012 chunks but 97,762 remain, because 1,125 of the 50,000 records
share a DOI with an earlier record and the json parser derives the object UUID
from the DOI, so the later record overwrites the earlier one.

```bash
fractal-rag status
# { "FractalArtifact": 101811, "Concept": 32 }   # 2026-10-25: 512 docs + 3,537 notebook + 97,762 json chunks

# Inspect by source_type:
python -c "
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

## 7. Wire Claude Code

### Option A — Run Claude Code on the same VM

The repo's `.mcp.json` references `fractal-rag serve` on PATH. Just open
Claude Code in the repo and run `/mcp` to confirm `fractal-rag` is connected,
then invoke the subagent (see [Using the fractal-explorer
agent](using-the-agent.md)).

### Option B — Run Claude Code on a workstation, MCP on the VM

Use SSH to wrap the remote `fractal-rag serve` so its stdio shows up locally:

```jsonc
// On your workstation, drop this into the project's .mcp.json:
{
  "mcpServers": {
    "fractal-rag": {
      "command": "ssh",
      "args": [
        "-T",
        "-o", "ServerAliveInterval=30",
        "user@your-gpu-vm.example.org",
        "cd /opt/tswetnam/github/fractal-notebooks/fractal_rag && fractal-rag serve"
      ]
    }
  }
}
```

The MCP protocol runs over stdin/stdout, so SSH (which forwards exactly
those) needs no extra setup. Keys-only auth is recommended; password prompts
will break the connection.

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

## Where to go next

- Run the eight-prompt agent checklist → [Using the fractal-explorer agent](using-the-agent.md)
- Pod stuck Pending? GPU not visible? → [Troubleshooting](troubleshooting.md)
- Move to a lighter local setup for iteration → [Local setup](local-setup.md)
