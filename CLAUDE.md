# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

It is also read by **Claude Science** and any agent that honors the `CLAUDE.md` /
`AGENTS.md` convention (`AGENTS.md` is a symlink to this file). Keep it tool-agnostic
where possible and mark tool-specific behavior explicitly.

## Project Overview

Fractal Notebooks is a research + teaching platform on self-affine fractals and
metabolic scaling theory. Six components:

- **MkDocs documentation** (`docs/`) — the "Self-Affinity in Nature" site, published to GitHub Pages.
- **React web applications** (`react/`) — TypeScript/React fractal visualizers deployed to `/react`.
- **Streamlit Python apps** (`apps/`) — 21 interactive fractal generators on the scientific-Python stack.
- **Fractal RAG stack** (`fractal_rag/`) — Weaviate-backed retrieval + MCP server. Design spec: `docs/superpowers/specs/2026-05-23-fractal-rag-agent-design.md`.
- **OKF knowledge bundles** (`okf/`) — the concept ontology and appendix proofs as Open Knowledge Format v0.1 Markdown.
- **Deployment** (`k3s-deployment/`, `docker/`) — K3s manifests (Weaviate 1.35 + GPU embedding sidecar, JupyterLab), a Streamlit Docker image, and a local Docker Compose RAG stack.

Design specs and plans live in `docs/superpowers/specs/`; the docs book structure is in `PLAN.md`.

## Environments

Prefer a pinned conda environment over ad-hoc `pip install`:

- `environments/fractal-foundations-gpu.yml` — GPU/CUDA stack for the foundations notebooks (fractal generators, dimension theory). Targets NVIDIA driver 535.x / CUDA 12.2.
- `environments/3dep-environment.yml` — geospatial / 3DEP terrain analysis.
- `fractal_rag/pyproject.toml` — the RAG package; install editable with `pip install -e ".[dev,parsers]"` (Python ≥ 3.10).
- `requirements.txt` — MkDocs docs toolchain only.

**Claude Science note:** create a dedicated conda env from the relevant `.yml` and pass
`environment=` on every code cell; do not install heavyweight stacks into the shared
default env. Prepare files in `python`, then reach the MCP server from the `repl` tool.

## Common Commands

### Documentation (MkDocs — current)
```bash
pip install -r requirements.txt
python -m mkdocs serve          # http://localhost:8000
mkdocs build --site-dir site    # production build (what CI runs)
```

### React Application (Vite)
```bash
cd react
npm ci
npm start                       # http://localhost:33000/fractal-notebooks/react/
npm run build                   # tsc -b && vite build → react/build/
npm run type-check              # run before committing
npm run lint
```
There is no React test runner; CI gates on `build`, `type-check`, and `lint`.

### Streamlit Applications
```bash
streamlit run apps/mandelbrot.py   # any apps/*.py runs standalone
```

### Fractal RAG package
```bash
cd fractal_rag
pytest                                          # unit tests (tests/unit)
pytest tests/unit/test_chunk.py -k <name>       # single test
ruff check src tests && mypy src
fractal-rag concepts validate                   # check seed.yaml
fractal-rag okf export --out ../okf/concepts    # regenerate the OKF concept bundle
fractal-rag status                              # collection counts
fractal-rag query "<text>"                      # ad-hoc hybrid search
```
The `integration` pytest marker (testcontainers Weaviate) is declared in `pyproject.toml`,
but no `tests/integration/` directory exists yet.

### Docker
```bash
cd docker && docker build -t fractal-app . && docker run -p 8501:8501 fractal-app
```

## The Fractal RAG knowledge stack

`fractal_rag/` builds a Weaviate index over four content types — Constellate
scholarly-article exports (`json`), Jupyter notebooks (`notebooks`), MkDocs
markdown (`docs`), and reference PDFs (`pdfs`) — these are the `--source` values
for `fractal-rag ingest`. It also keeps a hand-curated `Concept` side-collection
(31 seeded canonical concepts in `fractal_rag/src/fractal_rag/concepts/seed.yaml`)
and exposes eight retrieval tools over an MCP server. The stack is **read-only by
design** — it retrieves and synthesizes, it does not mutate the corpus.

Configuration is via `FRACTAL_RAG_*` env vars (`fractal_rag/src/fractal_rag/config.py`).
Defaults point Weaviate at the K3s NodePorts (`localhost:30080` HTTP / `30051` gRPC).

Bring it up — either on K3s:
```bash
kubectl apply -f k3s-deployment/   # Weaviate 1.35 + Arctic-embed-l-v2.0 GPU sidecar
```
or locally without a GPU (CPU `bge-small` embedder; override the port):
```bash
docker compose -f docker/fractal-rag/docker-compose.yaml up -d
export FRACTAL_RAG_WEAVIATE_HTTP_PORT=8080 FRACTAL_RAG_WEAVIATE_GRPC_PORT=50051
```
then:
```bash
cd fractal_rag && pip install -e ".[dev,parsers]"
fractal-rag schema bootstrap
fractal-rag pull                # gocmd-backed iRODS sync (one-time, ~30 GB)
fractal-rag ingest --source all # or json | notebooks | docs | pdfs; --limit N for smoke tests
```

**Reaching the MCP server depends on the tool:**

- **Claude Code** picks up `.mcp.json`, which runs the bare `fractal-rag serve` over stdio.
  The `fractal-rag` executable must be on `PATH` (activate the env where the package is
  installed before launching Claude Code), otherwise the server fails with `ENOENT`. The
  `fractal-explorer` subagent (`.claude/agents/fractal-explorer.md`) is scoped to the eight
  retrieval tools.
- **Claude Science** reaches a connected MCP server via `host.mcp("fractal-rag", "<tool>", ...)`
  from the **`repl` tool** (not `python`/`r`). Add the server under
  *Customize → Connectors* first; then discover its tools with
  `search_skills({prefix: "mcp-fractal-rag"})`. Pass results to `python`/`r` through
  `./handoff/*.json`.

The eight tools: `search_artifacts`, `get_artifact`, `near_artifact`,
`artifacts_by_concept`, `list_concepts`, `get_concept`, `search_concepts`,
`corpus_stats`. See `fractal_rag/README.md` and the design spec for signatures and the
tool-selection rubric.

## OKF bundles (`okf/`)

- **`okf/concepts/`** is **generated** from `concepts/seed.yaml` by `fractal-rag okf export`
  (`fractal_rag/src/fractal_rag/okf_export.py`). Never hand-edit it: edit the seed and
  re-export. Concepts are grouped into folders by their first domain tag; each level has
  `index.md` (progressive disclosure) and `log.md` (change history); the root `index.md`
  declares `okf_version: "0.1"`.
- **`okf/proofs/`** is **hand-authored**: `type: Fractal Proof` documents backing the
  quantitative claims in `docs/foundations/history.md`. Every proof step is tagged
  `[verified]` (checked with SymPy/NumPy, reproducibly) or `[asserted]` (rests on a cited
  named theorem), and the frontmatter `verification_status` is
  `verified` | `partially-verified` | `unverified`. Add a `log.md` entry and an `index.md`
  line when adding a proof.

## Agents & Specialists

This repo ships one agent role today — **`fractal-explorer`**, a citation-grounded
retrieval/synthesis agent over the RAG corpus.

- **Claude Code:** defined as a subagent in `.claude/agents/fractal-explorer.md`
  (YAML frontmatter + system prompt + explicit `tools:` allowlist).
- **Claude Science:** the same role should be registered as a **Specialist** agent
  profile via `host.agents.create(...)` (load the `customize` skill for the API). A
  Specialist captures the role's instructions + vocabulary and can be restricted to a
  connector/skill subset — here, the `mcp-fractal-rag` tools plus read-only file access.
  The frontmatter `description`, system prompt, and tool list in
  `.claude/agents/fractal-explorer.md` port over directly. Keep the two definitions in
  sync; treat the Markdown file as the source of truth for the prompt text.

When adding a new role, write the Claude Code subagent first (it version-controls
cleanly), then mirror it as a Specialist profile.

## Architecture

### React (`react/src/`)
- HashRouter for GitHub Pages; Vite `base` is `/fractal-notebooks/react/`.
- Adding a page takes two edits: import + `<Route>` in `App.tsx`, and an entry in the
  nav config in `components/layout/Navigation.tsx`. Pages live under
  `pages/{fractals-1d-2d-3d,branching-architectures,riemann-zeta-functions}/`.
- `components/controls/` is the shared UI kit (`AppScaffold`, `ControlSection`,
  `ParameterSlider`, `ParameterSelect`, `ActionBar`, `CollapsiblePanel`); build new
  pages on it rather than ad-hoc MUI layouts.
- `utils/` holds the compute engines: WebGL Mandelbrot/Julia, noise generators,
  L-system / plant engine + presets, and MUI themes.
- ThemeContext (light/dark/system, persisted to localStorage, MUI-integrated). Viz: D3, Plotly, KaTeX.

### Streamlit (`apps/`)
- Each `.py` is self-contained and independently runnable. NumPy, Matplotlib, Plotly, SciPy, Numba. Runtime GIFs/images stay local.

### Documentation (`docs/`)
- MkDocs Material, custom `fractals` palette, `mkdocs-jupyter` embeds (notebooks in `docs/notebooks/`), MathJax.
- Structured per `PLAN.md`: Part I Foundations (tutorial), then research chapters (biological-geometry, metabolic-scaling, spectral-geometry, hypotheses).

### Kubernetes (`k3s-deployment/`)
- JupyterLab + Weaviate with persistent storage, NVIDIA device plugin, local-path storage class.

## CI/CD

`.github/workflows/deploy-all.yaml` (push to `main`) builds MkDocs into `site/` and
React into `react/build/`, merges them (React under `/react`, with `index.html` copied
to `404.html`, and a `/react-apps` → `/react` redirect), and deploys to GitHub Pages.
`test-build.yaml` (PRs) runs the MkDocs build and React build + type-check + lint.
The RAG package has no CI yet.

## Change & Commit Policy

**Tool-specific — do not apply blindly.**

- **Claude Code:** after a prompt that modifies files, commit immediately:
  ```bash
  git add <files> && git commit -m "<concise description>"
  ```
  Messages start with a verb (Add/Update/Fix/Remove/Refactor/Implement), first line
  < 72 chars, reference the request when relevant.
- **Claude Science:** do **not** auto-commit. Produce results as **artifacts**
  (`save_artifacts`) and surface a diff; commit only on explicit user instruction, and
  never `rm` inside a granted host path (use the platform's delete flow). Git history is
  still the recovery path — keep commits atomic and message-consistent when you do commit.

## Key Dependencies

- **React:** React 18, Vite 7, MUI 5, D3 7, Plotly, react-router-dom 6, TypeScript 5, KaTeX, ESLint 9.
- **Python (docs):** mkdocs-material, mkdocs-jupyter, mkdocstrings, pymdown-extensions.
- **Python (apps):** streamlit, numpy, matplotlib, plotly, scipy, numba, pillow, imageio.
- **Python (RAG):** weaviate-client v4, MCP SDK, click, pydantic-settings, nbformat, mistune, pdfminer.six (`.[parsers]`).

## Roadmap — Zensical + OKF publishing

Material for MkDocs is in maintenance mode; Zensical is its successor and reads the
existing `mkdocs.yml` natively. The plan (spec: `docs/superpowers/specs/2026-07-13-zensical-migration.md`,
status Draft) is a non-blocking parallel `zensical build` job in CI until parity covers
the plugins this site uses (`mkdocs-jupyter`, MathJax, PDF export, git-revision-date),
then switch, and publish the `okf/` bundles through the site. Remaining hygiene items are
tracked in `SPECIALIST_READINESS.md`.
