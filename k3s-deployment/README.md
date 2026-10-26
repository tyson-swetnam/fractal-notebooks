# K3s deployment

Kubernetes manifests for the Fractal RAG stack on a single-node [K3s](https://k3s.io) server with
one NVIDIA GPU: Weaviate 1.35 (NodePorts 30080 HTTP / 30051 gRPC), the `text2vec-transformers`
embedding sidecar on the GPU, and the NVIDIA device plugin. The `fractal-rag` CLI and MCP server
(`fractal_rag/`) target these NodePorts by default; the operator walkthrough is
[docs/fractal-rag/hosted-vm.md](../docs/fractal-rag/hosted-vm.md).

## Layout

| Path | What it is |
|---|---|
| `base/` | kustomize base: `namespace.yaml` (`ai-workloads`), `nvidia-device-plugin-config.yaml` (time-slicing ConfigMap, 2 slices), `nvidia-device-plugin-daemonset.yaml` (plugin v0.20.1), `weaviate-pvc.yaml` (50 Gi, K3s `local-path` class), `weaviate-deployment.yaml`, `weaviate-service.yaml`, `t2v-transformers-deployment.yaml` (published `snowflake-snowflake-arctic-embed-l-latest` image, `ENABLE_CUDA=1`, `runtimeClassName: nvidia`, 1 GPU), `t2v-transformers-service.yaml` |
| `overlays/dgx-spark/` | arm64 NVIDIA DGX Spark (GB10): swaps the sidecar image for the locally built CUDA 13 build (see below) |
| `jupyterlab-*.yaml` | optional, legacy: a GPU JupyterLab written for the former x86 CyVerse node (hard-coded node name, `hostPath` library mounts). Adapt before applying; not part of the kustomize base |

K3s provides two things the manifests rely on: the `nvidia` RuntimeClass (created automatically
when `nvidia-container-runtime` is on K3s's PATH) and the default `local-path` StorageClass
(volumes under `/var/lib/rancher/k3s/storage`).

## Prerequisites (host)

1. NVIDIA driver and the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/):
   `nvidia-smi` works and `/usr/bin/nvidia-container-runtime` exists. No toolkit or containerd
   configuration is needed: K3s detects the runtime at start-up.
2. K3s server configuration, written before the install so it survives upgrades:

   ```yaml
   # /etc/rancher/k3s/config.yaml
   disable:
     - traefik                      # no ingress needed; keeps host ports 80/443 free
   write-kubeconfig-mode: "0640"    # root-owned kubeconfig, readable by one group
   write-kubeconfig-group: "docker" # or a dedicated k3s-admins group
   kube-proxy-arg:
     - nodeport-addresses=127.0.0.0/8  # Weaviate's NodePorts answer on loopback only (it runs with anonymous access)
   ```

3. If `ufw` is enforcing, allow the cluster CIDRs. Check with `sudo ufw status`: only `Status: active`
   counts (an active `ufw.service` with `ENABLED=no` in `/etc/ufw/ufw.conf` enforces nothing, and
   `ufw status` then lists no rules). Nothing else needs opening: `kubectl` talks to
   `127.0.0.1:6443` and the RAG client to `localhost`; Weaviate runs with anonymous access, so do
   not expose 30080/30051 to the network). The `kube-proxy-arg` above is what enforces that: without
   it a NodePort answers on every address of the host, firewall or not. An existing cluster takes the
   same lines followed by `sudo systemctl restart k3s` (running pods are kept):

   ```bash
   sudo ufw allow from 10.42.0.0/16 to any comment 'k3s pod CIDR'
   sudo ufw allow from 10.43.0.0/16 to any comment 'k3s service CIDR'
   ```

4. Install K3s with its embedded containerd (do not use `--docker`: the bundled cri-dockerd rejects
   `runtimeClassName`, and switching Docker's default runtime restarts every Docker workload):

   ```bash
   curl -sfL https://get.k3s.io | sudo env INSTALL_K3S_VERSION="v1.36.5+k3s1" sh -s - server
   export KUBECONFIG=/etc/rancher/k3s/k3s.yaml          # kubectl is symlinked into /usr/local/bin
   kubectl get nodes -o wide && kubectl get runtimeclass nvidia && kubectl get storageclass
   sudo grep -A3 "runtimes.'nvidia'" /var/lib/rancher/k3s/agent/etc/containerd/config.toml   # BinaryName = nvidia-container-runtime
   ```

## Deploy

```bash
kubectl label node "$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')" nvidia.com/gpu.present=true
kubectl apply -k k3s-deployment/base                 # or: kubectl apply -k k3s-deployment/overlays/dgx-spark
kubectl -n kube-system rollout status daemonset/nvidia-device-plugin-daemonset
kubectl get node -o jsonpath='{.items[0].status.allocatable.nvidia\.com/gpu}{"\n"}'   # 2 (time-sliced)
kubectl -n ai-workloads rollout status deployment/t2v-transformers --timeout=20m          # image pull + model load
kubectl -n ai-workloads rollout status deployment/weaviate --timeout=10m
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:30080/v1/.well-known/ready        # 200
kubectl -n ai-workloads logs deploy/t2v-transformers | grep -i -E 'cuda|sentence transformer'  # model on cuda:0
```

The label satisfies the device plugin's `nodeSelector` (there is no GPU feature discovery here).
A plugin older than v0.17.4 crashes on unified-memory GPUs such as the GB10 ("error getting device
memory: Not Supported"); v0.20.1 logs that condition and carries on. Time-slicing advertises
`nvidia.com/gpu: 2` so the sidecar and one more pod (a notebook, a second sidecar replica) can share
the GPU; there is no memory or fault isolation between slices, and MIG and MPS are unavailable on GB10.

Then, from the repository root with the `fractal_rag` package installed:

```bash
fractal-rag schema bootstrap
fractal-rag pull                     # iRODS mirror (FRACTAL_RAG_IRODS_ROOT / FRACTAL_RAG_CORPUS_ROOT)
fractal-rag ingest --source all
fractal-rag status
```

## NVIDIA DGX Spark (arm64, GB10)

The images Weaviate publishes for `transformers-inference` are multi-arch, but their arm64 variant
installs the PyPI PyTorch wheel, which has no CUDA support on aarch64: with `ENABLE_CUDA=1` the pod
dies with `AssertionError: Torch not compiled with CUDA enabled`. Build the same upstream app on a
CUDA 13 base with the `cu130` PyTorch wheel and the arctic-embed-l-v2.0 model instead, import it
into K3s's containerd (K3s does not read the Docker image store), and apply the overlay:

```bash
bash docker/t2v-transformers-cuda-arm64/build.sh                 # -> fractal-rag/t2v-transformers:arctic-embed-l-v2.0-cu130-arm64 (~8 GB)
docker save fractal-rag/t2v-transformers:arctic-embed-l-v2.0-cu130-arm64 | sudo k3s ctr -n k8s.io images import -
kubectl apply -k k3s-deployment/overlays/dgx-spark
```

Measured on a GB10: the model takes about 2.3 GB of GPU memory (about 3 GB per running replica)
and embeds roughly 16 long (350-word) or 50 short texts per second. Platform notes: `nvidia-smi`
reports memory as `N/A` (unified memory, expected); a container's `resources.limits.memory` also
caps its GPU allocations (the sidecar's 24 Gi limit is per pod and ample for one model, so a second
replica needs no manifest change); PyTorch 2.9 warns that compute capability 12.1 is newer than its
tested range and runs through PTX, which works.

## Operations

```bash
kubectl -n ai-workloads get pods -o wide
kubectl -n ai-workloads logs -f deploy/weaviate
kubectl -n ai-workloads rollout restart deploy/t2v-transformers
kubectl -n ai-workloads scale deploy/t2v-transformers --replicas=2   # one pod per GPU time slice; ~14 vs ~8 chunks/s on a GB10
sudo ls /var/lib/rancher/k3s/storage/                    # Weaviate data (PVC)
sudo /usr/local/bin/k3s-uninstall.sh                     # remove K3s (data under /var/lib/rancher is deleted too)
```

Swapping the embedding model: change the image (base manifest or an overlay `images:` entry), roll
the deployment, then `fractal-rag schema bootstrap --drop` and re-ingest, because vectors are
model-specific.

Upgrading Weaviate: change the tag in `base/weaviate-deployment.yaml` (1.35.3 or newer; 1.35.0
zeroes every BM25 score after a bulk delete, weaviate/weaviate#10102) and `kubectl apply -f` that
file. The deployment's `Recreate` strategy stops the old pod before the new one mounts the volume,
and the pinned `CLUSTER_HOSTNAME=node1` plus `RAFT_ENABLE_ONE_NODE_RECOVERY=true` let a re-created
pod rejoin, or recover, its single-node Raft cluster; without the pinned name a re-created pod exits
after `RAFT_BOOTSTRAP_TIMEOUT` with `could not join raft join list`.
