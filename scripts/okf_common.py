"""Shared helpers for the OKF bundle, notebook-rendering and agent-surface scripts.

Every script in scripts/ reads site settings (site_name, site_description,
site_url, nav, exclude_docs, not_in_nav) from zensical.toml, so the same
scripts serve any Zensical + OKF v0.2 site without per-site edits.
Requires Python 3.11+ (tomllib).

URL conventions (use_directory_urls = true):

    docs/index.md          -> <site_url>/                 twin: <site_url>/index.md
    docs/a/index.md        -> <site_url>/a/               twin: <site_url>/a/index.md
    docs/a/b.md            -> <site_url>/a/b/             twin: <site_url>/a/b.md
"""

from __future__ import annotations

import posixpath
import re
import tomllib
from pathlib import Path
from typing import Iterator

import pathspec
import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# The bundle roots published through the site: docs/ itself plus the two
# exchange bundles that stage_okf.py copies to docs/okf/{concepts,proofs}.
BUNDLE_ROOTS = ("", "okf/concepts", "okf/proofs")

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"(`+)(?:.*?)\1")
# ](target) or ](target "title") — covers links, images, and nested badges
MD_LINK_RE = re.compile(r"(\]\()(<[^>]+>|[^)\s]+)((?:\s+\"[^\"]*\")?\))")
# [id]: target   (reference-style definitions)
REF_DEF_RE = re.compile(r"^(\s{0,3}\[[^\]]+\]:\s*)(\S+)")
# src="..." / href="..." in raw HTML
HTML_ATTR_RE = re.compile(r"(\b(?:src|href)=\")([^\"]+)(\")")

EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "data:", "//", "#")


class ConfigError(RuntimeError):
    """zensical.toml is missing or malformed."""


# --------------------------------------------------------------------------- config


def load_config(root: Path = ROOT, config_path: str | Path | None = None) -> dict:
    """Return the ``[project]`` table of zensical.toml.

    Raises ConfigError with an actionable message when the file is missing,
    unparseable, or lacks ``[project]``.
    """
    path = Path(config_path) if config_path else Path(root) / "zensical.toml"
    if not path.is_file():
        raise ConfigError(
            f"zensical.toml not found at {path}. Pass --config <path> or create the "
            "Zensical configuration first (see the migration plan)."
        )
    try:
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
    except tomllib.TOMLDecodeError as e:  # pragma: no cover - exercised manually
        raise ConfigError(f"{path}: invalid TOML: {e}") from e
    project = data.get("project")
    if not isinstance(project, dict):
        raise ConfigError(f"{path}: missing [project] table")
    project.setdefault("_config_path", str(path))
    return project


def site_url(cfg: dict) -> str:
    """Site URL with exactly one trailing slash (the ``base`` of page_url)."""
    return (cfg.get("site_url") or "/").rstrip("/") + "/"


def site_root(cfg: dict) -> str:
    """Site URL without a trailing slash (the argument of html_url/md_url)."""
    return (cfg.get("site_url") or "").rstrip("/")


def docs_dir(cfg: dict, root: Path = ROOT) -> Path:
    base = Path(cfg.get("_config_path", root / "zensical.toml")).resolve().parent
    return (base / cfg.get("docs_dir", "docs")).resolve()


def site_dir(cfg: dict, root: Path = ROOT) -> Path:
    base = Path(cfg.get("_config_path", root / "zensical.toml")).resolve().parent
    return (base / cfg.get("site_dir", "site")).resolve()


def _spec_from_setting(*values: str | None) -> pathspec.GitIgnoreSpec:
    lines: list[str] = []
    for value in values:
        if value:
            lines.extend(line for line in str(value).splitlines() if line.strip())
    return pathspec.GitIgnoreSpec.from_lines(lines)


def exclude_spec(cfg: dict) -> pathspec.GitIgnoreSpec:
    """gitignore-style matcher for ``exclude_docs`` + ``draft_docs`` (docs-relative paths)."""
    return _spec_from_setting(cfg.get("exclude_docs"), cfg.get("draft_docs"))


def not_in_nav_spec(cfg: dict) -> pathspec.GitIgnoreSpec:
    """gitignore-style matcher for ``not_in_nav`` (docs-relative paths)."""
    return _spec_from_setting(cfg.get("not_in_nav"))


def is_excluded(spec: pathspec.GitIgnoreSpec, rel: str) -> bool:
    """True when the docs-relative path (or any dot-directory component) is excluded.

    Zensical excludes dot-files and dot-directories by default, so they count as
    excluded even when no pattern names them.
    """
    rel = rel.replace("\\", "/")
    if any(part.startswith(".") for part in rel.split("/")):
        return True
    return spec.match_file(rel)


def redirect_maps(cfg: dict) -> dict[str, str]:
    plugins = cfg.get("plugins") or {}
    redirects = plugins.get("redirects") or {}
    maps = redirects.get("redirect_maps") or {}
    return {str(k): str(v) for k, v in maps.items()}


# ---------------------------------------------------------------------- frontmatter


def split_frontmatter(text: str) -> tuple[dict | None, str]:
    """Return (frontmatter dict or None if absent, body). Raises ValueError on bad YAML."""
    if not text.startswith("---"):
        return None, text
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        raise ValueError(f"unparseable YAML frontmatter: {e}") from e
    return (data if isinstance(data, dict) else {}), text[m.end():]


def frontmatter(path: Path) -> dict:
    try:
        fm, _ = split_frontmatter(path.read_text(encoding="utf-8"))
    except ValueError:
        return {}
    return fm or {}


def first_paragraph(body: str) -> str:
    """First prose paragraph of a Markdown body (skips headings, lists, fences, html)."""
    para: list[str] = []
    for _, line, in_code in iter_body_lines(body):
        if in_code:
            continue
        stripped = line.strip()
        if not stripped:
            if para:
                break
            continue
        if stripped.startswith(("#", "*", "-", "+", "|", "<", "!!!", "???", "---")) or re.match(
            r"^\d+\.\s", stripped
        ):
            if para:
                break
            continue
        para.append(stripped)
    return " ".join(para)


# ----------------------------------------------------------------------------- urls


def page_url(base: str, rel: str) -> str:
    """docs-relative .md path -> pretty URL (``base`` must end with '/')."""
    rel = rel.replace("\\", "/")
    if rel == "index.md":
        return base
    if rel.endswith("/index.md"):
        return base + rel[: -len("index.md")]
    if rel.endswith(".md"):
        return base + rel[: -len(".md")] + "/"
    return base + rel


def html_url(site_url_: str, rel: str) -> str:
    """docs-relative .md path -> canonical page URL (``site_url_`` has no trailing slash).

    index.md -> site/, X/index.md -> site/X/, a/b.md -> site/a/b/
    """
    return page_url(site_url_.rstrip("/") + "/", rel)


def md_url(site_url_: str, rel: str) -> str:
    """docs-relative source path -> URL of its verbatim Markdown twin."""
    return site_url_.rstrip("/") + "/" + rel.replace("\\", "/")


def url_to_source_candidates(url_path: str) -> list[str]:
    """Pretty URL path (relative to the site root, e.g. 'a/b/') -> candidate source paths.

    '' -> ['index.md']; 'a/b/' -> ['a/b.md', 'a/b/index.md'].
    """
    path = url_path.strip("/")
    if not path:
        return ["index.md"]
    return [f"{path}.md", f"{path}/index.md"]


def is_external(target: str) -> bool:
    return target.startswith(EXTERNAL_PREFIXES)


def nav_pages(nav: list, trail: tuple = ()) -> Iterator[tuple[tuple, str | None, str]]:
    """Walk a Zensical nav. Yields (section trail, label or None, target)
    where target is a docs-relative .md path or an external URL."""
    for item in nav:
        if isinstance(item, str):
            yield trail, None, item
        elif isinstance(item, dict):
            for label, value in item.items():
                if isinstance(value, str):
                    yield trail, label, value
                elif isinstance(value, list):
                    yield from nav_pages(value, trail + (label,))


def nav_targets(cfg: dict) -> list[str]:
    """Docs-relative .md paths referenced by the nav, in order, without duplicates."""
    seen: list[str] = []
    for _, _, target in nav_pages(cfg.get("nav", [])):
        if not is_external(target) and target not in seen:
            seen.append(target)
    return seen


# ----------------------------------------------------------------------------- body


def iter_body_lines(body: str) -> Iterator[tuple[int, str, bool]]:
    """Yield (line number, line, in_code) for a Markdown body."""
    fence = None
    for i, line in enumerate(body.splitlines(), 1):
        m = FENCE_RE.match(line)
        if m:
            marker = m.group(1)
            if fence is None:
                fence = marker
                yield i, line, True
                continue
            if marker == fence:
                fence = None
                yield i, line, True
                continue
        yield i, line, fence is not None


def _sub_outside_inline_code(line: str, fn) -> str:
    """Apply fn to the parts of a line that are not inside `inline code`."""
    out, pos = [], 0
    for m in INLINE_CODE_RE.finditer(line):
        out.append(fn(line[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(fn(line[pos:]))
    return "".join(out)


def rewrite_link_targets(body: str, fn) -> str:
    """Call fn(target) -> new target for every link/image/src/href target in
    the Markdown body, skipping fenced code and inline code."""

    def repl_md(m):
        raw = m.group(2)
        bracketed = raw.startswith("<") and raw.endswith(">")
        target = raw[1:-1] if bracketed else raw
        new = fn(target)
        if bracketed:
            new = f"<{new}>"
        return m.group(1) + new + m.group(3)

    def repl_ref(m):
        return m.group(1) + fn(m.group(2))

    def repl_html(m):
        return m.group(1) + fn(m.group(2)) + m.group(3)

    def fix(segment: str) -> str:
        segment = MD_LINK_RE.sub(repl_md, segment)
        return HTML_ATTR_RE.sub(repl_html, segment)

    lines = []
    for _, line, in_code in iter_body_lines(body):
        if in_code:
            lines.append(line)
            continue
        line = REF_DEF_RE.sub(repl_ref, line)
        lines.append(_sub_outside_inline_code(line, fix))
    out = "\n".join(lines)
    return out + ("\n" if body.endswith("\n") else "")


def iter_link_targets(body: str) -> Iterator[tuple[int, str]]:
    """Yield (line number, target) for every link target outside code."""
    for lineno, line, in_code in iter_body_lines(body):
        if in_code:
            continue
        m = REF_DEF_RE.match(line)
        if m:
            yield lineno, m.group(2)
        stripped = INLINE_CODE_RE.sub("", line)
        for m in MD_LINK_RE.finditer(stripped):
            t = m.group(2)
            yield lineno, (t[1:-1] if t.startswith("<") and t.endswith(">") else t)
        for m in HTML_ATTR_RE.finditer(stripped):
            yield lineno, m.group(2)


def split_target(target: str) -> tuple[str, str]:
    """'a/b.md#frag' -> ('a/b.md', '#frag'); keeps ?query with the suffix."""
    for sep in ("#", "?"):
        if sep in target:
            idx = target.index(sep)
            return target[:idx], target[idx:]
    return target, ""


def absolutize(target: str, src_rel: str, base: str) -> str:
    """Resolve a relative link in docs/<src_rel> to an absolute site URL."""
    if not target or is_external(target) or target.startswith("/"):
        return target
    path, suffix = split_target(target)
    if not path:
        return target
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(src_rel), path))
    if resolved.startswith(".."):
        return target
    if resolved.endswith(".md"):
        return page_url(base, resolved) + suffix
    return base + resolved + suffix


def slugify(value: str) -> str:
    """Python-Markdown toc default slugify (what Zensical uses for heading ids)."""
    import unicodedata

    value = re.sub(r":[a-z0-9]+(?:-[a-z0-9]+)+:", "", value)  # icon shortcodes
    value = re.sub(r"\{[^}]*\}\s*$", "", value)  # trailing attr_list
    value = re.sub(r"<[^>]+>", "", value)  # inline HTML
    value = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", value)  # links -> text
    value = re.sub(r"[`*_~]", "", value)
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)
