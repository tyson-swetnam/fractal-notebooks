# Docker image for the Streamlit apps

`docker/Dockerfile` packages the Streamlit applications in [`apps/`](../apps/README.md) into a
single-stage image on `python:3.11-slim`. It installs the scientific-Python stack the apps need
(`streamlit numpy scipy matplotlib plotly pillow imageio pandas shapely`), copies `apps/` to
`/app/apps/`, exposes port 8501 and starts `streamlit run apps/tree_roots_3d.py`. There is no
requirements file, no build stage and no non-root user; the container runs as root like the base
image.

## Build and run

Build from the **repository root**. The Dockerfile copies `apps/`, so the build context must be
the root, not this directory:

```bash
docker build -f docker/Dockerfile -t fractal-app .
docker run -p 8501:8501 fractal-app          # http://localhost:8501
```

Serve another app by overriding the command (the working directory inside the container is `/app`):

```bash
docker run -p 8501:8501 fractal-app streamlit run apps/cones.py --server.address=0.0.0.0
```

Any of the twelve Streamlit apps (the `apps/*.py` files that `import streamlit`) works. The other
scripts in `apps/` are plain matplotlib/PIL programs that write an image or GIF; run them with
`python`, not `streamlit`. The catalogue is on the
[Streamlit Apps](../docs/applications/streamlit-apps.md) page.

For live editing, mount your working copy of `apps/` over the copy baked into the image:

```bash
docker run -p 8501:8501 -v "$PWD/apps:/app/apps" fractal-app
```

## Configuration

Streamlit reads its settings from environment variables passed with `docker run -e ...`, for
example `STREAMLIT_SERVER_HEADLESS=true`, `STREAMLIT_SERVER_PORT=8501` or
`STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`. The image sets nothing beyond
`--server.address=0.0.0.0` in its `CMD`.

## Related

- [`docker/fractal-rag/docker-compose.yaml`](fractal-rag/docker-compose.yaml) is a separate, local
  Docker Compose stack (Weaviate plus a CPU embedder) for the Fractal RAG package; see
  [Fractal RAG: local setup](../docs/fractal-rag/local-setup.md).
- [`k3s-deployment/`](../k3s-deployment/) holds the K3s manifests for JupyterLab and Weaviate.
  They use upstream images and do not build or deploy this one.
