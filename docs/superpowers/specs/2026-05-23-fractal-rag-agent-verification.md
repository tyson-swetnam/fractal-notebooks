# Fractal RAG Stack — Verification Checklist

Companion to `2026-05-23-fractal-rag-agent-design.md`. Walk this list once the
K3s cluster is up, the schema is bootstrapped, and `fractal-rag ingest --source all`
has completed. The goal is ≥7/8 prompts producing well-cited answers via the
`fractal-explorer` subagent.

## Pre-flight

1. **K3s pods healthy**
   ```bash
   kubectl -n ai-workloads get pods
   # Expect:  weaviate-*  Running   t2v-transformers-*  Running
   ```
2. **Weaviate reachable and reports the vectorizer module**
   ```bash
   curl -s localhost:30080/v1/.well-known/ready          # 200 OK
   curl -s localhost:30080/v1/meta | jq '.modules | keys'
   #   ["text2vec-transformers"]
   ```
3. **Package + CLI installed**
   ```bash
   cd fractal_rag && pip install -e ".[dev,parsers]"
   fractal-rag concepts validate         # OK: 31 concepts validated
   ```
4. **Schema bootstrapped (idempotent)**
   ```bash
   fractal-rag schema bootstrap          # second run -> "already_present"
   ```
5. **Ingest run completed**
   ```bash
   fractal-rag pull
   fractal-rag ingest --source all
   fractal-rag status
   # Expect: FractalArtifact total > 50000 (json) + ~600 (docs+notebooks)
   #         Concept total = 31
   ```
6. **MCP server discoverable in Claude Code**
   - Open Claude Code at the repo root.
   - `/mcp` lists `fractal-rag` as connected.
   - `Agent({ subagent_type: "fractal-explorer", ... })` works.

## The eight retrieval prompts

Run each through the `fractal-explorer` subagent. For each prompt, capture
(a) the agent's answer, (b) the citations it returned, and (c) a one-line
judgement of whether it was well-grounded.

| # | Prompt | What "good" looks like |
|---|---|---|
| 1 | "What is the Hausdorff dimension of the Cantor set, and what does the corpus say about its derivation?" | Cites the glossary concept entry AND at least one Constellate article or notebook covering Cantor sets / Hausdorff measure. Returns the value `log2/log3 ≈ 0.6309`. |
| 2 | "Find the notebook in this repo that introduces iterated function systems with Barnsley's fern." | Returns the `ch1_iterated_function_systems` notebook (or its predecessor `ferns.ipynb`) via `search_artifacts(target_vector='title_vec', source_types=['notebook'])`. |
| 3 | "Compare differential box-counting (DBC) with the plain box-counting method." | Two distinct citations — one for DBC, one for vanilla box-counting — pulled via `artifacts_by_concept` for both Concept names. |
| 4 | "What papers in the corpus relate fractal geometry to biological scaling laws (allometry)?" | At least three Constellate-source hits with `keyphrases` covering allometry / scaling / metabolic. |
| 5 | "Show me passages on the Riemann zeta function's connection to complex fractal dimensions." | At least one notebook hit (`ch1_complex_dimensions` or `zeta_3d`) plus an article hit; cites `Riemann Zeta Function` and `Complex Dimensions` concepts. |
| 6 | "Which concepts in the ontology have a Hausdorff dimension range recorded, and what are the values?" | Uses `list_concepts` then `get_concept` for each; returns Cantor, Sierpinski, Koch, Menger, DLA. |
| 7 | "Find articles published before 1990 about fractal noise or Brownian motion." | `search_artifacts` with `year_max=1990` and `source_types=['json_corpus']`; concept tags include `Brownian Motion` / `Pink Noise`. |
| 8 | "Where does this repo discuss the difference between self-similarity and self-affinity?" | Hits `docs/glossary.md` and/or `docs/foundations/glossary.md`; concept hits for both `Self-Similarity` and `Self-Affinity`. |

## Scoring

- Each prompt is **PASS** if the agent returns a coherent answer grounded in
  ≥1 citation whose `source_uri` you can resolve manually, and the citation
  actually supports the claim it backs.
- **PARTIAL** if the answer is correct but citations are weak or generic.
- **FAIL** if the answer is wrong, hallucinated, or citation-free.

Target: ≥7/8 PASS.

## Iteration

For each PARTIAL or FAIL, root-cause to one of:

| Likely cause | Where to fix |
|---|---|
| Parser dropped relevant content | `fractal_rag/src/fractal_rag/parsers/<type>.py` |
| Chunks too small / too large for the question | `Settings.chunk_max_tokens`, `chunk_overlap_tokens` |
| Concept missing from seed | `fractal_rag/src/fractal_rag/concepts/seed.yaml` |
| Retrieval picking wrong `target_vector` | tweak the agent prompt's rubric |
| Hybrid `alpha` favoring keyword over vector (or vice versa) | adjust agent's default `alpha` |
| Embedding model weak on technical math passages | swap to `nomic-embed-text-v2-moe` in `k3s-deployment/t2v-transformers-deployment.yaml` and rerun `fractal-rag ingest --source all` |

Use `/loop` on prompt #4 (the comparative-research one) to iterate retrieval
quality without re-running the full checklist. Stop iterating when the cited
papers stabilize across two consecutive loops.

## Done criteria

- ≥7/8 prompts PASS.
- `kubectl logs` for both Weaviate and `t2v-transformers` shows no error
  spikes during a full checklist walk.
- `~/.cache/fractal-rag/failed_objects.jsonl` is empty (or only contains
  expected items, e.g. zero-byte source files).
- `superpowers:verification-before-completion` skill walks clean.
