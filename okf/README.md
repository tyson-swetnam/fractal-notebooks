# OKF knowledge bundles

This directory holds two [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog)
(**OKF v0.2**) bundles: directories of Markdown files with YAML frontmatter that humans and
agents can read without bespoke tooling. The files here are canonical. The documentation
site copies them into `docs/okf/` at build time (gitignored) and publishes every file both
as a rendered page and as its raw Markdown twin under
`https://tyson-swetnam.github.io/fractal-notebooks/okf/`.

| Bundle | Contents | Authored | Root |
|---|---|---|---|
| `okf/concepts/` | 32 `type: Fractal Concept` pages in 12 domain groups | **generated** from `fractal_rag/src/fractal_rag/concepts/seed.yaml` | [`concepts/index.md`](concepts/index.md) |
| `okf/proofs/` | 12 `type: Fractal Proof` documents backing the quantitative claims in [Chapter 1](https://tyson-swetnam.github.io/fractal-notebooks/foundations/history/) | **hand-written** | [`proofs/index.md`](proofs/index.md) |

## Layout

```
okf/concepts/                 # GENERATED - never hand-edit
├── index.md                  # bundle root: frontmatter is only okf_version: "0.2"; links <group>/index.md
├── log.md                    # append-only change history (no frontmatter)
└── <group>/                  # one group per concept's first domain tag
    ├── index.md              # group listing (no frontmatter)
    └── <concept>.md          # type: Fractal Concept

okf/proofs/                   # HAND-WRITTEN
├── index.md                  # bundle root: okf_version: "0.2", verification conventions, proof list
├── log.md                    # change history (no frontmatter)
└── <proof>.md                # type: Fractal Proof
```

Both roots carry only `okf_version: "0.2"` in their frontmatter, as the spec reserves
them for; group indexes and both logs carry no frontmatter at all.

## Generated versus hand-written

**`okf/concepts/` is a build product.** The source of truth is
`fractal_rag/src/fractal_rag/concepts/seed.yaml`. To change a concept, edit the seed and
regenerate; CI fails when the committed bundle drifts from the seed.

```bash
# from the repo root, with the fractal_rag package importable (pip install -e fractal_rag)
PYTHONPATH=fractal_rag/src python -m fractal_rag.okf_export --out okf/concepts            # regenerate
PYTHONPATH=fractal_rag/src python -m fractal_rag.okf_export --out okf/concepts --check    # drift check, exit 1 on drift
fractal-rag okf export --out okf/concepts [--date YYYY-MM-DD] [--seed FILE] [--site-url URL] [--check]
```

The exporter needs only PyYAML. It preserves each concept's `generated.at` while the
rendered content is unchanged (re-exports are byte-stable), stamps only new or changed
concepts with `--date` (default: today), and prepends a dated **Creation** / **Update** /
**Deprecation** section to `log.md` (the OKF reserved-file vocabulary). It deletes only
stale files it generated itself (`generated.by: process:fractal-rag-okf-export`, or a
group `index.md` left with nothing but such files) and never any `log.md`; if `--out`
holds any other Markdown file (say `--out okf` instead of `okf/concepts`) it refuses with
exit code 2 and writes nothing, unless `--prune-unknown` is given. It writes nothing in
`--check` mode.

**`okf/proofs/` is hand-authored.** Every proof step is tagged `[verified]` (checked with
SymPy/NumPy, reproducibly) or `[asserted]` (rests on a cited, named theorem), and the
frontmatter `verification_status` is `verified`, `partially-verified` or `unverified`.
When adding a proof: write the document, add a line to `proofs/index.md`, add a dated
**Creation** bullet to `proofs/log.md`, and set the fields below by hand.

## Frontmatter (OKF v0.2)

Key order is fixed. Dates are quoted ISO-8601 strings; `description` is one plain-text
sentence (no double quotes or angle brackets); `resource` is the page's public URL.

| Key | Concept (generated) | Proof (hand-written) |
|---|---|---|
| `type` | `Fractal Concept` | `Fractal Proof` |
| `title`, `description`, `resource`, `tags` | from the seed; `resource` = `.../okf/concepts/<group>/<slug>/` | by hand; `resource` = `.../okf/proofs/<slug>/` |
| domain keys | `aliases`, `hausdorff_dim_range` (when present) | `result`, `concept` (relative link into `../concepts/`), `historical_source`, `verification_status` |
| `sources` | `glossary` (Chapter 4) and `seed` (seed.yaml on GitHub) | `history-chapter` (Chapter 1) |
| `generated` | `by: process:fractal-rag-okf-export`, `at` = date of last content change | `by: human:tswetnam`, `at: "2026-07-13T00:00:00Z"` |
| `verified` | not emitted (machine output) | `human:tswetnam`, 2026-07-13 on `verified` and `partially-verified` proofs; omitted when `verification_status` is `unverified` |
| `status` | `stable` | `stable` |

Concept pages link related concepts with relative paths (`slug.md` inside a group,
`../<group>/<slug>.md` across groups) so the bundle works from any mount point, and cite
the glossary chapter and the seed.

## Validation

The exporter does **not** validate cross-links while generating; correctness is enforced
by tests and CI instead:

- `fractal_rag/tests/unit/test_okf_export.py` (`pytest fractal_rag/tests/unit`) asserts,
  on a fixture seed and on the committed bundle, that every relative link resolves to a
  file on disk, that the root index links every group index, that concept frontmatter
  has the v0.2 keys in order, that the log is append-only, that stale files are deleted,
  and that `--check` passes against the committed `okf/concepts/`.
- The site build runs the exporter in `--check` mode and `scripts/validate_okf.py` over
  `okf/concepts` and `okf/proofs` (frontmatter policy, `resource` equal to the page URL,
  broken relative links, index coverage).

## Relationship to the RAG stack

OKF *complements* the Weaviate/MCP retrieval stack in `fractal_rag/`: the same ontology is
exposed as a plain-Markdown bundle (for exchange, diffing and direct agent consumption)
and as a vector-indexed `Concept` collection (for hybrid search); the `docs` ingest source
also indexes both bundles as `markdown` artifacts carrying their `resource` URL. Keep
them in sync by treating `seed.yaml` as the single authoring source.
