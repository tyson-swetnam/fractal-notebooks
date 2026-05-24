# Using the fractal-explorer Agent

You have a running Weaviate, the corpus is ingested, and Claude Code shows
`fractal-rag` as a connected MCP server under `/mcp`. This page is the
end-user guide for actually asking questions.

## The mental model

`fractal-explorer` is a **read-only retrieval subagent**. You hand it a
question; it picks the right MCP tool (or chain of tools), pulls back hits
from Weaviate, and synthesizes an answer with citations. It can't run shell
commands, can't edit files, and never writes to the index.

Two collections back every answer:

- **`FractalArtifact`** — chunked records of every notebook cell, markdown
  page, and Constellate article. Each chunk has three named vectors
  (`content_vec`, `title_vec`, `summary_vec`) plus cross-refs to the
  concepts it mentions.
- **`Concept`** — the curated ontology (~31 entries: Mandelbrot Set,
  Hausdorff Dimension, Hurst Exponent, DLA, …) with definitions and aliases.

## Invoking the agent

In any Claude Code session in this repo:

```text
> Use the fractal-explorer agent: "<your question>"
```

Or let Claude pick: just ask a fractal-math question and Claude will dispatch
the subagent on its own because the agent's `description:` advertises that
topic surface.

You can also invoke it programmatically from another agent:

```text
Agent({
  subagent_type: "fractal-explorer",
  description: "find DLA scaling exponent",
  prompt: "What value of the fractal dimension does the corpus report for 2D
           diffusion-limited aggregation, and which papers establish it?"
})
```

## The eight tools (cheat sheet)

| Tool | When to reach for it |
|---|---|
| `search_artifacts(query, target_vector=content_vec, source_types=…, year_min/max=…)` | First stop for any open-ended question |
| `get_artifact(uuid)` | Pull the full content of a search hit |
| `near_artifact(uuid)` | "More like this" expansion around a strong hit |
| `artifacts_by_concept(name)` | Exact concept tag filter |
| `list_concepts(domain=…)` | Browse the ontology |
| `get_concept(name)` | Canonical definition + aliases + Hausdorff dim range |
| `search_concepts(query)` | Semantic search when you don't know the canonical name |
| `corpus_stats()` | Sanity-check what's actually indexed |

The agent's full rubric (which tool fires for which question shape) lives in
`.claude/agents/fractal-explorer.md`. Edit that file if you want to bias
behavior — e.g., raise the default `limit`, or always prefer `summary_vec`
for "find me a paper" questions.

## Example transcripts

### Example 1 — Concept lookup with corroborating papers

> **You:** What is the Hausdorff dimension of the Cantor set, and what does
> the corpus say about its derivation?

The agent will typically:

1. Call `get_concept("Cantor Set")` → returns `hausdorff_dim_range = [0.6309, 0.6309]` with the definition.
2. Call `artifacts_by_concept("Cantor Set", limit=5)` → returns notebook + article hits.
3. Optionally call `get_artifact(uuid)` on the strongest hit to quote a passage.
4. Synthesize:

> The Cantor set has Hausdorff dimension $\log 2 / \log 3 \approx 0.6309$.
> The construction removes the middle third of each interval at every step,
> producing $N = 2$ self-similar copies at scale $r = 1/3$, so
> $D_H = -\log N / \log r = \log 2 / \log 3$. [^1][^2]
>
> [^1]: *Glossary of Self-Affine Fractal Properties* — `markdown`,
>       `file:///…/docs/glossary.md`, chunk 1
> [^2]: *Fractal dimensions of the Cantor set* (2014) — `json_corpus`,
>       `doi:10.xxxx/yyy`, chunk -1

### Example 2 — Find a notebook by topic

> **You:** Find the notebook in this repo that introduces iterated function
> systems with Barnsley's fern.

Agent calls `search_artifacts(query="Barnsley fern iterated function system",
target_vector="title_vec", source_types=["notebook"], limit=5)`, returns the
top hit with its `source_uri` (a `file://...#cell=N` URL you can open).

### Example 3 — Comparative synthesis

> **You:** Compare differential box-counting (DBC) with the plain box-counting
> method.

Agent runs two `artifacts_by_concept` calls (`"Differential Box-Counting"`
and `"Box-Counting Dimension"`), then `get_artifact` on the strongest hit
from each, then synthesizes the contrast with both citations attached.

### Example 4 — Historical scope

> **You:** Find articles published before 1990 about Brownian motion in the
> corpus.

Agent calls `search_artifacts(query="Brownian motion fractal",
source_types=["json_corpus"], year_max=1990, limit=10)`.

## Citation discipline

Every claim in the agent's answer should carry at least one footnote
pointing back to a real `source_uri`. If it doesn't, that's a bug — either
the agent is hallucinating, or the rubric needs sharpening. Open
`.claude/agents/fractal-explorer.md` and tighten the "Citation discipline"
section, or add explicit examples.

## Limits you should know about

- **No full text for Constellate articles.** Each article's "content" is
  synthesized from title + keyphrases + top n-grams. Quotation-style asks
  ("what does the paper *say*?") won't return prose; treat these hits as
  pointers to the actual paper (use the DOI).
- **Embedding model is English-only.** Non-English passages embed but
  retrieval quality is much weaker.
- **Concept ontology is hand-curated** (31 entries at v1). If your question
  hinges on a concept that isn't in `seed.yaml`, `artifacts_by_concept`
  won't find it; fall back to `search_artifacts`.
- **PDFs are optional** and currently empty in the default corpus.

## Iterating on agent quality

When you spot a weak answer:

1. Re-run the failing question through the agent **directly via the CLI** to
   isolate retrieval from synthesis:

    ```bash
    fractal-rag query "<the question>" --limit 10
    ```

2. If the CLI returns junk too, the problem is upstream — parser, chunking,
   or embedding choice. Walk
   [verification.md](../superpowers/specs/2026-05-23-fractal-rag-agent-verification.md#iteration)
   for fix triage.

3. If the CLI returns good hits but the agent still produces a thin answer,
   the problem is the agent prompt. Edit
   `.claude/agents/fractal-explorer.md` and add a more explicit rubric entry
   for that question shape.

4. Drive iteration with `/loop`:

    ```text
    /loop Use the fractal-explorer agent: "<your hardest test question>"
    ```

    Let it run a few cycles and watch whether the citations stabilize.

## Where to go next

- Prototype new query patterns in Python first → [Notebooks](notebooks/01_quickstart.ipynb)
- Agent isn't picking up the MCP server → [Troubleshooting](troubleshooting.md)
- Look under the hood → design spec at
  `docs/superpowers/specs/2026-05-23-fractal-rag-agent-design.md`
