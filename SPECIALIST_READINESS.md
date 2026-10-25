# Specialist Readiness — Tightening Checklist

Concrete steps to make Fractal Notebooks a clean, agent-consumable project ready for
**Claude Science Specialists**, an **OKF** knowledge bundle, and a **Zensical**
publishing path. Ordered by leverage. Each item is scoped so it can be done and
committed independently.

## 1. Make agent guidance portable and single-sourced

- [x] **Adopt the updated `CLAUDE.md`** (tool-agnostic, with Claude Code vs Claude Science
      behavior split explicitly, and an Agents/Specialists section).
- [x] **Add `AGENTS.md` as a symlink to `CLAUDE.md`** so non-Claude agents that honor the
      `AGENTS.md` convention get the same guidance from one source:
      `ln -s CLAUDE.md AGENTS.md`.
- [x] **Remove the "commit after every prompt" blanket rule** for Claude Science. Auto-commit
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
- [x] **Confirm `.mcp.json` is portable.** It invokes the bare command `fractal-rag serve`,
      which assumes the package is installed and on `PATH`. Done: `CLAUDE.md` ("Reaching the
      MCP server") documents that the env with the package must be activated before launching
      Claude Code, otherwise the server fails with `ENOENT`.
- [ ] **Surface stable error codes** (`not_found`, `invalid_argument`, `weaviate_error`,
      `unsupported`, `internal_error`) in the tool docs — the subagent already relies on them
      for retry logic.

## 4. Repository hygiene

- [x] **Resolve the disabled workflows.** Done: the three `.disabled` files (`deploy.yml`,
      `mkdocs.yaml`, `react-deploy.yaml`) were deleted in 3080fb1 (2026-07-13). `.github/workflows/`
      now holds `deploy-all.yaml` (Zensical + React deploy, live smoke test) and `test-build.yaml`
      (PR checks: docs pipeline, `fractal_rag` lint + tests, React, MkDocs rollback canary).
- [x] **Reconcile the copyright.** `zensical.toml` (and the frozen `mkdocs.yml`) now say
      "Copyright © 2026 The University of New Mexico"; the JSON-LD publisher in
      `overrides/main.html` matches. Author affiliations in the Part II pages are left as the
      historical University of Arizona departments.
- [ ] **Reconcile the site name across files.** `README.md` title is "Fractal Notebooks";
      `zensical.toml` `site_name` is "Fractal Self-Affinity in Nature". Pick canonical values
      and make README, `zensical.toml`, and the BibTeX entry agree.
- [x] **Verify `requirements.txt` reflects the live plugin set.** Done: the docs build uses the
      pinned `requirements-docs.txt` (Zensical, nbconvert, nbformat, PyYAML, pathspec);
      `requirements.txt` is kept only as the MkDocs rollback path until the cleanup phase.
- [ ] **Add a top-level `CONTRIBUTING.md`** (or expand README's contributing section) that
      states the env-per-component convention and the "run type-check + lint before commit"
      rule for React.

## 5. Prepare the OKF knowledge bundle

- [x] **Generate an OKF bundle from `concepts/seed.yaml`.** Done (`fractal-rag okf export`,
      OKF v0.2): each of the 32 concepts is a Markdown file with YAML frontmatter
      (`type: Fractal Concept`, `title`, `description`, `resource`, `tags`, `sources`,
      `generated`, `status`) and body = definition + aliases, cross-linked with relative
      Markdown links. Published at `/okf/concepts/` together with the hand-authored
      `okf/proofs/` bundle.
- [x] **Add `index.md` (entry point / progressive disclosure) and `log.md` (change history)**
      at each bundle level, per the OKF spec.
- [ ] **Wire the bundle into the RAG stack** as an additional knowledge source so the MCP
      server and the OKF bundle stay consistent (single ontology, two surfaces).
- [x] **Keep `seed.yaml` as the authoring source**; treat the OKF Markdown as a generated
      artifact so there is one place to edit a concept (CI runs `okf export --check`).

## 6. Zensical migration (done 2026-10-24)

- [x] **Inventory MkDocs plugin usage.** Done: the site depended on `mkdocs-jupyter` (notebooks,
      now pre-rendered by `scripts/render_notebooks.py`) and MathJax; `mkdocs-git-revision-date-plugin`
      and mkdocstrings were configured but unused. ~~`mkdocs-pdf-export-plugin`~~ was never
      configured in `mkdocs.yml` (it was only listed in `requirements.txt`), so there was no PDF
      export to preserve.
- [x] **Check each against Zensical's compatibility matrix.** Done: Zensical has no
      `mkdocs-jupyter` support (notebook pages are rendered to Markdown at commit time), ships
      native search and redirects, and renders math through `pymdownx.arithmatex` +
      `docs/javascripts/mathjax.js`.
- [x] **Switch the primary builder to Zensical.** Done: `zensical.toml` + `scripts/build_site.sh`
      build the site in CI (`deploy-all.yaml`); the MkDocs job in `test-build.yaml` remains only
      as a non-blocking rollback canary until the cleanup phase removes `mkdocs.yml`.

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
their own specs under `specs/`.
