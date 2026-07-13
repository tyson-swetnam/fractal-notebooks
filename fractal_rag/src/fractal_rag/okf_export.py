"""Generate an Open Knowledge Format (OKF v0.1) bundle from the concept seed.

OKF (https://github.com/GoogleCloudPlatform/knowledge-catalog) is a directory of
Markdown files with YAML frontmatter — one concept per file — designed to be read
by both humans and agents without bespoke tooling.

`concepts/seed.yaml` is the authoring source of truth; the OKF bundle is a *generated*
artifact. Re-run this exporter whenever the seed changes so the two stay in sync.

Usage:
    python -m fractal_rag.okf_export --out okf/concepts
    # or via the console entry point once wired into cli.py:
    fractal-rag okf export --out okf/concepts

The emitted bundle is conformant with OKF v0.1 §9:
  * every concept file has parseable YAML frontmatter with a non-empty `type`,
  * reserved filenames (`index.md`, `log.md`) follow §6 / §7.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import pathlib
import re
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------

_HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_SEED = _HERE / "concepts" / "seed.yaml"
OKF_VERSION = "0.1"
CONCEPT_TYPE = "Fractal Concept"

# Source that backs the definitions, cited in every concept body.
GLOSSARY_SOURCE = "docs/foundations/glossary.md"
GLOSSARY_URL = (
    "https://tyson-swetnam.github.io/fractal-notebooks/foundations/glossary/"
)

# Human-readable labels for the domain tags used to group concepts into
# subdirectories. The FIRST domain tag on a concept decides its subdirectory.
DOMAIN_LABELS: dict[str, str] = {
    "geometry": "Geometry",
    "foundations": "Foundations",
    "dimension-theory": "Dimension Theory",
    "measure-theory": "Measure Theory",
    "methods": "Methods",
    "image-analysis": "Image Analysis",
    "complex-dynamics": "Complex Dynamics",
    "classics": "Classical Fractals",
    "3d-fractals": "3D Fractals",
    "ifs": "Iterated Function Systems",
    "biological": "Biological Fractals",
    "branching": "Branching Structures",
    "generative": "Generative Grammars",
    "stochastic": "Stochastic Processes",
    "hurst": "Hurst / Long-Range Dependence",
    "signal-processing": "Signal Processing",
    "texture": "Texture",
    "number-theory": "Number Theory",
    "complex-analysis": "Complex Analysis",
    "advanced": "Advanced Topics",
    "statistics": "Statistics",
    "scaling": "Scaling",
    "dynamics": "Dynamics",
    "statistical-physics": "Statistical Physics",
    "topology": "Topology",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def slugify(name: str) -> str:
    """Concept-ID-safe slug: lowercase, hyphen-separated, alnum only."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def subdir_for(concept: dict[str, Any]) -> str:
    """First domain tag → subdirectory slug (falls back to 'misc')."""
    domains = concept.get("domain") or []
    return slugify(domains[0]) if domains else "misc"


def build_alias_index(concepts: list[dict[str, Any]]) -> dict[str, str]:
    """Map every name and alias (lowercased) to a bundle-relative concept path."""
    idx: dict[str, str] = {}
    for c in concepts:
        rel = f"/{subdir_for(c)}/{slugify(c['name'])}.md"
        idx[c["name"].lower()] = rel
        for alias in c.get("aliases") or []:
            idx.setdefault(alias.lower(), rel)
    return idx


def find_related(
    concept: dict[str, Any], alias_index: dict[str, str], self_path: str
) -> list[tuple[str, str]]:
    """Return (display, path) links for other concepts named in this definition."""
    text = concept["definition"].lower()
    seen: set[str] = set()
    related: list[tuple[str, str]] = []
    # Longest keys first so "self-affinity" wins over "self".
    for key in sorted(alias_index, key=len, reverse=True):
        if len(key) < 4:
            continue
        path = alias_index[key]
        if path == self_path or path in seen:
            continue
        if re.search(rf"\b{re.escape(key)}\b", text):
            related.append((key, path))
            seen.add(path)
    return related


def frontmatter(concept: dict[str, Any], today: str) -> str:
    fm: dict[str, Any] = {
        "type": CONCEPT_TYPE,
        "title": concept["name"],
        "description": _one_line(concept["definition"]),
        "tags": concept.get("domain") or [],
        "timestamp": f"{today}T00:00:00Z",
    }
    if concept.get("aliases"):
        fm["aliases"] = concept["aliases"]
    if concept.get("hausdorff_dim_range"):
        fm["hausdorff_dim_range"] = concept["hausdorff_dim_range"]
    body = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=100).rstrip()
    return f"---\n{body}\n---"


def _one_line(text: str) -> str:
    """Collapse whitespace and take the first sentence for the description field."""
    flat = re.sub(r"\s+", " ", text).strip()
    m = re.match(r"(.+?\.)(\s|$)", flat)
    return (m.group(1) if m else flat).strip()


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render_concept(
    concept: dict[str, Any], alias_index: dict[str, str], today: str
) -> str:
    self_path = f"/{subdir_for(concept)}/{slugify(concept['name'])}.md"
    parts = [frontmatter(concept, today), ""]

    parts.append("# Definition\n")
    parts.append(re.sub(r"\s+", " ", concept["definition"]).strip() + "\n")

    if concept.get("aliases"):
        parts.append("# Aliases\n")
        parts.append(", ".join(f"`{a}`" for a in concept["aliases"]) + "\n")

    dim = concept.get("hausdorff_dim_range")
    if dim:
        lo, hi = dim
        val = f"{lo}" if lo == hi else f"{lo} – {hi}"
        parts.append("# Hausdorff dimension\n")
        parts.append(f"Approximately **{val}**.\n")

    related = find_related(concept, alias_index, self_path)
    if related:
        parts.append("# Related concepts\n")
        for display, path in related:
            parts.append(f"* [{display}]({path})")
        parts.append("")

    parts.append("# Citations\n")
    parts.append(
        f"[1] [Fractal Notebooks glossary]({GLOSSARY_URL}) — `{GLOSSARY_SOURCE}`"
    )
    return "\n".join(parts) + "\n"


def render_root_index(groups: dict[str, list[dict[str, Any]]]) -> str:
    lines = [
        "---",
        f'okf_version: "{OKF_VERSION}"',
        "---",
        "",
        "# Fractal Notebooks — Concept Knowledge Bundle",
        "",
        "Canonical concepts for self-affine fractals, dimension theory, and metabolic",
        "scaling. Generated from `fractal_rag/src/fractal_rag/concepts/seed.yaml` — do",
        "not edit these files by hand; edit the seed and re-run the exporter.",
        "",
    ]
    for subdir in sorted(groups):
        label = DOMAIN_LABELS.get(subdir, subdir.replace("-", " ").title())
        count = len(groups[subdir])
        lines.append(f"* [{label}]({subdir}/) - {count} concept(s)")
    lines.append("")
    return "\n".join(lines)


def render_subdir_index(subdir: str, concepts: list[dict[str, Any]]) -> str:
    label = DOMAIN_LABELS.get(subdir, subdir.replace("-", " ").title())
    lines = [f"# {label}", ""]
    for c in sorted(concepts, key=lambda x: x["name"]):
        lines.append(f"* [{c['name']}]({slugify(c['name'])}.md) - {_one_line(c['definition'])}")
    lines.append("")
    return "\n".join(lines)


def render_log(today: str, n_concepts: int, n_groups: int) -> str:
    return "\n".join(
        [
            "# Concept Bundle Update Log",
            "",
            f"## {today}",
            f"* **Initialization**: Generated OKF v{OKF_VERSION} bundle with "
            f"{n_concepts} concepts across {n_groups} groups from `concepts/seed.yaml`.",
            "",
        ]
    )


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def export(seed_path: pathlib.Path, out_dir: pathlib.Path, today: str | None = None) -> dict[str, int]:
    today = today or _dt.date.today().isoformat()
    concepts: list[dict[str, Any]] = yaml.safe_load(seed_path.read_text())
    alias_index = build_alias_index(concepts)

    groups: dict[str, list[dict[str, Any]]] = {}
    for c in concepts:
        groups.setdefault(subdir_for(c), []).append(c)

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.md").write_text(render_root_index(groups))
    (out_dir / "log.md").write_text(render_log(today, len(concepts), len(groups)))

    for subdir, members in groups.items():
        d = out_dir / subdir
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.md").write_text(render_subdir_index(subdir, members))
        for c in members:
            (d / f"{slugify(c['name'])}.md").write_text(
                render_concept(c, alias_index, today)
            )

    return {"concepts": len(concepts), "groups": len(groups)}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Export concept seed as an OKF v0.1 bundle.")
    p.add_argument("--seed", type=pathlib.Path, default=DEFAULT_SEED)
    p.add_argument("--out", type=pathlib.Path, default=pathlib.Path("okf/concepts"))
    p.add_argument("--date", default=None, help="ISO date to stamp (default: today).")
    args = p.parse_args(argv)
    stats = export(args.seed, args.out, args.date)
    print(f"Wrote {stats['concepts']} concepts across {stats['groups']} groups to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
