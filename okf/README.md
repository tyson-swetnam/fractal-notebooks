# OKF Knowledge Bundle

This directory holds an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog)
(OKF v0.1) representation of the Fractal Notebooks concept ontology — a directory of
Markdown files with YAML frontmatter, one concept per file, readable by humans and
agents without any bespoke tooling.

## Layout

```
okf/concepts/
├── index.md          # root listing (progressive disclosure) — declares okf_version
├── log.md            # change history
└── <domain>/         # concepts grouped by their first domain tag
    ├── index.md
    └── <concept>.md
```

## Generated, not hand-authored

**The source of truth is `fractal_rag/src/fractal_rag/concepts/seed.yaml`.** This bundle
is a generated artifact. To change a concept, edit the seed and regenerate:

```bash
cd fractal_rag && pip install -e .
fractal-rag okf export --out ../okf/concepts
# or directly:
python -m fractal_rag.okf_export --out okf/concepts
```

Each concept file carries a required `type: Fractal Concept`, plus `title`,
`description`, `tags` (domains), `timestamp`, optional `aliases`, and
`hausdorff_dim_range`. Definitions cross-link to related concepts via
bundle-relative links and cite the project glossary.

## Conformance

The bundle conforms to OKF v0.1 §9: every concept file has parseable YAML frontmatter
with a non-empty `type`; `index.md` / `log.md` follow the reserved-file structure; the
root `index.md` declares `okf_version: "0.1"`. Cross-links are validated as part of
generation.

## Relationship to the RAG stack

OKF *complements* the Weaviate/MCP retrieval stack: the same ontology is exposed as a
plain-Markdown bundle (for exchange, diffing, and direct agent consumption) and as a
vector-indexed `Concept` collection (for hybrid search). Keep both in sync by treating
`seed.yaml` as the single authoring source.
