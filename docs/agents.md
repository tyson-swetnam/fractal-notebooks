---
type: Guide
title: For AI Agents
description: >-
  How AI agents and harnesses should consume this site: llms.txt and
  llms-full.txt, Markdown twins with OKF v0.2 frontmatter, the concept and
  proof knowledge bundles, notebook source links, and the trust signals to
  read before relying on a page.
resource: https://tyson-swetnam.github.io/fractal-notebooks/agents/
tags: [agents, okf, llms-txt, knowledge]
sources:
  - id: okf-spec
    resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
    title: Open Knowledge Format (OKF) v0.2 specification
  - id: llms-txt
    resource: https://llmstxt.org/
    title: The /llms.txt convention
generated:
  by: claude-code/claude-fable-5-1
  at: "2026-10-24T00:00:00Z"
status: stable
---

# For AI Agents

This site is published for people **and** for AI agents. The `docs/` tree behind it is an
[Open Knowledge Format (OKF) v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md){target=_blank}
knowledge bundle, and two further bundles (the fractal concept ontology and the appendix
proofs) are published through it. If you are an agent, or you are wiring one up, consume
the content through the endpoints below rather than scraping rendered HTML.

## Entry points

| Endpoint | What you get |
|----------|--------------|
| [`/fractal-notebooks/llms.txt`](https://tyson-swetnam.github.io/fractal-notebooks/llms.txt) | Linked outline of every page, concept, proof and interactive app with a one-line description each, per the [llms.txt convention](https://llmstxt.org/){target=_blank}. Start here. |
| [`/fractal-notebooks/llms-full.txt`](https://tyson-swetnam.github.io/fractal-notebooks/llms-full.txt) | The whole corpus in one file: every page's Markdown source with its frontmatter, each prefixed by its canonical `URL:` and `Source:` lines. Prefer this over crawling. |
| Markdown twin of any page | Replace the trailing `/` of a page URL with `.md`. For directory pages (the home page, the section landings, the OKF group indexes) append `index.md` instead. Examples: `/foundations/history/` has the twin [`/foundations/history.md`](https://tyson-swetnam.github.io/fractal-notebooks/foundations/history.md); `/metabolic-scaling/` has [`/metabolic-scaling/index.md`](https://tyson-swetnam.github.io/fractal-notebooks/metabolic-scaling/index.md); the home page has [`/index.md`](https://tyson-swetnam.github.io/fractal-notebooks/index.md). When in doubt, read the `<link rel="alternate" type="text/markdown">` element in the page head, which carries the exact URL. |
| OKF bundle roots | [`/okf/concepts/index.md`](https://tyson-swetnam.github.io/fractal-notebooks/okf/concepts/index.md) (32 concepts in 12 groups) and [`/okf/proofs/index.md`](https://tyson-swetnam.github.io/fractal-notebooks/okf/proofs/index.md) (12 proofs). Both are served verbatim here; the canonical exchange copies live in the repository under [`okf/`](https://github.com/tyson-swetnam/fractal-notebooks/tree/main/okf){target=_blank}. The human-readable overview is [Knowledge Bundles](okf/index.md). |
| Change logs | [`/log/`](log.md) for the site, plus [`/okf/concepts/log/`](okf/concepts/log.md) and [`/okf/proofs/log/`](okf/proofs/log.md) for the two bundles. Newest entries first; bullets are tagged **Creation**, **Update** or **Deprecation**. |
| [`/fractal-notebooks/sitemap.xml`](https://tyson-swetnam.github.io/fractal-notebooks/sitemap.xml) | Standard crawl surface. This is a GitHub Pages project site, so crawlers read the host-root [robots.txt](https://tyson-swetnam.github.io/robots.txt){target=_blank}, which is fully permissive; the copy at [`/fractal-notebooks/robots.txt`](https://tyson-swetnam.github.io/fractal-notebooks/robots.txt) is informational and restates these entry points. |
| Notebook pages | The 18 published notebooks are pre-rendered from their stored outputs; nothing executes at build time. Each page's frontmatter carries `notebook.source` (GitHub blob), `notebook.raw`, `notebook.nbviewer` and `notebook.colab`. The `.ipynb` files themselves are **not** hosted on this site, so fetch them from GitHub. The 73 unpublished research notebooks are catalogued on [Research Notebooks](notebooks/research.md). |
| React apps (`/react/`) | One crawlable URL. The apps are a HashRouter single-page application with 16 routes after `#/`, rendered entirely by JavaScript, so fetching `/react/` returns an empty shell. Read [React Apps](applications/react-apps.md) for the route table and what each app does. |
| Streamlit apps | Not hosted anywhere. Their sources live in the repository's [`apps/`](https://github.com/tyson-swetnam/fractal-notebooks/tree/main/apps){target=_blank} directory and are documented on [Streamlit Apps](applications/streamlit-apps.md). |
| Fractal RAG MCP server | Self-hosted and **not public**. The [Fractal RAG](fractal-rag/index.md) guide explains how to run the Weaviate index and the eight-tool MCP server yourself; it indexes the same pages and the same concept ontology that you can read here directly. |
| [Source repository](https://github.com/tyson-swetnam/fractal-notebooks){target=_blank} | The bundles, the notebooks, the validator (`scripts/validate_okf.py`) and the build pipeline. |

## HTML head signals

Every rendered page declares its Markdown twin and structured metadata in its `<head>`.
This page, for example, carries:

```html
<link rel="alternate" type="text/markdown" href="https://tyson-swetnam.github.io/fractal-notebooks/agents.md">
<meta name="okf:type" content="Guide">
<meta name="okf:status" content="stable">
<meta name="okf:generated-at" content="2026-10-24T00:00:00Z">
<script type="application/ld+json">
{ "@context": "https://schema.org", "@type": "LearningResource",
  "learningResourceType": "Guide",
  "url": "https://tyson-swetnam.github.io/fractal-notebooks/agents/",
  "encoding": { "@type": "MediaObject",
                "contentUrl": "https://tyson-swetnam.github.io/fractal-notebooks/agents.md",
                "encodingFormat": "text/markdown" },
  "license": "https://creativecommons.org/licenses/by/4.0/", ... }
</script>
```

The JSON-LD `@type` follows the page type: `ScholarlyArticle` (with `author` on Part II,
the only Part whose pages name their authors) for `Paper Section` pages, `LearningResource`
for `Chapter`, `Notebook` and `Guide` pages, `CreativeWork` otherwise.

## Reading the OKF frontmatter

Each page's YAML frontmatter answers the questions an agent should ask before relying on
content:

- **What is this?** `type`. On the documentation bundle: `Index` (home and section
  landings), `Chapter` (Part I), `Paper Section` (Parts II to V), `Notebook` (rendered
  notebooks), `Guide` (apps, Fractal RAG, this page), `Reference` (glossary, reference
  lists, the research-notebook catalogue) and `Log`. In the knowledge bundles: `Fractal
  Concept` and `Fractal Proof`. Plus `title`, `description` and controlled `tags`.
- **Where did it come from?** `generated: { by, at }` uses the OKF actor syntax:
  `human:tswetnam` for authored pages, `process:scripts/render_notebooks.py` for notebook
  pages, `process:fractal-rag-okf-export` for concepts, and `<producer>/<model>` (for
  example `claude-code/claude-fable-5-1`) for pages drafted by an AI assistant, which carry
  no `verified` entry until a human re-reads them. `sources` lists the external
  references a page's claims depend on (for a notebook page, the `.ipynb` it was rendered
  from). Part II pages also carry `paper`, `authors` (with ORCID iDs) and `citation`;
  Parts III to V carry `paper` only, because their pages name no authors.
- **How much should I trust it?**
    - `verified`, a list of `{ by, at }` events, marks pages a human has re-read; its
      presence puts a page in OKF's human-reviewed tier. A page without it is generated or
      not yet re-read, which is a weaker claim, not an error.
    - Notebook pages: `notebook.cells` gives `markdown`, `code`, `executed`, `figures` and
      `errors` counts. `errors` above zero means a stored cell raised; the page shows it as a
      failure admonition with the exception name and message. A notebook rendered from
      stale or missing outputs is marked `status: draft`.
    - Proofs: `verification_status` is `verified`, `partially-verified` or `unverified`,
      and every proof step is tagged `[verified]` (reproduced with SymPy or NumPy) or
      `[asserted]` (rests on a cited, named theorem that is not re-derived). Treat
      `[asserted]` steps as citations to check, not as results of this site.
- **Is it current?** `status` is `stable` or `draft`. `stale_after`, where present, dates a
  page whose content should be re-verified after that date.

!!! warning "Research content is unpublished draft material"

    Parts II to V (Metabolic Scaling, Spectral Geometry, Biological Geometry, Research
    Hypotheses) are manuscript drafts and a preregistration framework, not peer-reviewed
    publications. Their section pages carry `status: draft` (the four landing pages are
    `stable`), and some of their citations are still placeholders. Quote them as working drafts attributed to this site, and do not present
    their claims as established results.

Bundle shapes differ on purpose. The two exchange bundles stay spec-pure: `okf/concepts/index.md`
and `okf/proofs/index.md` carry only `okf_version: "0.2"`, and the group indexes and the two
bundle logs have no frontmatter at all. The documentation bundle is richer: its home page
declares `okf_version: "0.2"` and its landings and `log.md` carry full frontmatter, the
convention shared with the related sites below.

## Citing this material

- Cite the canonical page URL, the `resource` field, not the `.md` twin.
- For the project as a whole, the [home page](index.md#citation) gives a BibTeX entry,
  `swetnam2026fractals`: Swetnam, Pelletier and Enquist, *Fractal Patterns in Nature:
  Self-Affinity vs Self-Similarity*, 2026, https://github.com/tyson-swetnam/fractal-notebooks.
- Proof pages name their `historical_source`. Cite the original theorem for the
  mathematics, and this site for the verification record.

## Related OKF bundles

The author publishes other GitHub Pages sites with the same conventions:

- [tyson-swetnam.github.io/okf/index.md](https://tyson-swetnam.github.io/okf/index.md){target=_blank}: the root bundle, one record per site
- [intro-gpt llms.txt](https://tyson-swetnam.github.io/intro-gpt/llms.txt){target=_blank}: GPT 101, a self-paced workshop on generative AI and prompt engineering for research and teaching
- [energetics-pymol llms.txt](https://tyson-swetnam.github.io/energetics-pymol/llms.txt){target=_blank}: reproducible 3D molecular models of the molecules that store a conifer forest's chemical energy, annotated with OBO Foundry ontology terms
- [cod-kmap llms.txt](https://tyson-swetnam.github.io/cod-kmap/llms.txt){target=_blank}: the Coastal Observatory Design knowledge map, with Parquet tables queryable over HTTP

!!! info "Ground rules for agents"

    All content is [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/){target=_blank}:
    reuse freely with attribution. Crawling, indexing and AI grounding are welcome (see the
    host [robots.txt](https://tyson-swetnam.github.io/robots.txt){target=_blank}). Prefer
    `llms-full.txt` for one-shot ingestion over crawling the site, respect `status: draft`,
    and cite the canonical page URL (the `resource` field), not the `.md` source URL, when
    referencing this material for humans. Third-party material keeps its own licence: the
    OpenTopography 3DEP tutorial notebooks mirrored in the repository are GPL-3.0 upstream.
