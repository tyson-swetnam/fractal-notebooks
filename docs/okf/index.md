---
type: Index
title: Knowledge Bundles
description: >-
  The two Open Knowledge Format v0.2 bundles published with this site: 32
  generated fractal concepts in 12 groups and 12 hand-written proofs with
  machine-checked step tags, with how to read them, how they are produced, and
  how the Fractal RAG stack indexes the same ontology.
resource: https://tyson-swetnam.github.io/fractal-notebooks/okf/
tags: [knowledge, okf, agents, rag]
sources:
  - id: okf-spec
    resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
    title: Open Knowledge Format (OKF) v0.2 specification
generated:
  by: claude-code/claude-fable-5-1
  at: "2026-10-24T00:00:00Z"
status: stable
---

# Knowledge Bundles

The [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md){target=_blank}
is a convention for publishing knowledge as a directory of Markdown files with YAML
frontmatter: one record per file, an `index.md` at every level for progressive disclosure,
a `log.md` for change history, and an `okf_version` declaration at the bundle root. A bundle
needs no tooling to read: a person browses it, an agent fetches it, `git` diffs it.

This site publishes two such bundles alongside the documentation, which is itself an OKF
v0.2 bundle (see [For AI Agents](../agents.md)).

## The two bundles

| Bundle | Records | Produced by | Browse | Raw root |
|---|---|---|---|---|
| **Concepts** | 32 `Fractal Concept` records in 12 groups | Generated from the Fractal RAG concept seed | [concepts/index.md](concepts/index.md) | [`/okf/concepts/index.md`](https://tyson-swetnam.github.io/fractal-notebooks/okf/concepts/index.md) |
| **Proofs** | 12 `Fractal Proof` records | Hand-written, machine-checked where possible | [proofs/index.md](proofs/index.md) | [`/okf/proofs/index.md`](https://tyson-swetnam.github.io/fractal-notebooks/okf/proofs/index.md) |

### Concepts

The concept bundle is the glossary of this site as a typed ontology. Each record carries
`type: Fractal Concept`, a one-paragraph definition, `aliases`, domain `tags`, an optional
`hausdorff_dim_range`, and relative links to related concepts. The 12 groups are the first
domain tag of each concept: geometry, foundations, dimension-theory, classics, ifs,
complex-dynamics, stochastic, generative, biological, statistical-physics, dynamics and
number-theory. [Chapter 4: Glossary and Equations](../foundations/glossary.md) is the
narrative counterpart.

### Proofs

The proof bundle holds appendix-level proofs for the quantitative results stated in
[Chapter 1: History of Fractal Mathematics](../foundations/history.md): the dimensions of
the Cantor set, Koch curve, Sierpinski triangle and carpet, Menger sponge and Barnsley fern;
the Mandelbrot escape criterion and boundary dimension; the Fatou-Julia connectedness
dichotomy; the Weierstrass function's nowhere-differentiability; the spectral exponent of
self-affine processes; the WBE quarter-power law; and the complex dimensions of the Cantor
string. Each record states the theorem, its assumptions, numbered proof steps, the
historical source, and a cross-link to the matching concept.

Every proof step is tagged:

- **`[verified]`**: checked by symbolic or numerical computation (SymPy, NumPy) in a way
  that the step describes and a reader can reproduce.
- **`[asserted]`**: relied upon as the conclusion of a named, published theorem (Moran's
  theorem, Hardy's theorem, Shishikura's theorem, the Fatou-Julia dichotomy) that is cited
  but not re-derived. These are the load-bearing external results.

The frontmatter field `verification_status` summarises a proof: `verified` (all
quantitative steps machine-checked; any asserted steps are standard textbook theorems),
`partially-verified` (core computation checked, substantive structural claims asserted) or
`unverified` (no step machine-checkable with available tools). At the time of writing the
twelve proofs split 7 verified, 4 partially verified and 1 unverified; the unverified one is
the Mandelbrot boundary dimension, which rests entirely on Shishikura's theorem.

## How to consume them

- **Rendered pages here.** [concepts/index.md](concepts/index.md) and
  [proofs/index.md](proofs/index.md) are the entry points; the group indexes and the
  individual records are reachable from them. They are deliberately kept out of the site
  navigation so that the navigation does not grow with the seed (progressive disclosure).
- **Raw Markdown twins.** Every rendered bundle page is also served verbatim at its source
  path: replace the trailing `/` with `.md` (for directory pages append `index.md`). The
  roots are [`/okf/concepts/index.md`](https://tyson-swetnam.github.io/fractal-notebooks/okf/concepts/index.md)
  and [`/okf/proofs/index.md`](https://tyson-swetnam.github.io/fractal-notebooks/okf/proofs/index.md);
  they carry only `okf_version: "0.2"`, as the specification's reserved-file rules require.
- **Canonical exchange copies.** The bundles are tracked in the repository under
  [`okf/`](https://github.com/tyson-swetnam/fractal-notebooks/tree/main/okf){target=_blank}
  (`okf/concepts/`, `okf/proofs/`). The site copies are staged from there at build time, so
  the repository is the place to diff, fork or ingest them.
- **Change history.** [concepts/log.md](concepts/log.md) and [proofs/log.md](proofs/log.md),
  newest first.

## Source of truth

- **Concepts are generated. Never hand-edit `okf/concepts/`.** The source is
  [`fractal_rag/src/fractal_rag/concepts/seed.yaml`](https://github.com/tyson-swetnam/fractal-notebooks/blob/main/fractal_rag/src/fractal_rag/concepts/seed.yaml){target=_blank}.
  To change a concept, edit the seed and run `fractal-rag okf export --out okf/concepts`;
  CI checks that the committed bundle matches the seed.
- **Proofs are hand-authored** in `okf/proofs/`. Adding one means writing the record with
  tagged steps and a `verification_status`, adding a line to `proofs/index.md`, and adding
  an entry to `proofs/log.md`.

## The Fractal RAG stack

The same ontology backs the [Fractal RAG stack](../fractal-rag/index.md): a Weaviate index
over the documentation, the notebooks and the reference literature, with a curated
`Concept` side-collection seeded from the same `seed.yaml`, exposed to agents through an
MCP server with eight retrieval tools. The bundles are the exchange form of that knowledge
(plain files, no server); the RAG stack is the search form (hybrid vector and keyword
retrieval, self-hosted). An agent that cannot reach the server can read everything here;
see [For AI Agents](../agents.md).
