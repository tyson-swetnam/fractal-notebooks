#!/usr/bin/env python3
"""Validate an OKF v0.2 bundle (docs/, okf/concepts or okf/proofs).

Adapted from tyson-swetnam/intro-gpt scripts/validate_okf.py for a site that
publishes three bundles with different reserved-file conventions:

  --profile docs     the site bundle (docs/). index.md and log.md are *typed*
                     pages (type: Index / Log) and carry full frontmatter;
                     docs/index.md declares okf_version "0.2" as its FIRST key.
  --profile concept  the generated concept bundle. The root index.md carries
                     only okf_version; group index.md and log.md carry no
                     frontmatter (spec-pure exchange bundle).
  --profile proof    the hand-written proof bundle; same reserved-file rules.

Checks on every typed page: parseable frontmatter; type in the profile's
taxonomy; non-empty unique title; plain-text description (50-300 chars, none of
the characters " < > which break the unescaped <meta name="description">);
resource == canonical page URL; 2-6 tags from the vocabulary (warn on unknown);
sources[] with http(s) resources; generated{by, at} actor + ISO-8601; optional
verified[]; status draft|stable|deprecated; stale_after. Bundle-level checks:
reserved files, transitive index coverage (root index -> section index -> page),
log.md structure (newest-first ## YYYY-MM-DD, convention bullets), and internal
.md link targets.

Output: one "path: [ERROR|WARN] message" line per finding, then a summary with
per-type counts. Exit 1 on any ERROR (or any WARN with --strict).

Usage:
  python scripts/validate_okf.py docs --exclude 'okf/concepts/**' --exclude 'okf/proofs/**' [--site-url URL] [--config zensical.toml]
  python scripts/validate_okf.py okf/concepts --profile concept
  python scripts/validate_okf.py okf/proofs --profile proof
"""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pathspec

sys.path.insert(0, str(Path(__file__).resolve().parent))
from okf_common import (  # noqa: E402
    ConfigError,
    ROOT,
    exclude_spec,
    html_url,
    is_excluded,
    iter_link_targets,
    load_config,
    split_frontmatter,
    split_target,
)

OKF_VERSION = "0.2"

PROFILES: dict[str, dict] = {
    "docs": {
        "types": {"Index", "Chapter", "Paper Section", "Notebook", "Guide", "Reference", "Log"},
        "resource_prefix": "",
        "typed_reserved": True,  # index.md / log.md carry full frontmatter
        "extra_keys": {"paper", "authors", "citation", "companion_page", "notebook", "hide", "icon", "okf_version"},
    },
    "concept": {
        "types": {"Fractal Concept"},
        "resource_prefix": "okf/concepts",
        "typed_reserved": False,
        "extra_keys": {"aliases", "hausdorff_dim_range"},
    },
    "proof": {
        "types": {"Fractal Proof"},
        "resource_prefix": "okf/proofs",
        "typed_reserved": False,
        "extra_keys": {"result", "concept", "historical_source", "verification_status"},
    },
}

# Controlled tag vocabulary (the migration plan's list). Grow deliberately.
TAGS = {
    # kind
    "foundations", "research", "paper", "notebook", "app", "knowledge", "agents", "reference", "tutorial",
    # part
    "part-i", "part-ii", "part-iii", "part-iv", "part-v",
    # math
    "geometry", "dimension-theory", "measure-theory", "methods", "image-analysis", "complex-dynamics",
    "classics", "3d-fractals", "ifs", "biological", "branching", "generative", "stochastic", "hurst",
    "signal-processing", "texture", "number-theory", "complex-analysis", "advanced", "statistics",
    "scaling", "dynamics", "statistical-physics", "topology",
    # science
    "self-affinity", "self-similarity", "metabolic-scaling", "allometry", "spectral-geometry",
    "riemann-zeta", "complex-dimensions", "dla", "lidar", "canopy-height-model", "3dep",
    "forest-ecology", "preregistration",
    # tooling
    "jupyter", "react", "streamlit", "blender", "cuda", "rag", "weaviate", "mcp", "okf", "llms-txt",
}

STATUS = {"draft", "stable", "deprecated"}
VERIFICATION_STATUS = {"verified", "partially-verified", "unverified"}
BASE_KEYS = {"type", "title", "description", "resource", "tags", "sources", "generated", "verified", "status", "stale_after"}
KEY_ORDER = [
    "okf_version", "type", "title", "description", "resource", "tags", "paper", "authors", "citation",
    "companion_page", "notebook", "aliases", "hausdorff_dim_range", "result", "concept", "historical_source",
    "verification_status", "sources", "generated", "verified", "status", "stale_after",
]

ACTOR_RE = re.compile(r"^(human:[A-Za-z0-9_.@-]+|process:[A-Za-z0-9_./-]+|[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)$")
ORCID_RE = re.compile(r"^https://orcid\.org/\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
SHORTCODE_RE = re.compile(r":(material|fontawesome|simple|octicons|lucide)[-_a-z0-9/]*:")
LOG_HEADING_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$")
LOG_CONVENTION_RE = re.compile(r"\*\*(Creation|Update|Deprecation|Deletion|Initialization)\*\*")
JUNK_PREFIXES = ("#", ".#")


def parse_iso(value) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class Reporter:
    def __init__(self) -> None:
        self.errors = 0
        self.warnings = 0
        self.lines: list[str] = []

    def error(self, path: str, msg: str) -> None:
        self.errors += 1
        self.lines.append(f"{path}: [ERROR] {msg}")

    def warn(self, path: str, msg: str) -> None:
        self.warnings += 1
        self.lines.append(f"{path}: [WARN] {msg}")


def is_junk(rel: Path) -> bool:
    return any(part.startswith(JUNK_PREFIXES) or part.endswith("~") or part.startswith(".") for part in rel.parts)


def raw_key_order(text: str) -> list[str]:
    """Top-level keys of the frontmatter block in file order."""
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    block = text[3:end] if end != -1 else ""
    return [m.group(1) for m in re.finditer(r"^([A-Za-z_][\w-]*):", block, re.M)]


def check_actor_event(rep: Reporter, rel: str, field: str, event) -> None:
    if not isinstance(event, dict):
        rep.error(rel, f"{field} must be a mapping with by/at")
        return
    by, at = event.get("by"), event.get("at")
    if by is None or at is None:
        rep.error(rel, f"{field} requires both by and at")
        return
    if not isinstance(by, str) or not ACTOR_RE.match(by):
        rep.error(rel, f"{field}.by {by!r} is not a valid OKF actor (human:<id>, process:<path> or <org>/<model>)")
    if parse_iso(at) is None:
        rep.error(rel, f"{field}.at {at!r} is not an ISO-8601 string (quote it in YAML)")


def check_page(rep: Reporter, rel: str, meta: dict, text: str, profile: dict, canonical: str, is_root: bool, is_log: bool) -> None:
    allowed = BASE_KEYS | profile["extra_keys"]
    unknown = [k for k in meta if k not in allowed]
    if unknown:
        rep.warn(rel, f"unknown frontmatter keys {unknown} (consumers must tolerate them, but check for typos)")
    if "okf_version" in meta and not is_root:
        rep.error(rel, "okf_version belongs on the bundle root index.md only (§12)")

    order = raw_key_order(text)
    known = [k for k in order if k in KEY_ORDER]
    if known != sorted(known, key=KEY_ORDER.index):
        rep.warn(rel, f"frontmatter keys are not in the canonical order: {order}")
    if is_root and order and order[0] != "okf_version":
        rep.error(rel, 'bundle root index.md must declare okf_version: "0.2" as its first key')

    okf_type = meta.get("type")
    if not isinstance(okf_type, str) or not okf_type.strip():
        rep.error(rel, "frontmatter must contain a non-empty 'type'")
    elif okf_type not in profile["types"]:
        rep.error(rel, f"type {okf_type!r} not in this bundle's taxonomy {sorted(profile['types'])}")

    title = meta.get("title")
    if not isinstance(title, str) or not title.strip():
        rep.error(rel, "missing 'title'")
    elif SHORTCODE_RE.search(title):
        rep.error(rel, "title must not contain icon shortcodes")

    desc = meta.get("description")
    if not isinstance(desc, str) or not desc.strip():
        rep.error(rel, "missing 'description'")
    else:
        d = " ".join(desc.split())
        if len(d) > 300:
            rep.warn(rel, f"description is {len(d)} chars (>300)")
        elif len(d) < 50:
            rep.warn(rel, f"description is {len(d)} chars (<50); say what the page covers")
        if "](" in d or SHORTCODE_RE.search(d) or "`" in d:
            rep.warn(rel, "description should be plain text (no markdown/shortcodes)")
        unsafe = [c for c in '"<>' if c in d]
        if unsafe:
            rep.error(rel, f"description contains attribute-breaking characters: {unsafe} (MiniJinja autoescape is off)")

    if meta.get("resource") != canonical:
        rep.error(rel, f"resource {meta.get('resource')!r} != canonical {canonical!r}")

    tags = meta.get("tags")
    if not is_log:
        if not isinstance(tags, list) or not tags or not all(isinstance(t, str) for t in tags):
            rep.error(rel, "tags must be a non-empty list of strings")
        else:
            unknown_tags = [t for t in tags if t not in TAGS]
            if unknown_tags:
                rep.warn(rel, f"tags not in vocabulary: {unknown_tags}")
            if not 2 <= len(tags) <= 6:
                rep.warn(rel, f"{len(tags)} tags; the convention is 2-6")
            if len(set(tags)) != len(tags):
                rep.warn(rel, "duplicate tags")
    elif tags is not None and not isinstance(tags, list):
        rep.error(rel, "tags must be a list")

    sources = meta.get("sources")
    if sources is not None:
        if not isinstance(sources, list) or not sources:
            rep.error(rel, "sources, when present, must be a non-empty list")
        else:
            for i, src in enumerate(sources):
                if not isinstance(src, dict) or not isinstance(src.get("resource"), str):
                    rep.error(rel, f"sources[{i}] must be a mapping with a 'resource'")
                    continue
                if not re.match(r"^https?://", src["resource"]):
                    rep.error(rel, f"sources[{i}].resource must be an http(s) URL")
                lm = src.get("last_modified")
                if lm is not None and parse_iso(lm) is None:
                    rep.error(rel, f"sources[{i}].last_modified is not ISO-8601")

    if not is_log:
        generated = meta.get("generated")
        if generated is None:
            rep.error(rel, "missing 'generated'")
        else:
            check_actor_event(rep, rel, "generated", generated)
        verified = meta.get("verified")
        if verified is not None:
            if not isinstance(verified, list) or not verified:
                rep.error(rel, "verified, when present, must be a non-empty list")
            else:
                for i, event in enumerate(verified):
                    check_actor_event(rep, rel, f"verified[{i}]", event)
        status = meta.get("status")
        if status not in STATUS:
            rep.error(rel, f"status {status!r} must be one of {sorted(STATUS)}")

    stale = meta.get("stale_after")
    if stale is not None:
        dt = parse_iso(stale)
        if dt is None:
            rep.error(rel, "stale_after is not an ISO-8601 string")
        elif dt.tzinfo and dt < datetime.now(timezone.utc):
            rep.warn(rel, f"page is stale (stale_after {stale})")

    authors = meta.get("authors")
    if authors is not None:
        if not isinstance(authors, list) or not authors:
            rep.error(rel, "authors, when present, must be a non-empty list")
        else:
            for i, a in enumerate(authors):
                if not isinstance(a, dict) or not isinstance(a.get("name"), str):
                    rep.error(rel, f"authors[{i}] must be a mapping with a 'name'")
                    continue
                orcid = a.get("orcid")
                if orcid is not None and (not isinstance(orcid, str) or not ORCID_RE.match(orcid)):
                    rep.error(rel, f"authors[{i}].orcid {orcid!r} must look like https://orcid.org/0000-0000-0000-0000")
    for key in ("paper", "citation", "notebook"):
        if key in meta and not isinstance(meta[key], dict):
            rep.error(rel, f"{key} must be a mapping")
    cp = meta.get("companion_page")
    if cp is not None and (not isinstance(cp, str) or not re.match(r"^https?://", cp)):
        rep.warn(rel, "companion_page should be an absolute http(s) URL")
    vs = meta.get("verification_status")
    if vs is not None and vs not in VERIFICATION_STATUS:
        rep.error(rel, f"verification_status {vs!r} must be one of {sorted(VERIFICATION_STATUS)}")
    hd = meta.get("hausdorff_dim_range")
    if hd is not None and not (isinstance(hd, list) and len(hd) == 2 and all(isinstance(x, (int, float)) for x in hd)):
        rep.error(rel, "hausdorff_dim_range must be a two-number list [lo, hi]")


def check_links(rep: Reporter, bundle: Path, rel: str, body: str, profile_name: str) -> list[str]:
    """Warn on unresolvable .md link targets; return the resolved bundle-relative targets."""
    resolved_targets: list[str] = []
    path = bundle / rel
    for lineno, target in iter_link_targets(body):
        if target.startswith(("http://", "https://", "mailto:", "tel:", "data:", "//")) or target.startswith("#"):
            continue
        tpath, _ = split_target(target)
        if not tpath:
            continue
        if tpath.startswith("/"):
            rep.warn(f"{rel}:{lineno}", f"root-absolute link {target!r} breaks under the /fractal-notebooks/ sub-path; make it relative")
            continue
        if not (tpath.endswith(".md") or tpath.endswith("/")):
            continue  # images and other assets are checked by check_site.py on the built output
        dest = (path.parent / tpath).resolve()
        if tpath.endswith("/"):
            dest = dest / "index.md"
        try:
            inside = dest.relative_to(bundle.resolve()).as_posix()
        except ValueError:
            inside = None
        if not dest.exists():
            rep.warn(f"{rel}:{lineno}", f"broken internal link: {target}")
            continue
        if inside is not None:
            resolved_targets.append(inside)
    return resolved_targets


def check_log_body(rep: Reporter, rel: str, body: str) -> None:
    dates: list[str] = []
    for line in body.splitlines():
        s = line.strip()
        m = LOG_HEADING_RE.match(s)
        if s.startswith("## "):
            if not m:
                rep.error(rel, f"log heading {s!r} is not ISO 8601 `## YYYY-MM-DD` (§9)")
            else:
                dates.append(m.group(1))
        elif s.startswith(("- ", "* ")) and not LOG_CONVENTION_RE.search(s):
            rep.warn(rel, f"bullet without **Creation**/**Update**/**Deprecation**: {s[:60]}")
    if dates != sorted(dates, reverse=True):
        rep.error(rel, "date headings must be strictly newest-first")


def validate(bundle: Path, profile_name: str, site_url: str, resource_prefix: str, excludes: list[str], cfg: dict | None, strict: bool, warn_unverified: bool = False) -> tuple[Reporter, Counter, int]:
    profile = PROFILES[profile_name]
    rep = Reporter()
    base = site_url.rstrip("/") + ("/" + resource_prefix.strip("/") if resource_prefix.strip("/") else "")
    user_spec = pathspec.GitIgnoreSpec.from_lines(excludes)
    cfg_spec = exclude_spec(cfg) if (cfg and profile_name == "docs") else None

    pages: dict[str, tuple[dict | None, str, str]] = {}  # rel -> (meta, body, text)
    for path in sorted(bundle.rglob("*.md")):
        rel_path = path.relative_to(bundle)
        rel = rel_path.as_posix()
        if is_junk(rel_path) or user_spec.match_file(rel) or (cfg_spec and is_excluded(cfg_spec, rel)):
            continue
        text = path.read_text(encoding="utf-8")
        try:
            meta, body = split_frontmatter(text)
        except ValueError as e:
            rep.error(rel, str(e))
            continue
        pages[rel] = (meta, body, text)

    titles: dict[str, str] = {}
    types: Counter = Counter()
    unverified = 0
    index_targets: dict[str, list[str]] = {}
    for rel, (meta, body, text) in pages.items():
        name = posixpath.basename(rel)
        is_root = rel == "index.md"
        is_index = name == "index.md"
        is_log = name == "log.md"
        canonical = html_url(base, rel)

        if profile["typed_reserved"] or not (is_index or is_log):
            if meta is None:
                rep.error(rel, "missing YAML frontmatter block")
            elif not meta:
                rep.error(rel, "empty frontmatter block")
            else:
                check_page(rep, rel, meta, text, profile, canonical, is_root, is_log)
                types[str(meta.get("type"))] += 1
                t = meta.get("title")
                if isinstance(t, str) and t.strip():
                    key = t.strip().lower()
                    if key in titles:
                        rep.error(rel, f"title {t!r} duplicates {titles[key]} (titles must be unique across the bundle)")
                    else:
                        titles[key] = rel
                if not is_log and not meta.get("verified"):
                    unverified += 1
                    if warn_unverified:
                        rep.warn(rel, "no verified[] entry (unverified trust tier)")
            if is_root and meta is not None and meta.get("okf_version") != OKF_VERSION:
                rep.error(rel, f'bundle root must declare okf_version: "{OKF_VERSION}"')
        else:  # spec-pure exchange bundle reserved files
            if is_root:
                if meta is None:
                    rep.error(rel, f'bundle root index.md must declare okf_version: "{OKF_VERSION}" (§12)')
                elif set(meta) != {"okf_version"} or meta.get("okf_version") != OKF_VERSION:
                    rep.error(rel, f'root index.md frontmatter must be exactly okf_version: "{OKF_VERSION}", got {sorted(meta)}')
            elif meta is not None:
                rep.error(rel, f"{name} must not contain frontmatter in an exchange bundle (§8/§9)")

        if is_log:
            check_log_body(rep, rel, body)
        targets = check_links(rep, bundle, rel, body, profile_name)
        if is_index:
            index_targets[rel] = targets

    # Transitive index coverage: root index -> section indexes -> pages.
    if "index.md" in pages:
        reached: set[str] = set()
        frontier = ["index.md"]
        while frontier:
            cur = frontier.pop()
            for t in index_targets.get(cur, []):
                if t in reached:
                    continue
                reached.add(t)
                if posixpath.basename(t) == "index.md":
                    frontier.append(t)
        for rel in sorted(pages):
            if rel == "index.md" or posixpath.basename(rel) == "log.md":
                continue
            if rel not in reached:
                msg = f"not reachable from index.md through index pages: {rel}"
                (rep.error if strict else rep.warn)("index.md", msg)
    else:
        rep.error("index.md", "bundle root index.md is missing")

    return rep, types, unverified


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bundle", nargs="?", default="docs", help="bundle root directory (default: docs)")
    ap.add_argument("--profile", choices=sorted(PROFILES), default=None, help="docs (default for docs/), concept, proof")
    ap.add_argument("--site-url", default=None, help="site URL (default: zensical.toml site_url)")
    ap.add_argument("--resource-prefix", default=None, help="URL path of the bundle under the site (default per profile)")
    ap.add_argument("--exclude", action="append", default=[], metavar="PATTERN", help="gitignore-style pattern relative to the bundle (repeatable)")
    ap.add_argument("--config", default=None, help="zensical.toml (for site_url and, in the docs profile, exclude_docs)")
    ap.add_argument("--strict", action="store_true", help="treat warnings (and uncovered pages) as errors")
    ap.add_argument("--warn-unverified", action="store_true", help="warn on every page without a verified[] entry")
    args = ap.parse_args(argv)

    bundle = Path(args.bundle)
    if not bundle.is_dir():
        print(f"{bundle}: [ERROR] not a directory")
        return 2
    profile_name = args.profile or ("docs" if bundle.resolve().name == "docs" else None)
    if profile_name is None:
        n = bundle.resolve().name
        profile_name = "concept" if n == "concepts" else "proof" if n == "proofs" else "docs"

    cfg = None
    if args.config is not None or (ROOT / "zensical.toml").is_file():
        try:
            cfg = load_config(ROOT, args.config)
        except ConfigError as e:
            if args.site_url is None or args.config is not None:
                print(f"[ERROR] {e}")
                return 2
    site_url = args.site_url or (cfg or {}).get("site_url")
    if not site_url:
        print("[ERROR] no site URL: pass --site-url or provide zensical.toml (--config)")
        return 2
    prefix = args.resource_prefix if args.resource_prefix is not None else PROFILES[profile_name]["resource_prefix"]

    rep, types, unverified = validate(bundle, profile_name, site_url, prefix, args.exclude, cfg, args.strict, args.warn_unverified)
    for line in rep.lines:
        print(line)
    counts = ", ".join(f"{k}={v}" for k, v in sorted(types.items()))
    total = sum(types.values())
    print(f"Checked {total} typed pages in {bundle} ({profile_name} profile): {rep.errors} error(s), {rep.warnings} warning(s); {unverified} without verified[]")
    print(f"type counts: {counts or 'none'}")
    if rep.errors or (args.strict and rep.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
