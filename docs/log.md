---
type: Log
title: Change Log
description: >-
  Dated history of notable changes to the Fractal Self-Affinity in Nature site:
  the 2026-10-24 Zensical rebuild with OKF v0.2 publishing and agent endpoints,
  the 2026-07-13 knowledge bundles, and the 2025-12-14 seven-part restructure.
resource: https://tyson-swetnam.github.io/fractal-notebooks/log/
tags: [reference, okf, knowledge]
generated:
  by: claude-code/claude-fable-5-1
  at: "2026-10-24T00:00:00Z"
status: stable
---

# Log

Newest first. Bullets are tagged **Creation**, **Update** or **Deprecation**, following the
[OKF v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md){target=_blank}
reserved-file convention. The two knowledge bundles keep their own logs:
[concepts](okf/concepts/log.md) and [proofs](okf/proofs/log.md).

## 2026-10-25

- **Update**: Fractal RAG guides: `FRACTAL_RAG_REPO_ROOT` is documented in [Local Setup](fractal-rag/local-setup.md), [Hosted VM](fractal-rag/hosted-vm.md) and [Troubleshooting](fractal-rag/troubleshooting.md). The `docs` and `notebooks` sources index `<repo_root>/docs/` and silently index nothing when the default checkout path does not exist; the `.env` recipe gained the variable and the gRPC port, and the Local Setup counts reflect the 2026-10-25 rebuild.
- **Update**: [Hosted VM (K3s)](fractal-rag/hosted-vm.md) and [Troubleshooting](fractal-rag/troubleshooting.md) carry the measured 2026-10-25 ingest on the DGX Spark: 104,061 artifacts (512 docs, 3,537 notebook and 100,012 json chunks for the 50,000 Constellate records), about two hours for the json source with two sidecar replicas, and the fact that the batch settings are not used by the ingest loop. The json parser now keys records on the Constellate `id` instead of the DOI: 1,125 records shared a DOI with an earlier record and overwrote it in the first index (97,762 json objects for 100,012 inserted chunks). Troubleshooting documents the symptom and the delete-and-re-ingest fix, and Constellate hits now carry the `https://doi.org/` link (or the record's JSTOR page) as `resource` for the [fractal-explorer agent](fractal-rag/using-the-agent.md) to cite.
- **Update**: [Hosted VM (K3s)](fractal-rag/hosted-vm.md) rewritten for the current deployment: the manifests are a kustomize base (`kubectl apply -k k3s-deployment/base`) with a DGX Spark (arm64) overlay, the embedding sidecar runs from a CUDA 13 arm64 image built by `docker/t2v-transformers-cuda-arm64/build.sh`, the NVIDIA device plugin moved to v0.20.1 with GPU time slicing, and a new "DGX Spark (arm64) notes" section records the platform findings. The iRODS corpus path is now `/iplant/home/tswetnam/projects/fractal-notebooks/` in the [overview](fractal-rag/index.md), [Troubleshooting](fractal-rag/troubleshooting.md) and the CLI default.

## 2026-10-24

- **Creation**: [For AI Agents](agents.md) — guide to the machine-readable endpoints (llms.txt, Markdown twins, OKF bundle roots) and to reading the frontmatter trust signals.
- **Creation**: [Change Log](log.md) — this page.
- **Creation**: [Knowledge Bundles](okf/index.md) — overview of the concept and proof bundles published through the site, how they are produced and how to consume them.
- **Creation**: [Notebooks](notebooks/index.md) — how notebooks are published, the environments that run them, and the catalogue of the 18 rendered notebook pages.
- **Creation**: [Research Notebooks](notebooks/research.md) — catalogue of the 73 unpublished research notebooks (3DEP canopy height models, Barro Colorado Island, Sierra Nevada, Part II reviewer companions, metabolic scaling tutorials, GPU and Blender DLA work, work in progress) with GitHub and nbviewer links.
- **Creation**: [Foundations](foundations/index.md) — Part I landing page.
- **Creation**: Research landing pages for [Part II: Metabolic Scaling](metabolic-scaling/index.md), [Part III: Spectral Geometry](spectral-geometry/index.md), [Part IV: Biological Geometry](biological-geometry/index.md) and [Part V: Research Hypotheses](hypotheses/index.md); the Part II landing takes over the manuscript table of contents and the author block from the Abstract.
- **Update**: Site rebuilt with Zensical in place of Material for MkDocs: `zensical.toml` replaces `mkdocs.yml`, the build runs strict, and the home-page icons, favicon and fonts now render.
- **Update**: Navigation regrouped into Home, Foundations, Research, Notebooks, Apps, Knowledge and For AI Agents. Part and chapter numbers stay in titles; no directory was renamed, so every previous navigation URL still resolves.
- **Update**: The concept ontology (32 concepts in 12 groups) and the 12 proofs are published as OKF bundles under `/okf/` and upgraded from OKF v0.1 to v0.2; every page in `docs/` now carries OKF v0.2 frontmatter (type, description, resource, tags, sources, generated, status).
- **Update**: Notebooks are pre-rendered from their stored outputs into committed Markdown pages: Part I chapters 1 to 4, Part II methods 1 to 4 and results 1 to 3, the `dla`, `fractals`, `fractal_generators` and `zeta_space` demonstrations, and the Fractal RAG examples 01 to 03 (code-only). `fractals` and `4_zeta_space` were executed to regenerate their figures; `zeta_space` is widget-only and published as a draft.
- **Update**: Agent surface added: `llms.txt`, `llms-full.txt`, `robots.txt`, a verbatim Markdown twin for every page, and `rel="alternate"` links plus JSON-LD in every page head.
- **Update**: Content salvaged from the retired legacy pages: the Barnsley fern IFS maps and a Differential Box-Counting entry into [Glossary and Equations](foundations/glossary.md); the signal and 2D-application material into [Fractal Dimensionality](foundations/dimensionality.md); the per-app deep links and app details into [React Apps](applications/react-apps.md).
- **Deprecation**: Fourteen legacy single-paper pages at the site root were removed; their URLs redirect: `/introduction/`, `/methods/`, `/results/`, `/discussion/`, `/conclusion/` and `/references/` to the matching Part II pages; `/glossary/` to Glossary and Equations; `/dims/` to Fractal Dimensionality; `/installation/`, `/dbc/`, `/tree_roots/` and `/react-apps/` to the Apps pages Installation, Box-Counting Tool, 3D Visualization and React Apps; `/dla/` to the DLA notebook; `/applications/` is now served by the Apps overview.
- **Deprecation**: The chatbot widget (`chatbot_widget.js`, `chatbot_widget.css`, the robot icon and the unused `overrides/` templates) was removed from every page.
- **Deprecation**: Internal planning notes and design specs were moved out of the site into the repository's `notes/` and `specs/` directories (the specs redacted); orphan notebook pages, helper-script pages and README directory indexes are no longer built. Every former URL redirects to the matching section of [Research Notebooks](notebooks/research.md), to the Fractal RAG overview, or to the file on GitHub.

## 2026-07-13

- **Creation**: OKF knowledge bundles: `okf/proofs` (12 hand-written proofs backing the quantitative claims of Chapter 1, commit `08c1e2e`) and `okf/concepts` (generated from the Fractal RAG concept seed by `fractal-rag okf export`, commit `3080fb1`); the Zensical migration spec was drafted the same day.

## 2025-12-14

- **Update**: Site restructured into seven parts (Foundations, Metabolic Scaling, Spectral Geometry, Biological Geometry, Research Hypotheses, Interactive Applications, Notebooks) with a new landing page (commit `3c34f41`).
