# CLAUDE.md

Guidance for AI coding/analysis agents working in this repository. It is read by
**Claude Code** (`claude.ai/code`), **Claude Science**, and any agent that honors the
`CLAUDE.md` / `AGENTS.md` convention. Keep it tool-agnostic where possible and mark
tool-specific behavior explicitly.

> `AGENTS.md` is a symlink to this file so non-Claude agents pick up the same guidance.

## Project Overview

Fractal Notebooks is a research + teaching platform on self-affine fractals and
metabolic scaling theory. Five components:

- **MkDocs documentation** (`docs/`) — the "Self-Affinity in Nature" site, published to GitHub Pages.
- **React web applications** (`react/`) — TypeScript/React fractal visualizers deployed to `/react`.
- **Streamlit Python apps** (`apps/`) — 21 interactive fractal generators on the scientific-Python stack.
- **Fractal RAG stack** (`fractal_rag/`) — Weaviate-backed retrieval + MCP server. Design spec: `docs/superpowers/specs/2026-05-23-fractal-rag-agent-design.md`.
- **Deployment** (`k3s-deployment/`, `docker/`) — K3s manifests (Weaviate 1.35 + GPU embedding sidecar, JupyterLab) and a Streamlit Docker image.

**Direction of travel** (see *Roadmap* below): wrap the knowledge in this repo as an
**Open Knowledge Format (OKF)** bundle and publish the docs via **Zensical** (the
Material-for-MkDocs successor), with Claude Science **Specialists** as the primary
agent-facing consumers.

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
mkdocs build --site-dir site    # production build
```

### React Application (Vite)
```bash
cd react
npm ci
npm start                       # http://localhost:33000
npm run build
npm run type-check              # run before committing
npm run lint
```

### Streamlit Applications
```bash
streamlit run apps/mandelbrot.py
streamlit run apps/branching_tree.py
streamlit run apps/julia.py
```

### Docker
```bash
cd docker && docker build -t fractal-app . && docker run -p 8501:8501 fractal-app
```

## The Fractal RAG knowledge stack

`fractal_rag/` builds a Weaviate index over four content types — Constellate
scholarly-article exports (`json_corpus`), Jupyter notebooks (`notebook`), MkDocs
markdown (`markdown`), and reference PDFs (`pdf`) — plus a hand-curated `Concept`
side-collection (31 seeded canonical concepts in
`fractal_rag/src/fractal_rag/concepts/seed.yaml`). It exposes eight retrieval tools
over an MCP server. The stack is **read-only by design** — it retrieves and
synthesizes, it does not mutate the corpus.

Bring it up:
```bash
# 1. K3s manifests define Weaviate 1.35 + a text2vec-transformers
#    (Arctic-embed-l-v2.0) GPU sidecar.
kubectl apply -f k3s-deployment/

# 2. Install + bootstrap the RAG package
cd fractal_rag && pip install -e ".[dev,parsers]"
fractal-rag schema bootstrap
fractal-rag pull                # gocmd-backed iRODS sync (one-time, ~30 GB)
fractal-rag ingest --source all
```

**Reaching the MCP server depends on the tool:**

- **Claude Code** picks up `.mcp.json` automatically (`fractal-rag serve` over stdio); the
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
- HashRouter for GitHub Pages compatibility.
- Pages by category: `pages/fractals-1d-2d-3d/`, `pages/branching-architectures/`, `pages/riemann-zeta-functions/`.
- `components/{controls,layout,math}/`; `utils/` holds WebGL Mandelbrot/Julia, noise generators, theming.
- ThemeContext (light/dark/system, persisted to localStorage, MUI-integrated). Viz: D3, Plotly, KaTeX.

### Streamlit (`apps/`)
- Each `.py` is self-contained and independently runnable. NumPy, Matplotlib, Plotly, SciPy, Numba. Runtime GIFs/images stay local.

### Documentation (`docs/`)
- MkDocs Material, custom `fractals` palette, `mkdocs-jupyter` embeds, MathJax.
- Structured per `PLAN.md`: Part I Foundations (tutorial), then research chapters (biological-geometry, metabolic-scaling, spectral-geometry, hypotheses).

### Kubernetes (`k3s-deployment/`)
- JupyterLab + Weaviate with persistent storage, NVIDIA device plugin, local-path storage class.

## CI/CD

GitHub Actions deploys MkDocs (root) and React/Vite (`/react`) to GitHub Pages on push
to `main`. PR checks run React type-check + lint and an MkDocs build test.

> **Housekeeping:** `.github/workflows/` currently has one active deploy workflow
> (`deploy-all.yaml`) plus three `.disabled` files (`deploy.yml`, `mkdocs.yaml`,
> `react-deploy.yaml`) and `test-build.yaml`. Delete the superseded `.disabled`
> workflows or document why they are retained — see `SPECIALIST_READINESS.md`.

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
- **Python (RAG):** weaviate-client, MCP SDK, corpus/notebook/markdown/pdf parsers (`.[parsers]`).

## Roadmap — OKF + Zensical

The project's stated goal is to publish this work as agent-consumable knowledge.

1. **OKF bundle.** Represent the concept ontology (and, over time, datasets/notebooks)
   as an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog)
   bundle — a directory of Markdown files, one concept per file, each with YAML
   frontmatter (`type` is the only required field; `title`/`description`/`tags`/`timestamp`
   are optional). The 31 entries in `concepts/seed.yaml` (name, aliases, definition,
   domain) already map onto OKF concepts; cross-link them with normal Markdown links and
   add `index.md` (progressive disclosure) + `log.md` (change history) per level. OKF
   *complements* the MCP server — the server can expose the bundle as a knowledge source.
2. **Zensical migration.** Material for MkDocs is in maintenance mode; Zensical is its
   successor and reads the existing `mkdocs.yml` natively. Plan a migration
   (`zensical serve` / `zensical build`) once feature parity covers the plugins this site
   uses (`mkdocs-jupyter`, MathJax, PDF export). Track the parity gap before switching CI.

See `SPECIALIST_READINESS.md` for the concrete tightening checklist.
