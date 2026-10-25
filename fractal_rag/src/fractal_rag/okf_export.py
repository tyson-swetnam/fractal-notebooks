"""Generate the Open Knowledge Format (OKF v0.2) concept bundle from the concept seed.

OKF (https://github.com/GoogleCloudPlatform/knowledge-catalog) is a directory of
Markdown files with YAML frontmatter -- one concept per file -- designed to be read by
both humans and agents without bespoke tooling.

``concepts/seed.yaml`` is the authoring source of truth; the bundle under
``okf/concepts/`` is a *generated* artifact that is committed and drift-checked in CI.
Re-run this exporter whenever the seed changes so the two stay in sync::

    python -m fractal_rag.okf_export --out okf/concepts          # regenerate
    python -m fractal_rag.okf_export --out okf/concepts --check  # drift check, exit 1 on drift
    fractal-rag okf export --out okf/concepts                    # same thing via the CLI

Bundle layout and conventions (OKF v0.2 sections 4, 5, 8, 9 and 12):

* ``index.md`` (bundle root) carries only ``okf_version: "0.2"`` in its frontmatter and
  links every group index as ``<group>/index.md``.
* ``<group>/index.md`` -- one group per *first* domain tag -- has no frontmatter and lists
  the group's concepts with their one-sentence descriptions.
* ``<group>/<slug>.md`` carries ``type: Fractal Concept`` frontmatter in the fixed key
  order ``type, title, description, resource, tags, aliases?, hausdorff_dim_range?,
  sources, generated{by, at}, status`` and links related concepts with *relative* paths
  (``slug.md`` inside the group, ``../<group>/<slug>.md`` across groups) using the
  concept title as link text.
* ``log.md`` is append-only and frontmatter-free: every run that changes files prepends
  (or, on the same day, extends) a ``## <date>`` section with **Creation** / **Update** /
  **Deprecation** bullets naming the files (the OKF reserved-file vocabulary).

``generated.at`` is preserved from the file already on disk whenever a concept's rendered
content is otherwise unchanged, so re-exports are byte-stable and ``--date`` stamps only
new or changed concepts. Stale Markdown files under the output directory are deleted only
when this exporter produced them: ``generated.by`` equals :data:`GENERATOR`, or a
frontmatter-free ``index.md`` whose directory holds nothing but such files. A ``log.md`` at
any depth is never deleted. Any other Markdown file under ``--out`` makes the run refuse
(exit code 2, nothing written) unless ``--prune-unknown`` is given, so pointing ``--out`` at
the wrong directory (say ``okf`` instead of ``okf/concepts``) cannot wipe hand-written
bundles. Emptied directories are removed. All file I/O is UTF-8 with ``\\n`` newlines
regardless of the locale.

The module depends on PyYAML only (no Weaviate, no MCP) so it can run in the docs CI job.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import pathlib
import re
from dataclasses import dataclass, field
from typing import Any

import yaml

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------

_HERE = pathlib.Path(__file__).resolve().parent
DEFAULT_SEED = _HERE / "concepts" / "seed.yaml"
DEFAULT_OUT = pathlib.Path("okf/concepts")

OKF_VERSION = "0.2"
CONCEPT_TYPE = "Fractal Concept"
GENERATOR = "process:fractal-rag-okf-export"
STATUS = "stable"

SITE_URL = "https://tyson-swetnam.github.io/fractal-notebooks"
REPO_URL = "https://github.com/tyson-swetnam/fractal-notebooks"
SEED_SOURCE = "fractal_rag/src/fractal_rag/concepts/seed.yaml"
SEED_URL = f"{REPO_URL}/blob/main/{SEED_SOURCE}"
GLOSSARY_SOURCE = "docs/foundations/glossary.md"
GLOSSARY_TITLE = "Fractal Notebooks glossary (Chapter 4)"
SEED_TITLE = "fractal_rag concept seed (seed.yaml)"

LOG_NAME = "log.md"
LOG_TITLE = "# Concept Bundle Update Log"


def bundle_url(site_url: str = SITE_URL) -> str:
    """Public URL of the published bundle root (always ends with ``/``)."""
    return f"{site_url.rstrip('/')}/okf/concepts/"


def glossary_url(site_url: str = SITE_URL) -> str:
    """Public URL of the glossary chapter that backs every definition."""
    return f"{site_url.rstrip('/')}/foundations/glossary/"


BUNDLE_URL = bundle_url()
GLOSSARY_URL = glossary_url()

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

_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_LOG_HEADING_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------------------------------------------------------------------------
# YAML helpers
# ---------------------------------------------------------------------------


class _Quoted(str):
    """Marker type: dump this scalar double-quoted so ISO dates stay strings."""


class _Dumper(yaml.SafeDumper):
    pass


def _represent_quoted(dumper: yaml.SafeDumper, data: _Quoted) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style='"')


_Dumper.add_representer(_Quoted, _represent_quoted)


def _dump_yaml(data: dict[str, Any]) -> str:
    # width is large so one-sentence descriptions never wrap onto a continuation line.
    return yaml.dump(
        data,
        Dumper=_Dumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=4096,
    ).rstrip()


def split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    """Return ``(frontmatter dict or None, body)`` for a Markdown document."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None, text
    return (data if isinstance(data, dict) else {}), text[m.end() :]


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------


def slugify(name: str) -> str:
    """Concept-ID-safe slug: lowercase, hyphen-separated, alnum only."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def subdir_for(concept: dict[str, Any]) -> str:
    """First domain tag -> subdirectory slug (falls back to 'misc')."""
    domains = concept.get("domain") or []
    return slugify(str(domains[0])) if domains else "misc"


def _flatten(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


# A period that ends one of these is an abbreviation, not the end of the sentence.
_ABBREVIATIONS = ("et al.", "e.g.", "i.e.", "cf.", "vs.", "fig.", "figs.")
_SENTENCE_END_RE = re.compile(r"\.(?=\s|$)")


def _one_line(text: str) -> str:
    """Collapse whitespace and take the first sentence (ignoring common abbreviations)."""
    flat = _flatten(text)
    for m in _SENTENCE_END_RE.finditer(flat):
        head = flat[: m.end()]
        if head.lower().endswith(_ABBREVIATIONS):
            continue
        return head.strip()
    return flat


def description_for(definition: str) -> str:
    """First sentence of the definition as a plain-text ``description``.

    OKF v0.2 descriptions on this site are plain text without double quotes or angle
    brackets (``scripts/validate_okf.py`` rejects them; the page template escapes the
    ``<meta name="description">`` value with ``| e``, but the convention keeps the raw
    text attribute-safe too), so ASCII arrows and comparison operators are replaced with
    their Unicode equivalents, double quotes become apostrophes and any remaining ``<``
    or ``>`` characters are dropped.
    """
    text = _one_line(definition)
    for old, new in (("->", "→"), ("<=", "≤"), (">=", "≥")):
        text = text.replace(old, new)
    text = text.replace('"', "'")
    return re.sub(r"[<>]", "", text).strip()


def _plural(n: int, noun: str) -> str:
    return f"{n} {noun}" if n == 1 else f"{n} {noun}s"


# ---------------------------------------------------------------------------
# Seed loading & cross-references
# ---------------------------------------------------------------------------


def load_concepts(seed_path: pathlib.Path) -> list[dict[str, Any]]:
    """Load the seed YAML and check the minimal structure the exporter relies on."""
    with pathlib.Path(seed_path).open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    if not isinstance(raw, list):
        raise ValueError(f"{seed_path}: seed must be a YAML list of concepts")
    concepts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, entry in enumerate(raw):
        if not isinstance(entry, dict) or not entry.get("name") or not entry.get("definition"):
            raise ValueError(f"{seed_path}: entry {i} needs 'name' and 'definition'")
        name = str(entry["name"]).strip()
        if name.lower() in seen:
            raise ValueError(f"{seed_path}: duplicate concept name {name!r}")
        seen.add(name.lower())
        concepts.append({**entry, "name": name})
    return concepts


@dataclass(frozen=True)
class ConceptRef:
    """Where a concept lives in the bundle, plus its display title."""

    subdir: str
    slug: str
    title: str

    @property
    def rel_path(self) -> str:
        return f"{self.subdir}/{self.slug}.md"

    def link_from(self, subdir: str) -> str:
        """Relative link target from a file inside ``subdir``."""
        if subdir == self.subdir:
            return f"{self.slug}.md"
        return f"../{self.subdir}/{self.slug}.md"


def concept_ref(concept: dict[str, Any]) -> ConceptRef:
    return ConceptRef(subdir_for(concept), slugify(concept["name"]), concept["name"])


def build_alias_index(concepts: list[dict[str, Any]]) -> dict[str, ConceptRef]:
    """Map every name and alias (lowercased) to the concept it belongs to."""
    idx: dict[str, ConceptRef] = {}
    for c in concepts:
        ref = concept_ref(c)
        idx[c["name"].lower()] = ref
        for alias in c.get("aliases") or []:
            idx.setdefault(str(alias).lower(), ref)
    return idx


def find_related(concept: dict[str, Any], alias_index: dict[str, ConceptRef]) -> list[ConceptRef]:
    """Other concepts named in this definition, in order of first mention."""
    text = _flatten(concept["definition"]).lower()
    self_ref = concept_ref(concept)
    hits: dict[ConceptRef, int] = {}
    # Longest keys first so "self-affinity" wins over "self"; keys under 4 chars are too noisy.
    for key in sorted(alias_index, key=len, reverse=True):
        if len(key) < 4:
            continue
        ref = alias_index[key]
        if ref == self_ref or ref in hits:
            continue
        m = re.search(rf"\b{re.escape(key)}\b", text)
        if m:
            hits[ref] = m.start()
    return sorted(hits, key=lambda r: (hits[r], r.title))


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _stamp(date: str) -> _Quoted:
    return _Quoted(f"{date}T00:00:00Z")


def concept_frontmatter(concept: dict[str, Any], date: str, site_url: str = SITE_URL) -> str:
    ref = concept_ref(concept)
    fm: dict[str, Any] = {
        "type": CONCEPT_TYPE,
        "title": concept["name"],
        "description": description_for(concept["definition"]),
        "resource": f"{bundle_url(site_url)}{ref.subdir}/{ref.slug}/",
        "tags": [str(t) for t in (concept.get("domain") or [])],
    }
    if concept.get("aliases"):
        fm["aliases"] = [str(a) for a in concept["aliases"]]
    if concept.get("hausdorff_dim_range"):
        fm["hausdorff_dim_range"] = list(concept["hausdorff_dim_range"])
    fm["sources"] = [
        {"id": "glossary", "resource": glossary_url(site_url), "title": GLOSSARY_TITLE},
        {"id": "seed", "resource": SEED_URL, "title": SEED_TITLE},
    ]
    fm["generated"] = {"by": GENERATOR, "at": _stamp(date)}
    fm["status"] = STATUS
    return f"---\n{_dump_yaml(fm)}\n---"


def render_concept(
    concept: dict[str, Any],
    alias_index: dict[str, ConceptRef],
    date: str,
    site_url: str = SITE_URL,
) -> str:
    ref = concept_ref(concept)
    parts = [concept_frontmatter(concept, date, site_url), ""]

    parts.append("# Definition\n")
    parts.append(_flatten(concept["definition"]) + "\n")

    if concept.get("aliases"):
        parts.append("# Aliases\n")
        parts.append(", ".join(f"`{a}`" for a in concept["aliases"]) + "\n")

    dim = concept.get("hausdorff_dim_range")
    if dim:
        lo, hi = dim
        val = f"{lo}" if lo == hi else f"{lo} – {hi}"  # noqa: RUF001 (en dash intended)
        parts.append("# Hausdorff dimension\n")
        parts.append(f"Approximately **{val}**.\n")

    related = find_related(concept, alias_index)
    if related:
        parts.append("# Related concepts\n")
        for other in related:
            parts.append(f"* [{other.title}]({other.link_from(ref.subdir)})")
        parts.append("")

    parts.append("# Citations\n")
    parts.append(f"[1] [{GLOSSARY_TITLE}]({glossary_url(site_url)}) — `{GLOSSARY_SOURCE}`\n")
    parts.append(f"[2] [{SEED_TITLE}]({SEED_URL}) — `{SEED_SOURCE}`")
    return "\n".join(parts) + "\n"


def group_concepts(concepts: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for c in concepts:
        groups.setdefault(subdir_for(c), []).append(c)
    return groups


def _label(subdir: str) -> str:
    return DOMAIN_LABELS.get(subdir, subdir.replace("-", " ").title())


def render_root_index(groups: dict[str, list[dict[str, Any]]]) -> str:
    lines = [
        "---",
        f'okf_version: "{OKF_VERSION}"',
        "---",
        "",
        "# Fractal Notebooks — Concept Knowledge Bundle",
        "",
        # Maintainer note for people reading the source; an HTML comment so it is neither
        # rendered on the page nor picked up as the page description by generate_llms_txt.py.
        f"<!-- Generated from `{SEED_SOURCE}` — do not edit these files by hand; "
        "edit the seed and re-run the exporter. -->",
        "",
        "Canonical concepts for self-affine fractals, dimension theory, and metabolic scaling, "
        "grouped by domain.",
        "",
    ]
    for subdir in sorted(groups):
        count = _plural(len(groups[subdir]), "concept")
        lines.append(f"* [{_label(subdir)}]({subdir}/index.md) - {count}")
    lines += ["", f"See [{LOG_NAME}]({LOG_NAME}) for change history.", ""]
    return "\n".join(lines)


def render_subdir_index(subdir: str, concepts: list[dict[str, Any]]) -> str:
    lines = [f"# {_label(subdir)}", ""]
    for c in sorted(concepts, key=lambda x: x["name"]):
        lines.append(f"* [{c['name']}]({slugify(c['name'])}.md) - {description_for(c['definition'])}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Append-only log
# ---------------------------------------------------------------------------


def _log_bullets(
    added: list[str], updated: list[str], deleted: list[str], pruned: list[str] | None = None
) -> list[str]:
    def files(paths: list[str]) -> str:
        return ", ".join(f"`{p}`" for p in paths)

    bullets: list[str] = []
    if added:
        bullets.append(
            f"* **Creation**: {_plural(len(added), 'file')} added by the OKF v{OKF_VERSION} "
            f"exporter from `concepts/seed.yaml`: {files(added)}."
        )
    if updated:
        bullets.append(
            f"* **Update**: {_plural(len(updated), 'file')} regenerated by the OKF v{OKF_VERSION} "
            f"exporter from `concepts/seed.yaml`: {files(updated)}."
        )
    if deleted:
        bullets.append(
            f"* **Deprecation**: {_plural(len(deleted), 'stale file')} removed because the seed no "
            f"longer produces {'it' if len(deleted) == 1 else 'them'}: {files(deleted)}."
        )
    if pruned:
        bullets.append(
            f"* **Deprecation**: {_plural(len(pruned), 'unmanaged file')} not generated by the "
            f"exporter removed with `--prune-unknown`: {files(pruned)}."
        )
    return bullets


def update_log(
    existing: str | None,
    date: str,
    added: list[str],
    updated: list[str],
    deleted: list[str],
    pruned: list[str] | None = None,
) -> str | None:
    """Return the new log text, or ``None`` when there is nothing to record.

    The log is append-only: earlier sections are kept verbatim. A ``## <date>`` section is
    prepended, or extended when the newest section already carries today's date. Any
    frontmatter found on an older log is dropped (the log is frontmatter-free).
    """
    bullets = _log_bullets(added, updated, deleted, pruned)
    if not bullets:
        return None

    text = existing or ""
    _, text = split_frontmatter(text)
    lines = text.rstrip("\n").split("\n") if text.strip() else []

    header: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    for line in lines:
        m = _LOG_HEADING_RE.match(line)
        if m:
            sections.append((m.group(1), []))
        elif sections:
            sections[-1][1].append(line)
        else:
            header.append(line)
    if not any(h.startswith("# ") for h in header):
        header = [LOG_TITLE, *header]
    while header and not header[-1].strip():
        header.pop()

    if sections and sections[0][0] == date:
        body = [ln for ln in sections[0][1] if ln.strip()]
        sections[0] = (date, body + bullets)
    else:
        sections.insert(0, (date, bullets))

    out = [*header, ""]
    for i, (when, body) in enumerate(sections):
        body = [ln for ln in body if ln.strip()] if i == 0 else _strip_blank_edges(body)
        out.append(f"## {when}")
        out.extend(body)
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def _strip_blank_edges(lines: list[str]) -> list[str]:
    start, end = 0, len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


# ---------------------------------------------------------------------------
# Planning & writing
# ---------------------------------------------------------------------------


@dataclass
class Plan:
    """Everything one export run would write, compared against what is on disk."""

    date: str
    out_dir: pathlib.Path
    n_concepts: int
    n_groups: int
    files: dict[str, str] = field(default_factory=dict)  # rel posix path -> content
    added: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)  # stale files this exporter generated
    pruned: list[str] = field(default_factory=list)  # unmanaged files, only with prune_unknown
    unknown: list[str] = field(default_factory=list)  # unmanaged files that block the run

    @property
    def changed(self) -> int:
        return len(self.added) + len(self.updated) + len(self.deleted) + len(self.pruned)

    def stats(self) -> dict[str, int]:
        return {
            "concepts": self.n_concepts,
            "groups": self.n_groups,
            "added": len(self.added),
            "updated": len(self.updated),
            "deleted": len(self.deleted),
            "pruned": len(self.pruned),
            "unknown": len(self.unknown),
            "changed": self.changed,
        }


class UnmanagedFilesError(RuntimeError):
    """``--out`` holds Markdown files this exporter did not generate; refusing to touch them."""

    def __init__(self, out_dir: pathlib.Path, files: list[str]) -> None:
        self.out_dir = out_dir
        self.files = list(files)
        listing = "\n".join(f"  ? {rel}" for rel in self.files)
        super().__init__(
            f"okf export: refusing to write {out_dir}: {_plural(len(self.files), 'Markdown file')} "
            f"there {'was' if len(self.files) == 1 else 'were'} not generated by this exporter:\n"
            f"{listing}\n"
            "Check --out (the concept bundle lives in okf/concepts), remove the file(s) by hand, "
            "or pass --prune-unknown to delete them."
        )


def _read(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    with path.open("r", encoding="utf-8", newline="") as fh:
        return fh.read()


def _write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _generated_date(text: str | None) -> str | None:
    """``YYYY-MM-DD`` of ``generated.at`` in an existing concept file, if any."""
    if text is None:
        return None
    fm, _ = split_frontmatter(text)
    at = (fm or {}).get("generated", {}).get("at") if isinstance((fm or {}).get("generated"), dict) else None
    if isinstance(at, (_dt.datetime, _dt.date)):
        return at.strftime("%Y-%m-%d")
    if isinstance(at, str) and _DATE_RE.match(at[:10]):
        return at[:10]
    return None


def _validate_date(date: str | None) -> str:
    if date is None:
        return _dt.date.today().isoformat()
    try:
        return _dt.date.fromisoformat(date).isoformat()
    except ValueError as exc:
        raise ValueError(f"--date must be an ISO date (YYYY-MM-DD), got {date!r}") from exc


def _existing_markdown(out_dir: pathlib.Path) -> list[str]:
    if not out_dir.is_dir():
        return []
    return sorted(
        p.relative_to(out_dir).as_posix()
        for p in out_dir.rglob("*.md")
        if p.is_file() and not any(part.startswith(".") for part in p.relative_to(out_dir).parts)
    )


def _is_generated(text: str | None) -> bool:
    """True when the file's frontmatter says this exporter wrote it (``generated.by``)."""
    if text is None:
        return False
    fm, _ = split_frontmatter(text)
    generated = (fm or {}).get("generated")
    return isinstance(generated, dict) and generated.get("by") == GENERATOR


def _classify_unplanned(out_dir: pathlib.Path, planned: set[str]) -> tuple[list[str], list[str]]:
    """Split the ``*.md`` files under ``out_dir`` that this run does not produce.

    Returns ``(stale, unknown)``: *stale* files are safe to delete because the exporter
    generated them (``generated.by`` is :data:`GENERATOR`, or a frontmatter-free
    ``index.md`` whose directory holds nothing but such files); everything else is
    *unknown* and must not be touched without ``--prune-unknown``. A ``log.md`` at any
    depth belongs to neither list: logs are never deleted.
    """
    unplanned = [
        rel
        for rel in _existing_markdown(out_dir)
        if rel not in planned and pathlib.PurePosixPath(rel).name != LOG_NAME
    ]
    generated = {rel for rel in unplanned if _is_generated(_read(out_dir / rel))}
    stale: list[str] = []
    unknown: list[str] = []
    for rel in unplanned:
        if rel in generated:
            stale.append(rel)
            continue
        path = pathlib.PurePosixPath(rel)
        if path.name == "index.md" and path.parent != pathlib.PurePosixPath("."):
            siblings = [
                other for other in unplanned if pathlib.PurePosixPath(other).parent == path.parent
            ]
            siblings.remove(rel)
            if siblings and all(other in generated for other in siblings):
                stale.append(rel)  # a group index whose concepts the seed no longer produces
                continue
        unknown.append(rel)
    return stale, unknown


def plan(
    seed_path: pathlib.Path,
    out_dir: pathlib.Path,
    date: str | None = None,
    site_url: str = SITE_URL,
    prune_unknown: bool = False,
) -> Plan:
    """Render the bundle in memory and classify every file against ``out_dir``.

    With ``prune_unknown`` the Markdown files under ``out_dir`` that the exporter did not
    generate are scheduled for deletion (``Plan.pruned``); otherwise they are listed in
    ``Plan.unknown`` and :func:`apply` refuses to run while any exist.
    """
    date = _validate_date(date)
    out_dir = pathlib.Path(out_dir)
    concepts = load_concepts(pathlib.Path(seed_path))
    alias_index = build_alias_index(concepts)
    groups = group_concepts(concepts)
    result = Plan(date=date, out_dir=out_dir, n_concepts=len(concepts), n_groups=len(groups))

    result.files["index.md"] = render_root_index(groups)
    for subdir, members in groups.items():
        result.files[f"{subdir}/index.md"] = render_subdir_index(subdir, members)
        for c in members:
            rel = concept_ref(c).rel_path
            if rel in result.files:
                raise ValueError(f"two concepts render to the same file: {rel}")
            existing = _read(out_dir / rel)
            old_date = _generated_date(existing)
            if old_date is not None and render_concept(c, alias_index, old_date, site_url) == existing:
                result.files[rel] = existing  # content unchanged: keep the old generated.at
            else:
                result.files[rel] = render_concept(c, alias_index, date, site_url)

    for rel, text in result.files.items():
        existing = _read(out_dir / rel)
        if existing is None:
            result.added.append(rel)
        elif existing != text:
            result.updated.append(rel)
        else:
            result.unchanged.append(rel)
    result.deleted, unknown = _classify_unplanned(out_dir, set(result.files))
    if prune_unknown:
        result.pruned = unknown
    else:
        result.unknown = unknown
    return result


def apply(result: Plan) -> None:
    """Write the planned files, delete stale ones, prune empty dirs, update the log.

    Raises :class:`UnmanagedFilesError` (before writing anything) when ``result.unknown``
    lists files the exporter did not generate.
    """
    if result.unknown:
        raise UnmanagedFilesError(result.out_dir, result.unknown)
    out_dir = result.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    for rel in [*result.added, *result.updated]:
        _write(out_dir / rel, result.files[rel])
    for rel in [*result.deleted, *result.pruned]:
        (out_dir / rel).unlink()
    for d in sorted((p for p in out_dir.rglob("*") if p.is_dir()), reverse=True):
        if not any(d.iterdir()):
            d.rmdir()
    log_path = out_dir / LOG_NAME
    new_log = update_log(
        _read(log_path), result.date, result.added, result.updated, result.deleted, result.pruned
    )
    if new_log is not None:
        _write(log_path, new_log)


def export(
    seed_path: pathlib.Path,
    out_dir: pathlib.Path,
    today: str | None = None,
    *,
    site_url: str = SITE_URL,
    check: bool = False,
    prune_unknown: bool = False,
) -> dict[str, int]:
    """Export the seed as an OKF bundle (or, with ``check=True``, only report drift).

    Returns ``{concepts, groups, added, updated, deleted, pruned, unknown, changed}``;
    ``changed`` is the number of files that differ from disk (0 means the committed bundle
    is current) and ``unknown`` counts Markdown files under ``out_dir`` the exporter does
    not manage. In check mode nothing is written; otherwise :class:`UnmanagedFilesError`
    is raised (nothing written) when ``unknown`` is non-zero and ``prune_unknown`` is off.
    """
    result = plan(seed_path, out_dir, today, site_url, prune_unknown=prune_unknown)
    if not check:
        apply(result)
    return result.stats()


def _summary(result: Plan, check: bool) -> str:
    out = result.out_dir
    if check:
        if not result.changed and not result.unknown:
            return (
                f"okf export --check: {out} is up to date "
                f"({result.n_concepts} concepts across {result.n_groups} groups)"
            )
        detail = f"{result.changed} file(s) differ"
        if result.unknown:
            detail += f"; {len(result.unknown)} unmanaged file(s)"
        lines = [f"okf export --check: {out} is out of date ({detail}):"]
        lines += [f"  + {rel}" for rel in result.added]
        lines += [f"  ~ {rel}" for rel in result.updated]
        lines += [f"  - {rel}" for rel in [*result.deleted, *result.pruned]]
        lines += [
            f"  ? {rel} (not generated by this exporter; remove it or pass --prune-unknown)"
            for rel in result.unknown
        ]
        lines.append("Run `fractal-rag okf export` (or `python -m fractal_rag.okf_export`) and commit.")
        return "\n".join(lines)
    pruned = f", {len(result.pruned)} pruned" if result.pruned else ""
    return (
        f"Wrote {result.n_concepts} concepts across {result.n_groups} groups to {out} "
        f"({len(result.added)} added, {len(result.updated)} updated, "
        f"{len(result.deleted)} deleted{pruned}, {len(result.unchanged)} unchanged)"
    )


def run(
    seed_path: pathlib.Path,
    out_dir: pathlib.Path,
    date: str | None = None,
    site_url: str = SITE_URL,
    check: bool = False,
    *,
    prune_unknown: bool = False,
) -> tuple[int, str]:
    """Shared driver for ``python -m fractal_rag.okf_export`` and ``fractal-rag okf export``.

    Returns ``(exit_code, message)``: 1 when ``check`` finds drift or unmanaged files, 2 when
    a write run refuses because of unmanaged files (see :class:`UnmanagedFilesError`).
    """
    result = plan(seed_path, out_dir, date, site_url, prune_unknown=prune_unknown)
    if check:
        return (1 if result.changed or result.unknown else 0), _summary(result, check=True)
    try:
        apply(result)
    except UnmanagedFilesError as exc:
        return 2, str(exc)
    return 0, _summary(result, check=False)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=f"Export the concept seed as an OKF v{OKF_VERSION} bundle."
    )
    p.add_argument("--seed", type=pathlib.Path, default=DEFAULT_SEED, help="Concept seed YAML.")
    p.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT, help="Bundle directory.")
    p.add_argument(
        "--date",
        default=None,
        help="ISO date stamped on new/changed concepts (default: today).",
    )
    p.add_argument(
        "--site-url",
        default=SITE_URL,
        help="Published site root used for `resource` and source URLs.",
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="Write nothing; exit 1 if the bundle on disk differs from the seed.",
    )
    p.add_argument(
        "--prune-unknown",
        action="store_true",
        help=(
            "Also delete Markdown files under --out that this exporter did not generate "
            "(by default their presence makes the run refuse with exit code 2; log.md files "
            "are never deleted)."
        ),
    )
    args = p.parse_args(argv)
    code, message = run(
        args.seed, args.out, args.date, args.site_url, args.check, prune_unknown=args.prune_unknown
    )
    print(message)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
