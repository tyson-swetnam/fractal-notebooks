# Weaviate text2vec-transformers sidecar (weaviate/t2v-transformers-models app) rebuilt for
# arm64 + CUDA 13 so it can use the GB10 on a DGX Spark. The upstream image installs the
# PyPI torch wheel, which is CPU-only on aarch64 ("Torch not compiled with CUDA enabled").
# Build context: a checkout of https://github.com/weaviate/t2v-transformers-models
#   see build.sh in this directory
ARG BASE_IMAGE=nvidia/cuda:13.0.1-base-ubuntu24.04
FROM ${BASE_IMAGE} AS base_image
ENV DEBIAN_FRONTEND=noninteractive PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1 \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-venv python3-pip ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH
WORKDIR /app
COPY requirements.txt .
# CUDA 13 aarch64 PyTorch from the PyTorch index, then the upstream pins minus the torch line.
RUN pip install --upgrade pip setuptools wheel \
 && pip install --index-url https://download.pytorch.org/whl/cu130 "torch==2.9.1" \
 && grep -v -E '^torch==' requirements.txt > /tmp/req-notorch.txt \
 && pip install -r /tmp/req-notorch.txt \
 && python -c "import torch; print('torch', torch.__version__, 'cuda build', torch.version.cuda)"

FROM base_image AS download_model
WORKDIR /app
ARG MODEL_NAME
ARG ONNX_RUNTIME=false
ARG TRUST_REMOTE_CODE=false
ARG USE_SENTENCE_TRANSFORMERS_VECTORIZER=false
ENV ONNX_CPU=arm64
RUN mkdir nltk_data
COPY download.py .
# optimum 1.27 cannot be imported under torch 2.9; the ONNX path is unused, so import it lazily.
COPY --from=patch patch_lazy_onnx.py /tmp/patch_lazy_onnx.py
RUN python /tmp/patch_lazy_onnx.py download.py
RUN ./download.py

FROM base_image AS t2v_transformers
WORKDIR /app
COPY --from=download_model /app/models /app/models
COPY --from=download_model /app/nltk_data /app/nltk_data
COPY . .
COPY --from=patch patch_lazy_onnx.py /tmp/patch_lazy_onnx.py
RUN python /tmp/patch_lazy_onnx.py download.py vectorizer.py && rm /tmp/patch_lazy_onnx.py
# The model is baked in; never phone home to the Hub at runtime.
ENV HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
ENTRYPOINT ["/bin/sh", "-c"]
CMD ["uvicorn app:app --host 0.0.0.0 --port 8080"]
