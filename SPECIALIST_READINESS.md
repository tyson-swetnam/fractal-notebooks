# Specialist Readiness — Tightening Checklist

Concrete steps to make Fractal Notebooks a clean, agent-consumable project ready for
**Claude Science Specialists**, an **OKF** knowledge bundle, and a **Zensical**
publishing path. Ordered by leverage. Each item is scoped so it can be done and
committed independently.

## 1. Make agent guidance portable and single-sourced

- [ ] **Adopt the updated `CLAUDE.md`** (tool-agnostic, with Claude Code vs Claude Science
      behavior split explicitly, and an Agents/Specialists section).
- [ ] **Add `AGENTS.md` as a symlink to `CLAUDE.md`** so non-Claude agents that honor the
      `AGENTS.md` convention get the same guidance from one source:
      `ln -s CLAUDE.md AGENTS.md`.
- [ ] **Remove the "commit after every prompt" blanket rule** for Claude Science. Auto-commit
      is a Claude Code behavior; Claude Science should produce artifacts and commit only on
      explicit instruction. (Done in the updated `CLAUDE.md`.)

## 2. Promote the subagent to a portable Specialist definition

- [ ] **Keep `.claude/agents/fractal-explorer.md` as the source of truth** for the prompt
      text and tool allowlist — it version-controls cleanly and both runtimes can read it.
- [ ] **Register the Specialist in Claude Science** via `host.agents.create(...)` (load the
      `customize` skill). Restrict it to the `mcp-fractal-rag` connector tools + read-only
      file access, mirroring the Claude Code `tools:` list. Document the mapping in
      `CLAUDE.md` (done) so the two definitions do not drift.
- [ ] **Add a short "How to run the fractal-explorer" section to `fractal_rag/README.md`**
      covering both runtimes (Claude Code auto-wires `.mcp.json`; Claude Science needs the
      connector added under Customize → Connectors, then `host.mcp("fractal-rag", ...)`).

## 3. Tighten the MCP connector contract

- [ ] **Document each of the 8 tools with input/output JSON schemas** in
      `fractal_rag/README.md` (name, params, defaults, return shape, error codes). Agents
      bind more reliably against explicit schemas than prose.
- [ ] **Confirm `.mcp.json` is portable.** It invokes the bare command `fractal-rag serve`,
      which assumes the package is installed and on `PATH`. Note that dependency in
      `CLAUDE.md`/README, or pin an absolute/venv path, so a fresh clone does not fail
      silently.
- [ ] **Surface stable error codes** (`not_found`, `invalid_argument`, `weaviate_error`,
      `unsupported`, `internal_error`) in the tool docs — the subagent already relies on them
      for retry logic.

## 4. Repository hygiene

- [ ] **Resolve the disabled workflows.** `.github/workflows/` has `deploy-all.yaml` +
      `test-build.yaml` active and three `.disabled` files (`deploy.yml`, `mkdocs.yaml`,
      `react-deploy.yaml`). Delete the superseded ones or add a one-line comment in each
      explaining why it is retained.
- [ ] **Reconcile the site name across files.** `README.md` title is "Fractal Notebooks";
      `mkdocs.yml` `site_name` is "Fractal Self-Affinity in Nature"; the copyright says
      "The University of Arizona" (2025) while the citation says 2026. Pick canonical values
      and make README, `mkdocs.yml`, and the BibTeX entry agree.
- [ ] **Verify `requirements.txt` reflects the live plugin set.** It carries commented-out
      pins and legacy tooling (`sphinx`, `tox`, `twine`, `bump2version`) that the docs build
      may not need. Split into `requirements-docs.txt` (build) vs dev extras, or prune.
- [ ] **Add a top-level `CONTRIBUTING.md`** (or expand README's contributing section) that
      states the env-per-component convention and the "run type-check + lint before commit"
      rule for React.

## 5. Prepare the OKF knowledge bundle

- [ ] **Generate an OKF bundle from `concepts/seed.yaml`.** Each of the 31 concepts becomes a
      Markdown file with YAML frontmatter (`type: concept` is the only required field;
      `title`, `description`, `tags`/domain, `timestamp` optional) and body = definition +
      aliases. Cross-link related concepts with Markdown links.
- [ ] **Add `index.md` (entry point / progressive disclosure) and `log.md` (change history)**
      at each bundle level, per the OKF spec.
- [ ] **Wire the bundle into the RAG stack** as an additional knowledge source so the MCP
      server and the OKF bundle stay consistent (single ontology, two surfaces).
- [ ] **Keep `seed.yaml` as the authoring source**; treat the OKF Markdown as a generated
      artifact so there is one place to edit a concept.

## 6. Plan the Zensical migration

- [ ] **Inventory MkDocs plugin usage** the site depends on: `mkdocs-jupyter`, MathJax,
      `mkdocs-pdf-export-plugin`, `mkdocs-git-revision-date-plugin`, mkdocstrings.
- [ ] **Check each against Zensical's compatibility matrix** before switching — Zensical reads
      `mkdocs.yml` natively but does not yet cover the entire Material/MkDocs plugin surface.
- [ ] **Add a parallel `zensical build` job** (non-blocking) in CI to track parity without
      breaking the live MkDocs deploy; promote to the primary builder only once notebooks,
      math, and PDF export render correctly.

## 7. Reproducibility for agents

- [ ] **Ensure every notebook declares its environment** (which `.yml` to use) in a top cell
      or adjacent README, so an agent knows what to instantiate.
- [ ] **Add a `corpus_stats()` smoke check** to the RAG test suite / CI so a Specialist can
      trust the index is populated before it answers (avoids confidently citing an empty
      corpus).
- [ ] **Pin the embedding model** (`Arctic-embed-l-v2.0`) and Weaviate version (1.35) in the
      README so retrieval is reproducible across redeploys.

---

**Quick wins first:** items 1 (`AGENTS.md` symlink + commit-policy split), 4 (workflows +
name reconciliation), and 3 (`.mcp.json` PATH note) are low-effort and unblock reliable
agent onboarding. The OKF bundle (5) and Zensical migration (6) are larger tracks worth
their own specs under `docs/superpowers/specs/`.
