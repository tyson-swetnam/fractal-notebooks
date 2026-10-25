#!/usr/bin/env bash
# Build the Weaviate text2vec-transformers sidecar for arm64 + CUDA 13 (NVIDIA DGX Spark / GB10).
# The images Weaviate publishes ship a CPU-only PyTorch on arm64, so the same upstream app
# (weaviate/t2v-transformers-models) is rebuilt on a CUDA 13 base with the cu130 PyTorch wheel and
# the arctic-embed-l-v2.0 model baked in. Needs Docker (no root) and network access to GitHub,
# the PyTorch index and the Hugging Face Hub. Takes ~15 minutes; the result is ~8 GB.
#
#   bash docker/t2v-transformers-cuda-arm64/build.sh            # -> fractal-rag/t2v-transformers:arctic-embed-l-v2.0-cu130-arm64
#   MODEL_NAME=Snowflake/snowflake-arctic-embed-m-v1.5 TAG=... bash docker/t2v-transformers-cuda-arm64/build.sh
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_NAME="${MODEL_NAME:-Snowflake/snowflake-arctic-embed-l-v2.0}"
TAG="${TAG:-fractal-rag/t2v-transformers:arctic-embed-l-v2.0-cu130-arm64}"
UPSTREAM_REF="${UPSTREAM_REF:-ad93b21}"   # weaviate/t2v-transformers-models commit this recipe was tested with
WORK="${WORK:-$(mktemp -d)}"

git clone -q https://github.com/weaviate/t2v-transformers-models "$WORK/src"
git -C "$WORK/src" checkout -q "$UPSTREAM_REF" 2>/dev/null || echo "note: ref $UPSTREAM_REF not found, building the default branch"

docker build --progress=plain \
  -f "$HERE/Dockerfile" --build-context patch="$HERE" \
  --build-arg MODEL_NAME="$MODEL_NAME" \
  --build-arg USE_SENTENCE_TRANSFORMERS_VECTORIZER=true \
  --build-arg ONNX_RUNTIME=false \
  --build-arg TRUST_REMOTE_CODE=false \
  -t "$TAG" "$WORK/src"
docker image inspect "$TAG" --format 'built {{.RepoTags}} arch={{.Architecture}} size={{.Size}}'
echo "smoke test: docker run --rm --gpus all -e ENABLE_CUDA=1 -p 127.0.0.1:8090:8080 $TAG  # then curl :8090/.well-known/ready"
