# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

It is also read by **Claude Science** and any agent that honors the `CLAUDE.md` /
`AGENTS.md` convention (`AGENTS.md` is a symlink to this file). Keep it tool-agnostic
where possible and mark tool-specific behavior explicitly.

## Project Overview

Fractal Notebooks is a research + teaching platform on self-affine fractals and
metabolic scaling theory. Six components:

- **Zensical documentation site** (`docs/`, `zensical.toml`, `overrides/`, `scripts/`) — the
  "Fractal Self-Affinity in Nature" site at https://tyson-swetnam.github.io/fractal-notebooks,
  published to GitHub Pages. `docs/` is an **OKF v0.2 knowledge bundle**: every page carries OKF
  frontmatter, and the site also ships raw Markdown twins, `llms.txt` / `llms-full.txt` and
  per-page JSON-LD for AI agents.
- **React web applications** (`react/`) — TypeScript/React fractal visualizers deployed to `/react`.
- **Streamlit Python apps** (`apps/`) — 21 fractal-generator scripts (12 of them Streamlit apps,
  the rest matplotlib/PIL) on the scientific-Python stack.
- **Fractal RAG stack** (`fractal_rag/`) — Weaviate-backed retrieval + MCP server. Design spec:
  `specs/2026-05-23-fractal-rag-agent-design.md`.
- **OKF knowledge bundles** (`okf/`) — `okf/concepts/` (generated from the concept seed) and
  `okf/proofs/` (hand-authored proofs), both Open Knowledge Format v0.2, published through the
  site under `/okf/`.
- **Deployment** (`k3s-deployment/`, `docker/`) — K3s manifests as a kustomize base (Weaviate 1.35 +
  GPU embedding sidecar + device plugin) with an arm64 DGX Spark overlay, optional JupyterLab, a
  Streamlit Docker image, a local Docker Compose RAG stack, and a CUDA 13 arm64 build of the
  embedding sidecar (`docker/t2v-transformers-cuda-arm64/`).

Design specs live in `specs/` (moved out of `docs/`, redacted); the notebooks' historical
planning notes live in `notes/notebooks/`; `PLAN.md` is the completed restructuring plan.

## Environments

Prefer a pinned environment over ad-hoc `pip install`:

- `.venv` — the docs toolchain (Python 3.11): `uv venv --python 3.11 .venv && uv pip install
  --python .venv/bin/python -r requirements-docs.txt` gives Zensical 0.0.72 (pinned), nbconvert,
  nbformat, PyYAML and pathspec. Add `pytest` for `scripts/tests`. Every docs command below assumes
  `.venv/bin/python` / `.venv/bin/zensical`.
- `environments/fractal-foundations-gpu.yml` — GPU/CUDA stack for the foundations notebooks
  (fractal generators, dimension theory). Targets NVIDIA driver 535.x / CUDA 12.2.
- `environments/3dep-environment.yml` — geospatial / 3DEP terrain analysis.
- `fractal_rag/pyproject.toml` — the RAG package; install editable with `pip install -e ".[dev,parsers]"`
  (Python ≥ 3.10).
- `requirements.txt` — the legacy MkDocs toolchain, kept only as the rollback path until the cleanup
  phase. Do not extend it.

**Claude Science note:** create a dedicated conda env from the relevant `.yml` and pass
`environment=` on every code cell; do not install heavyweight stacks into the shared
default env. Prepare files in `python`, then reach the MCP server from the `repl` tool.

## Common Commands

### Documentation (Zensical)
```bash
uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python -r requirements-docs.txt
bash scripts/build_site.sh               # full pipeline into site/ (strict)
bash scripts/build_site.sh --with-react  # + npm ci/type-check/lint/build, copied into site/react/
bash scripts/build_site.sh --serve       # pipeline, then `zensical serve` with live reload (http://localhost:8000)
```
`build_site.sh` runs, in order: `okf_export --check` (concept bundle fresh) → `stage_okf.py`
(copy `okf/` into `docs/okf/`) → `render_notebooks.py --check` (rendered notebook pages fresh) →
`validate_okf.py` ×3 (`docs`, `okf/concepts`, `okf/proofs`) → `zensical build -f zensical.toml
--clean --strict` → `publish_sources.py` (raw `.md` twins into `site/`) → `generate_llms_txt.py
--strict` → [React] → `check_site.py` (live-URL coverage, links, leaks, size). Single steps:
```bash
.venv/bin/python scripts/render_notebooks.py                      # re-render notebook pages (rewrites only on change)
.venv/bin/python scripts/render_notebooks.py --only 1_history --strict
.venv/bin/python scripts/validate_okf.py docs --exclude 'okf/**'
.venv/bin/python scripts/validate_okf.py okf/concepts --profile concept
.venv/bin/python scripts/validate_okf.py okf/proofs --profile proof
.venv/bin/python scripts/check_site.py --emit-redirects           # redirect entries still missing for live URLs
.venv/bin/python -m pytest scripts/tests -q
.venv/bin/zensical serve                                          # from the repo root, after stage_okf.py + render_notebooks.py
```
`zensical build` alone neither stages `okf/` nor renders notebooks, so run the pipeline (or those
two scripts) first or the nav targets under `docs/okf/` are missing. A deleted or moved page needs a
redirect in `zensical.toml` in the same commit.

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
streamlit run apps/tree_roots_3d.py   # the 12 Streamlit apps are the apps/*.py files that `import streamlit`
python apps/mandelbrot.py             # the other 9 (mandelbrot, julia, branching_tree, ...) are matplotlib/PIL scripts
```

### Fractal RAG package
```bash
cd fractal_rag
pytest                                          # unit tests (tests/unit)
pytest tests/unit/test_chunk.py -k <name>       # single test
ruff check src tests && mypy src
fractal-rag concepts validate                   # check seed.yaml
fractal-rag okf export --out ../okf/concepts    # regenerate the OKF concept bundle (v0.2)
fractal-rag okf export --out ../okf/concepts --check   # drift check, what CI runs
fractal-rag status                              # collection counts
fractal-rag query "<text>"                      # ad-hoc hybrid search
```
The `integration` pytest marker (testcontainers Weaviate) is declared in `pyproject.toml`,
but no `tests/integration/` directory exists yet.

Re-index the docs after a content change (from an env with the package installed, at the repo root):
```bash
export FRACTAL_RAG_REPO_ROOT=$PWD   # repo_root defaults to /opt/tswetnam/github/fractal-notebooks
fractal-rag schema bootstrap --drop # UUIDs derive from paths and ingest never prunes, so drop first
fractal-rag ingest --source docs
fractal-rag ingest --source notebooks
fractal-rag status
```

### Docker
```bash
docker build -f docker/Dockerfile -t fractal-app . && docker run -p 8501:8501 fractal-app   # from the repo root
```

## Documentation architecture (`docs/`, `zensical.toml`)

Zensical (Material theme, `variant = "classic"`, custom light palette `fractals`) reads
`zensical.toml` at the repo root: site metadata, `nav`, `exclude_docs` / `not_in_nav`, theme,
Markdown extensions and the `redirects` map all live there, and `scripts/okf_common.py` reads the
same file so no script hard-codes site settings. `mkdocs.yml` is a frozen rollback copy.

| Tab | Landing | Pages |
|---|---|---|
| Home | `index.md` | — |
| Foundations | `foundations/index.md` | Chapters 1–4: `history`, `mathematics`, `dimensionality`, `glossary` |
| Research | `metabolic-scaling/index.md`, `spectral-geometry/index.md`, `biological-geometry/index.md`, `hypotheses/index.md` | Parts II–V, seven IMRaD sections each (Part V "Expected Results" = `results.md`) |
| Notebooks | `notebooks/index.md` | 15 rendered notebook pages under `notebooks/foundations/` and `notebooks/metabolic-scaling/{methods,results}/`, plus `notebooks/research.md` (GitHub / nbviewer links to the unpublished research notebooks) |
| Apps | `applications/index.md` | `installation`, `react-apps`, `streamlit-apps`, `dbc`, `tree-roots-3d`, `blender-dla`, external "Launch the React apps ↗" |
| Knowledge | `okf/index.md` | `okf/concepts/index.md`, `okf/proofs/index.md` + 12 proofs, `fractal-rag/` guides + 3 rendered notebooks |
| For AI Agents | `agents.md` | — |

Built but not in the nav (`not_in_nav`): `log.md`, the concept pages and group indexes under
`okf/concepts/*/`, and `okf/*/log.md`. Part and chapter numbers stay in titles; body H1s and anchor
slugs are never renumbered; no directory has been renamed, so pre-2026-10 nav URLs still resolve.

- **Rendered notebooks**: the `.ipynb` files stay under `docs/` but are excluded from the build;
  `scripts/render_notebooks.py` writes `<stem>.md` + `<stem>_files/` next to each published notebook
  (committed, drift-checked in CI). The pages keep the URLs mkdocs-jupyter gave them
  (`/notebooks/foundations/1_history/`).
- **OKF staging**: `docs/okf/concepts/` and `docs/okf/proofs/` are build-time copies of `okf/` made
  by `scripts/stage_okf.py` and are gitignored; `docs/okf/index.md` is hand-written and tracked.
- **Excluded from the site** (`exclude_docs`): `*.ipynb`, `*.py`, data files, every `README.md`, and
  the 3DEP / Sierra Nevada / Smithsonian / Part II review / Blender notebook directories. Internal
  notes moved to `notes/notebooks/` and specs to `specs/`: nothing under `docs/` is private.
- **Redirects**: every removed URL — legacy root pages, gh-pages-era flat notebook URLs, orphan
  notebook pages, `.py` pages, README indexes, notes/specs, moved anchors (~130 entries) — is in
  `[project.plugins.redirects.redirect_maps]`. Zensical writes `/old/index.html` stubs (canonical link,
  meta refresh, anchor-forwarding JS; destinations are relative); anchor keys on live pages go to
  `redirect.json` and are handled client-side. Stubs are not listed in `sitemap.xml`.
- **Theme files**: `overrides/main.html` (repo root; head injection, see "Agent-readable
  publishing"), `docs/stylesheets/extra.css` (palette; hides the `stable` status badge),
  `docs/javascripts/mathjax.js` (MathJax 3 + instant-navigation re-typeset + annotation hook). Math
  uses `pymdownx.arithmatex` generic mode (`$…$`, `\(…\)`, `$$`, `\[…\]`); icons use `pymdownx.emoji`
  with the `zensical.extensions.emoji` index/generator.

## OKF frontmatter (required on every `docs/` page)

`docs/` is an [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
bundle. Every Markdown page carries YAML frontmatter in this exact key order
(`okf_version: "0.2"` first on `docs/index.md` only):

```yaml
---
type: Chapter                 # docs taxonomy: Index, Chapter, Paper Section, Notebook, Guide, Reference, Log
title: "Chapter 1: History of Fractal Mathematics"   # disambiguates pages sharing an H1; nav labels stay short
description: >-               # plain text, 50-300 chars, specific to THIS page; no double quotes, no < or >,
  One or two concrete sentences about the page.      # no markdown; use >- so a ": " cannot break the YAML
resource: https://tyson-swetnam.github.io/fractal-notebooks/foundations/history/   # canonical URL (X/index.md -> .../X/)
tags: [foundations, part-i, geometry]                # 2-6 from the vocabulary below
paper:                        # Paper Section pages (Parts II-V) only
  title: "Fractal Patterns in Nature: Self-Affinity vs Self-Similarity"
  part_title: "Part II: Metabolic Scaling"
  landing: https://tyson-swetnam.github.io/fractal-notebooks/metabolic-scaling/
  stage: manuscript
authors:                      # Part II only (the only Part that names authors): name, ORCID URL, affiliation
  - name: Tyson L. Swetnam
    orcid: https://orcid.org/0000-0002-6639-7181
    affiliation: University of Arizona
citation: {}                  # Part II only: the BibTeX fields from docs/index.md
companion_page: https://tyson-swetnam.github.io/fractal-notebooks/foundations/history/   # Notebook pages
notebook: {}                  # Notebook pages (generated): source, raw, nbviewer, colab, kernel, environment, cells, outputs
sources:                      # 2-8 load-bearing external references actually cited in the body; omit if none
  - id: mandelbrot1982
    resource: https://doi.org/10.1119/1.13295
    title: The Fractal Geometry of Nature
generated:
  by: human:tswetnam          # actors: human:tswetnam, process:scripts/render_notebooks.py, process:fractal-rag-okf-export
  at: "2025-12-14T00:00:00Z"  # quoted ISO-8601; authored pages use the first-commit date (git log --diff-filter=A --follow)
verified:                     # optional and HUMAN-ONLY: added by a person who re-read the page; automation and
  - by: human:tswetnam        # agents never add, copy or refresh verified entries
    at: "2026-10-24T00:00:00Z"
status: stable                # stable | draft (Part II-V paper pages are draft); optional stale_after: "<ISO date>"
---
```

Tag vocabulary (kept in `scripts/validate_okf.py`, the source of truth):

- kind: `foundations research paper notebook app knowledge agents reference tutorial`
- part: `part-i part-ii part-iii part-iv part-v`
- math: `geometry foundations dimension-theory measure-theory methods image-analysis complex-dynamics
  classics 3d-fractals ifs biological branching generative stochastic hurst signal-processing texture
  number-theory complex-analysis advanced statistics scaling dynamics statistical-physics topology`
- science: `self-affinity self-similarity metabolic-scaling allometry spectral-geometry riemann-zeta
  complex-dimensions dla lidar canopy-height-model 3dep forest-ecology preregistration`
- tooling: `jupyter react streamlit blender cuda rag weaviate mcp okf llms-txt`

Conventions:

- Run `.venv/bin/python scripts/validate_okf.py docs --exclude 'okf/**'` before committing; CI
  enforces it, and `resource` must equal the page's canonical URL.
- The exchange bundles stay spec-pure: `okf/concepts/index.md` and `okf/proofs/index.md` carry only
  `okf_version: "0.2"`; group `index.md` files and both `log.md` files have no frontmatter. Concepts
  are `type: Fractal Concept`, proofs `type: Fractal Proof` (+ `result`, `concept`,
  `historical_source`, `verification_status`). `docs/` landings and `docs/log.md` do carry frontmatter.
- `docs/log.md` (`type: Log`) is the OKF change log: newest-first `## YYYY-MM-DD` headings with
  **Creation** / **Update** / **Deprecation** bullets; add an entry for every new, moved or removed page.
- New page checklist: frontmatter → `nav` entry in `zensical.toml` (or a `not_in_nav` pattern) →
  `docs/log.md` entry → a redirect if it replaces a URL.

## Recipes

**Publishing a notebook.** Add a `[[notebook]]` entry to `scripts/notebooks.toml` (`src`, an
explicit `title`, `description`, `tags`, `companion_page`, `environment`, `as_of` date →
`generated.at`, `status`, `code_only = true` for notebooks without stored outputs), add the rendered
`.md` path to `nav` in `zensical.toml`, run `.venv/bin/python scripts/render_notebooks.py`, and
commit the generated `<stem>.md` + `<stem>_files/`. The renderer never executes notebooks: it renders
the stored outputs (PNG preferred over Plotly/HTML, widget views become a note, stderr dropped,
machine paths scrubbed, long streams truncated) and is deterministic, so `--check` in CI catches
drift. Re-run it after editing a published `.ipynb`.

**Editing a concept.** Edit `fractal_rag/src/fractal_rag/concepts/seed.yaml`, run `fractal-rag okf
export --out okf/concepts` (from `fractal_rag/`: `--out ../okf/concepts`), and commit the regenerated
`okf/concepts/**`. Never hand-edit the bundle (CI runs `--check`); `log.md` is append-only (one dated
**Creation** / **Update** / **Deletion** section per run).

**Adding a proof.** Write `okf/proofs/<slug>.md` (`type: Fractal Proof`; every step tagged
`[verified]` — checked with SymPy/NumPy, reproducibly — or `[asserted]` — rests on a cited named
theorem; `verification_status` is `verified` | `partially-verified` | `unverified`), add a line to
`okf/proofs/index.md`, an entry to `okf/proofs/log.md`, and the page to the "OKF Proofs" nav section.

## Agent-readable publishing

Beyond the rendered HTML, the build publishes:

- **Markdown twins**: the raw source of every page, verbatim, at `site_url + <source path>`
  (`/foundations/history/` ↔ `/foundations/history.md`; directory pages append `index.md`:
  `/metabolic-scaling/` ↔ `/metabolic-scaling/index.md`, home ↔ `/index.md`; `okf/**` twins come
  from the pristine `okf/` tree). `scripts/publish_sources.py` copies them (`--verify` asserts every
  emitted twin href resolves); each page's `<link rel="alternate" type="text/markdown">` gives the
  exact URL. GitHub Pages serves them as `text/markdown`.
- **`llms.txt` + `llms-full.txt`** from nav + frontmatter (`scripts/generate_llms_txt.py`): one H2
  per tab/section, Knowledge sections for the 46 concept pages and 13 proof pages, the 16 React
  routes (which share one crawlable URL), and `Related OKF bundle:` lines from `[project.extra]
  related_llms` in `zensical.toml`.
- **Per-page JSON-LD, OpenGraph and `okf:*` metas** injected by `overrides/main.html`:
  `ScholarlyArticle` (Paper Section, with the `authors` list) / `LearningResource` (Chapter, Notebook,
  Guide) / `CreativeWork` otherwise. The template is MiniJinja with autoescape OFF: `| e` on
  author-supplied attributes, `| tojson` on JSON-LD scalars, no Python calls, every `page.meta.*`
  guarded. It also hides the edit/view buttons on Notebook, Fractal Concept and Fractal Proof pages
  (no editable source under `docs/` on GitHub).
- **`docs/robots.txt`** is informational: this is a GitHub Pages *project* site, so crawlers read the
  host-root `https://tyson-swetnam.github.io/robots.txt` (repo `tyson-swetnam/tyson-swetnam.github.io`),
  which is where the sitemap and agent entry points must be registered (see follow-ups).
- `docs/agents.md` ("For AI Agents") documents all of the above for readers; update it whenever an
  endpoint or convention changes.

## The Fractal RAG knowledge stack

`fractal_rag/` builds a Weaviate index over four content types — Constellate
scholarly-article exports (`json`), Jupyter notebooks (`notebooks`), the site's Markdown
pages (`docs`), and reference PDFs (`pdfs`) — these are the `--source` values for
`fractal-rag ingest`. It also keeps a hand-curated `Concept` side-collection (32 seeded
canonical concepts in `fractal_rag/src/fractal_rag/concepts/seed.yaml`, the same seed that
generates `okf/concepts/`) and exposes eight retrieval tools over an MCP server. The stack is
**read-only by design** — it retrieves and synthesizes, it does not mutate the corpus.

The `docs` source honours the site layout: it parses and strips OKF frontmatter (title from
`title`, metadata gains `okf_type`, `description`, `tags`, `status`, `resource`), and skips dot-dirs,
`*_files/`, the staged `docs/okf/**` copies, everything matched by `exclude_docs` / `draft_docs` in
`zensical.toml`, and rendered notebook pages whose sibling `.ipynb` exists (the `notebooks` source
indexes those, scanning `docs/**/*.ipynb` as well as the iRODS mirror).

Configuration is via `FRACTAL_RAG_*` env vars (`fractal_rag/src/fractal_rag/config.py`).
Defaults point Weaviate at the K3s NodePorts (`localhost:30080` HTTP / `30051` gRPC) and
`repo_root` at `/opt/tswetnam/github/fractal-notebooks`; set `FRACTAL_RAG_REPO_ROOT=$PWD` on any
other host (or put it in a gitignored `.env` at the repo root, read when the CLI runs from there),
otherwise `ingest --source docs` silently indexes nothing.

Bring it up — either on K3s:
```bash
kubectl apply -k k3s-deployment/base                 # Weaviate 1.35 + arctic-embed GPU sidecar (x86 node)
kubectl apply -k k3s-deployment/overlays/dgx-spark   # arm64 DGX Spark: sidecar built by docker/t2v-transformers-cuda-arm64/build.sh
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
tool-selection rubric. Cite `metadata.resource` (the public page URL) when present, not the
`file://` source URI.

## OKF bundles (`okf/`)

Both bundles are OKF **v0.2** and are published through the site at `/okf/concepts/` and
`/okf/proofs/` (build-time copies under `docs/okf/`, gitignored; raw twins served from the pristine tree).

- **`okf/concepts/`** is **generated** from `concepts/seed.yaml` by `fractal-rag okf export`
  (`fractal_rag/src/fractal_rag/okf_export.py`). Never hand-edit it: edit the seed and re-export.
  32 concepts in 12 folders grouped by first domain tag, each folder with an `index.md`; the root
  `index.md` carries only `okf_version: "0.2"`; `log.md` is append-only. Links are relative
  (`slug.md`, `../<group>/<slug>.md`) so they resolve on GitHub, on the site and as raw twins.
- **`okf/proofs/`** is **hand-authored**: `type: Fractal Proof` documents backing the quantitative
  claims in `docs/foundations/history.md`, with `[verified]` / `[asserted]` step tags,
  `verification_status`, and the v0.2 keys (`resource`, `sources`, `generated`, `verified`,
  `status`). See "Adding a proof" above.
- `scripts/validate_okf.py --profile concept|proof` validates each bundle; `scripts/stage_okf.py`
  copies them into `docs/okf/` for the build.

## Agents & Specialists

This repo ships three Claude Code subagents in `.claude/agents/`:

- **`fractal-explorer`** — a citation-grounded retrieval/synthesis agent over the RAG corpus
  (explicit `tools:` allowlist = the eight MCP tools + read-only file access).
- **`jupyter-notebook-engineer`** and **`dla-fractal-gpu`** — notebook authoring/debugging and
  DLA / L-system / CUDA specialists (moved here from `docs/notebooks/**/.claude/`, where they were
  inert).

- **Claude Code:** each is a Markdown file with YAML frontmatter + system prompt.
- **Claude Science:** the same roles should be registered as **Specialist** agent profiles via
  `host.agents.create(...)` (load the `customize` skill for the API). A Specialist captures the
  role's instructions + vocabulary and can be restricted to a connector/skill subset — for
  `fractal-explorer`, the `mcp-fractal-rag` tools plus read-only file access. The frontmatter
  `description`, system prompt, and tool list port over directly. Keep the two definitions in
  sync; treat the Markdown file as the source of truth for the prompt text.

When adding a new role, write the Claude Code subagent first (it version-controls
cleanly), then mirror it as a Specialist profile.

## Architecture

### React (`react/src/`)
- HashRouter for GitHub Pages; Vite `base` is `/fractal-notebooks/react/`. All 16 routes share one
  crawlable URL, so the docs page `applications/react-apps.md` is the agent-readable description.
- Adding a page takes two edits: import + `<Route>` in `App.tsx`, and an entry in the
  nav config in `components/layout/Navigation.tsx`. Pages live under
  `pages/{fractals-1d-2d-3d,branching-architectures,riemann-zeta-functions}/`. Also add the route
  to the table in `docs/applications/react-apps.md` (`generate_llms_txt.py` lists the routes).
- `components/controls/` is the shared UI kit (`AppScaffold`, `ControlSection`,
  `ParameterSlider`, `ParameterSelect`, `ActionBar`, `CollapsiblePanel`); build new
  pages on it rather than ad-hoc MUI layouts.
- `utils/` holds the compute engines: WebGL Mandelbrot/Julia, noise generators,
  L-system / plant engine + presets, and MUI themes.
- ThemeContext (light/dark/system, persisted to localStorage, MUI-integrated). Viz: D3, Plotly, KaTeX.

### Streamlit (`apps/`)
- Each `.py` is self-contained and independently runnable. NumPy, Matplotlib, Plotly, SciPy.
  Runtime GIFs/images stay local.

### Kubernetes (`k3s-deployment/`)
- `base/` is a kustomize base (namespace, `nvidia` RuntimeClass, device plugin, Weaviate, sidecar);
  `overlays/dgx-spark/` swaps in the locally built CUDA arm64 sidecar image. JupyterLab manifests
  stay at the top level and are optional. Persistent storage uses K3s's `local-path` class.

## CI/CD

- `.github/workflows/deploy-all.yaml` (push to `main`): checkout with `fetch-depth: 0`, Python 3.11
  + `requirements-docs.txt`, Node 20, `bash scripts/build_site.sh --with-react --ci` (the script
  copies `react/build/` into `site/react/`; HashRouter needs no `404.html` fallback or `/react-apps/`
  hack — that URL is a redirect stub now), then `configure-pages` → `upload-pages-artifact`
  (`site/`) → `deploy-pages`. A `verify` job runs `scripts/smoke_live.sh` against the live site.
- `.github/workflows/test-build.yaml` (PRs): `docs` (same pipeline + `pytest scripts/tests` +
  site artifact), `fractal-rag` (`pip install -e fractal_rag[dev,parsers]`, `ruff check`,
  `pytest fractal_rag/tests/unit`), `test-react` (build, type-check, lint), and `test-mkdocs`
  (`continue-on-error: true` rollback canary until the cleanup phase).
- Generated files are drift-checked, not rebuilt, in CI: `okf/concepts/**` (`okf_export --check`)
  and the rendered notebook pages (`render_notebooks.py --check`). If CI fails there, regenerate
  locally and commit the result.

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
- **Python (docs):** zensical 0.0.72 (pinned in `requirements-docs.txt`), nbconvert 7, nbformat,
  PyYAML, pathspec; MathJax 3 from the unpkg CDN; Google Fonts (EB Garamond, Courier Prime).
- **Python (apps):** streamlit, numpy, matplotlib, plotly, scipy, pillow, imageio.
- **Python (RAG):** weaviate-client v4, MCP SDK, click, pydantic-settings, nbformat, mistune,
  pdfminer.six (`.[parsers]`).

## Deferred follow-ups (after one clean release)

- **Cleanup:** remove `mkdocs.yml`, `requirements.txt`, the `test-mkdocs` canary and
  `scripts/compare_builds.py`; drop the TEMPORARY legacy excludes in `zensical.toml`; refresh
  `okf/README.md` (v0.2, both bundles, truthful validation statement).
- **User-site PR** to `tyson-swetnam/tyson-swetnam.github.io`: root `robots.txt` sitemap line and an
  "AI agents and harnesses: Fractal Notebooks" block (llms.txt, llms-full.txt, twin rule incl.
  `index.md` for directory pages, OKF bundle roots, agent guide, React is HashRouter/JS-only),
  rewritten `okf/sites/fractal-notebooks.md`, an `okf/log.md` **Update** bullet. Open it only after
  every URL in it resolves live.
- **Optional:** delete the stale `origin/gh-pages` branch (Pages deploys from Actions); bump
  Zensical to the 0.1.x line in its own PR; richer JSON-LD types (`DefinedTerm` for concepts,
  `Article` for proofs); React → docs backlink and `react/index.html` favicon/manifest/MathJax
  cleanup; publish `docs/notebooks/3dep/README.md` as a page; define `environments/fractal-proof.yml`
  (cited by `okf/proofs/log.md`); notebook re-execution fixes (`1_history` cell 8 `ValueError`,
  `ferns`, `dbc` `input()`, `zeta_3d` CUDA).
