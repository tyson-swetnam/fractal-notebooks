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
| K3s | `curl -sfL https://get.k3s.io \| sh -` |
| NVIDIA driver + container runtime | `nvidia-smi` must work on the host; K3s picks up the NVIDIA runtime via the `nvdp.yaml` manifest in this repo |
| `kubectl` | `sudo ln -s /usr/local/bin/k3s /usr/local/bin/kubectl` (or use `k3s kubectl ...`) |
| `gocmd` v0.11.5+ | for the iRODS pull; `~/.irods/` must already be authenticated |
| `helm` (optional) | not required by these manifests |

Quick host checks:

```bash
nvidia-smi                                 # GPUs visible to the OS
sudo systemctl status k3s                  # active (running)
kubectl get nodes -o wide                  # node Ready, GPU label present
```

## 1. Create the namespace + storage class + GPU plugin

```bash
kubectl apply -f k3s-deployment/namespace.yaml
kubectl apply -f k3s-deployment/storageclass.yaml
kubectl apply -f k3s-deployment/nvidia-device-plugin-daemonset.yaml
kubectl -n kube-system get pods | grep nvidia-device-plugin   # Running
```

Verify GPUs are now schedulable:

```bash
kubectl describe node | grep -A2 "nvidia.com/gpu"
#  Allocatable:
#   nvidia.com/gpu:  3
```

## 2. Deploy Weaviate + the embedding sidecar

```bash
kubectl apply -f k3s-deployment/weaviate-pvc.yaml
kubectl apply -f k3s-deployment/weaviate-deployment.yaml
kubectl apply -f k3s-deployment/weaviate-service.yaml
kubectl apply -f k3s-deployment/t2v-transformers-deployment.yaml
kubectl apply -f k3s-deployment/t2v-transformers-service.yaml

# Wait for both pods to go Ready (first start pulls ~6 GB of images +
# downloads the embedding model; budget 5-10 minutes).
kubectl -n ai-workloads get pods -w
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
fractal-rag concepts validate            # OK: 31 concepts validated
```

The default `config.py` already targets the NodePort `30080`/`30051` exposed
by `weaviate-service.yaml`, so no environment overrides are needed.

## 4. Bootstrap the schema

```bash
fractal-rag schema bootstrap
# { "created": ["Concept", "FractalArtifact"], "already_present": [] }
```

## 5. Pull the corpus from iRODS

```bash
fractal-rag pull
# Mirrors /iplant/home/tswetnam/fractal-notebooks/ -> /opt/tswetnam/fractal-notebooks/
# ~30 GB. Resumable; gocmd skips files whose checksums already match.
```

## 6. Run the full ingest

```bash
fractal-rag ingest --source all 2>&1 | tee ~/fractal-rag-ingest.log
```

A full ingest on the reference hardware takes ~30-90 minutes — most of the
wall clock is spent waiting on the GPU sidecar to embed the 50K JSONL records
(the markdown + notebooks finish in seconds). Watch progress with:

```bash
kubectl -n ai-workloads logs -f deploy/t2v-transformers
fractal-rag status                       # repeat to see counts climbing
```

When it finishes, sanity-check that all four source types landed:

```bash
fractal-rag status
# { "FractalArtifact": 75000+, "Concept": 31 }

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

The eight-prompt checklist lives at
`docs/superpowers/specs/2026-05-23-fractal-rag-agent-verification.md`. Target
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

Edit `k3s-deployment/t2v-transformers-deployment.yaml` to change the image
tag (e.g. to `transformers-inference:sentence-transformers-all-mpnet-base-v2`
or `nomic-embed-text-v2-moe`), then:

```bash
kubectl apply -f k3s-deployment/t2v-transformers-deployment.yaml
kubectl -n ai-workloads rollout status deploy/t2v-transformers
fractal-rag schema bootstrap --drop      # vectors are model-specific
fractal-rag ingest --source all
```

## Where to go next

- Run the eight-prompt agent checklist → [Using the fractal-explorer agent](using-the-agent.md)
- Pod stuck Pending? GPU not visible? → [Troubleshooting](troubleshooting.md)
- Move to a lighter local setup for iteration → [Local setup](local-setup.md)
