# Spec — Zensical Migration & OKF Publishing (v1)

- **Date:** 2026-07-13
- **Status:** Draft — for review
- **Author:** Tyson Swetnam (tswetnam@arizona.edu) with Claude Science
- **Related specs:**
  - `2026-05-23-fractal-rag-agent-design.md` (Fractal RAG Stack)
- **Related docs:** `../../../SPECIALIST_READINESS.md`, `../../../okf/README.md`

---

## 1. Overview

Two coupled moves that make Fractal Notebooks agent-consumable and future-proof its
documentation toolchain:

1. **Publish the concept ontology as an OKF bundle** (`okf/concepts/`) — done in v1 as a
   generator (`fractal-rag okf export`); this spec covers wiring it into the site and CI.
2. **Migrate the documentation site from MkDocs (Material) to Zensical** — the successor
   built by the Material for MkDocs team. Material for MkDocs is now in maintenance mode;
   Zensical reads the existing `mkdocs.yml` natively, so migration is incremental rather
   than a rewrite.

This spec defines a **parallel-build** migration: Zensical runs alongside the current
MkDocs build in CI (non-blocking) until feature parity is confirmed for the plugins this
site depends on, then becomes the primary builder.

## 2. Goals and success criteria

### Goals

- Keep the live MkDocs GitHub Pages deploy working throughout — zero downtime.
- Stand up a `zensical build` path that renders the same `docs/` tree.
- Verify parity for the site's plugin-dependent features (notebooks, math, PDF export,
  git-revision dates) before switching.
- Surface the OKF bundle from the docs site so humans and agents can browse it.
- Leave a clean rollback: reverting to MkDocs is a one-line CI change until cutover.

### Done = all of:

1. `zensical build` produces a site from `docs/` with no fatal errors.
2. A non-blocking `zensical-build` CI job runs on PRs and uploads its output as an artifact
   for visual diffing against the MkDocs build.
3. The parity checklist (§6) is fully assessed against the live Zensical compatibility
   matrix, with each item marked supported / workaround / blocker.
4. The OKF bundle is reachable from the published site (linked from a docs page).
5. A cutover decision is recorded (go / no-go) with the parity gaps that drove it.

### Non-goals (v1)

- Rewriting page content or restructuring `docs/` (that is `PLAN.md`'s scope).
- Migrating the React app build (unaffected — it deploys to `/react` independently).
- Dropping MkDocs before parity is confirmed.

## 3. Background

- **Material for MkDocs → maintenance mode.** The maintainers announced Zensical
  (2025-11-05) as the go-forward static site generator. New feature work moves to Zensical.
- **Zensical reads `mkdocs.yml`.** Existing navigation, theme palette, and much of the
  configuration are consumed directly, which is why this is a migration and not a rebuild.
- **Plugin surface is the risk.** MkDocs' plugin ecosystem is large; Zensical does not (yet)
  cover all of it. The features this repo actually depends on must each be checked against
  the **live** compatibility matrix at <https://zensical.org/compatibility/> at migration
  time — do not rely on a snapshot, as coverage is expanding.

## 4. Current site inventory (what must keep working)

From `mkdocs.yml` and `requirements.txt`, the site depends on:

| Feature | Provided by (MkDocs) | Why it matters |
|---|---|---|
| Material theme + `fractals` palette | `mkdocs-material` | Site look; Zensical is the Material team's own successor. |
| Embedded Jupyter notebooks | `mkdocs-jupyter` | Foundations notebooks render as pages. **Highest-risk dependency.** |
| LaTeX math | MathJax (via `pymdown-extensions`) | Equations across every math page. |
| PDF export | `mkdocs-pdf-export-plugin` + `weasyprint` | Downloadable paper PDFs. |
| Git revision dates | `mkdocs-git-revision-date-plugin` | "Last updated" stamps. |
| API docs | `mkdocstrings` (+ python-legacy) | Any autodoc pages. |
| Admonitions, tabs, superfences | `pymdown-extensions` | Structural markdown used throughout. |

## 5. Migration approach — parallel build

1. **Add Zensical as a dev dependency** (isolated; do not remove MkDocs).
   ```bash
   pip install zensical          # into a docs env, alongside mkdocs-material
   zensical build                # reads mkdocs.yml, emits to its default site dir
   zensical serve                # local preview
   ```
2. **Run both builders in CI.** Extend `.github/workflows/test-build.yaml` with a
   `zensical-build` job that runs on PRs, is `continue-on-error: true`, and uploads its
   output as an artifact. This tracks parity every PR without gating merges or touching the
   live deploy (`deploy-all.yaml` stays on MkDocs).
3. **Assess parity** (§6) against the live compatibility matrix; record each feature's state.
4. **Close gaps** with Zensical-native equivalents or documented workarounds; for any hard
   blocker (e.g. a notebook-embedding gap), decide whether to pre-render or defer cutover.
5. **Cutover** only when parity is green: point `deploy-all.yaml`'s docs step at
   `zensical build`, keep the MkDocs job available for one release as rollback, then remove.

## 6. Parity checklist (assess against the live matrix at cutover time)

- [ ] Material theme + custom `fractals` color palette render correctly.
- [ ] Navigation tree from `mkdocs.yml` is honored (Parts I–…, notebook entries).
- [ ] **`mkdocs-jupyter` notebook embedding** — supported natively, needs pre-render, or blocker?
- [ ] MathJax / LaTeX equations render on math-heavy pages.
- [ ] PDF export path (or an accepted alternative) works.
- [ ] Git revision "last updated" dates present (or dropped by decision).
- [ ] `pymdown-extensions` features (admonitions, tabs, superfences, arithmatex) render.
- [ ] `mkdocstrings` autodoc pages render (if any are in use).
- [ ] Search works and indexes all pages.
- [ ] Internal links and `use_directory_urls` behavior match the MkDocs output.

## 7. OKF publishing integration

- Add a docs page (e.g. `docs/fractal-rag/knowledge-bundle.md`) that links to the OKF
  bundle and explains the seed-as-source-of-truth model (see `okf/README.md`).
- Add `fractal-rag okf export` to the docs build so the bundle is regenerated from
  `concepts/seed.yaml` on every build — never hand-edited, never stale.
- Optionally expose the bundle as an additional knowledge source to the RAG ingest so the
  Weaviate `Concept` collection and the Markdown bundle share one ontology.

## 8. Risks & mitigations

| Risk | Mitigation |
|---|---|
| `mkdocs-jupyter` unsupported in Zensical | Pre-render notebooks to HTML/Markdown as a build step, or defer cutover until supported. |
| PDF export plugin gap | Keep MkDocs job solely for PDF artifacts during transition, or switch to a Zensical-native/CI-side PDF step. |
| Compatibility matrix changes under us | Re-check <https://zensical.org/compatibility/> at cutover; treat §6 as a point-in-time assessment. |
| Regression on live site | Parallel non-blocking build + one-release MkDocs rollback window. |

## 9. Rollout steps (ordered)

1. Land the OKF generator + bundle (**done** in the current change).
2. Add the non-blocking `zensical-build` CI job.
3. Fill in §6 against the live matrix; open issues for each gap.
4. Resolve/triage gaps; add the OKF docs page + export step to the build.
5. Go/no-go review; on go, switch `deploy-all.yaml` and keep MkDocs as rollback.
6. After one clean release, remove the MkDocs build path and stale dependencies.

## 10. Citations

[1] [Zensical — A modern static site generator (Material for MkDocs team)](https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/)
[2] [Zensical compatibility matrix](https://zensical.org/compatibility/)
[3] [Zensical source repository](https://github.com/zensical/zensical)
[4] [Open Knowledge Format specification (v0.1)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
