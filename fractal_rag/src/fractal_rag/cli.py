"""Click-based entrypoint for the fractal-rag command line."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from .concepts.loader import load_seed
from .config import get_settings

# NOTE: `.client` / `.schema` import weaviate, which is only needed for the
# Weaviate-backed commands. Import them lazily inside those commands so that
# `fractal-rag okf export`, `concepts list/validate`, and `--help` work without
# a weaviate install.


@click.group()
@click.version_option(package_name="fractal-rag")
def main() -> None:
    """Fractal RAG ingestion and MCP server."""


@main.group()
def schema() -> None:
    """Schema management commands."""


@schema.command("bootstrap")
@click.option("--drop", is_flag=True, help="Delete existing collections first (destructive).")
def schema_bootstrap(drop: bool) -> None:
    """Create FractalArtifact and Concept collections if missing.

    Existing collections are kept and gain any property the current schema declares
    that they lack (e.g. `resource`); re-run `fractal-rag ingest` afterwards to fill it.
    """
    from .client import client_session
    from .schema import bootstrap

    with client_session() as client:
        result = bootstrap(client, drop_existing=drop)
    click.echo(json.dumps({
        "created": result.created,
        "already_present": result.already_present,
        "properties_added": result.properties_added,
    }, indent=2))


@main.group()
def concepts() -> None:
    """Concept seed inspection commands."""


@concepts.command("list")
def concepts_list() -> None:
    """List seeded concept names."""
    records = load_seed()
    for r in records:
        click.echo(f"{r.name}  ({len(r.aliases)} aliases)")
    click.echo(f"\nTotal: {len(records)} concepts")


@concepts.command("validate")
def concepts_validate() -> None:
    """Validate the seed YAML loads without error."""
    records = load_seed()
    click.echo(f"OK: {len(records)} concepts validated")


@main.group()
def okf() -> None:
    """Open Knowledge Format (OKF v0.2) bundle commands."""


@okf.command("export")
@click.option(
    "--seed",
    type=click.Path(path_type=Path, dir_okay=False),
    default=None,
    help="Concept seed YAML (default: the packaged concepts/seed.yaml).",
)
@click.option(
    "--out",
    type=click.Path(path_type=Path),
    default=Path("okf/concepts"),
    help="Bundle directory (default: okf/concepts, relative to the current directory).",
)
@click.option(
    "--date", default=None, help="ISO date stamped on new or changed concepts (default: today)."
)
@click.option(
    "--site-url",
    default=None,
    help="Published site root used for `resource` and source URLs.",
)
@click.option(
    "--check",
    is_flag=True,
    help="Write nothing; exit 1 if the bundle on disk differs from the seed.",
)
@click.option(
    "--prune-unknown",
    is_flag=True,
    help=(
        "Also delete Markdown files under --out that the exporter did not generate "
        "(by default their presence makes the run refuse with exit code 2; log.md files "
        "are never deleted)."
    ),
)
def okf_export(
    seed: Path | None,
    out: Path,
    date: str | None,
    site_url: str | None,
    check: bool,
    prune_unknown: bool,
) -> None:
    """Generate the OKF v0.2 concept bundle from concepts/seed.yaml.

    The seed YAML is the authoring source of truth; the bundle under okf/concepts
    is a generated, committed artifact. Re-run after editing the seed and commit
    the result (CI runs --check and fails on drift). Only files the exporter
    generated are ever deleted; any other Markdown file under --out makes the run
    refuse unless --prune-unknown is given. Behaves exactly like
    `python -m fractal_rag.okf_export`.
    """
    from .okf_export import DEFAULT_SEED, SITE_URL, run

    code, message = run(
        seed or DEFAULT_SEED, out, date, site_url or SITE_URL, check, prune_unknown=prune_unknown
    )
    click.echo(message)
    if code:
        sys.exit(code)


@main.command()
@click.option(
    "--source",
    type=click.Choice(["json", "notebooks", "docs", "pdfs", "all"]),
    default="all",
)
@click.option("--limit", type=int, default=None, help="Cap docs per source (for smoke tests).")
@click.option("--dry-run", is_flag=True, help="Don't touch Weaviate; print would-be totals.")
def ingest(source: str, limit: int | None, dry_run: bool) -> None:
    """Parse, chunk, enrich, and batch-import the corpus."""
    from .client import client_session
    from .ingest import DryRunWriter, WeaviateWriter, run_ingest

    sources = ["json", "notebooks", "docs", "pdfs"] if source == "all" else [source]

    if dry_run:
        writer = DryRunWriter()
        report = run_ingest(sources, writer, limit_per_source=limit)
        click.echo(
            json.dumps(
                {
                    "dry_run": True,
                    "concepts": len(writer.concepts),
                    "artifacts": len(writer.artifacts),
                    "report": report.to_dict(),
                },
                indent=2,
            )
        )
        return

    with client_session() as client:
        writer = WeaviateWriter(client)
        report = run_ingest(sources, writer, limit_per_source=limit)
    click.echo(json.dumps(report.to_dict(), indent=2))


@main.command("pull")
@click.option("--force", is_flag=True, help="Re-download files even if checksum matches.")
@click.option("--dry-run", is_flag=True, help="Print the gocmd command without running it.")
def pull_cmd(force: bool, dry_run: bool) -> None:
    """Pull the corpus from iRODS using gocmd."""
    from .pull import pull as do_pull

    result = do_pull(force=force, dry_run=dry_run)
    click.echo(
        json.dumps(
            {
                "irods_root": result.irods_root,
                "local_root": str(result.local_root),
                "returncode": result.returncode,
            },
            indent=2,
        )
    )


@main.command()
def status() -> None:
    """Show collection object counts."""
    from .client import client_session

    settings = get_settings()
    with client_session(settings) as client:
        counts = {}
        for name in (settings.artifact_collection, settings.concept_collection):
            if client.collections.exists(name):
                coll = client.collections.get(name)
                counts[name] = coll.aggregate.over_all(total_count=True).total_count
            else:
                counts[name] = None
    click.echo(json.dumps(counts, indent=2))


@main.command()
def serve() -> None:
    """Run the MCP server on stdio transport."""
    from .server.mcp import serve_stdio

    serve_stdio()


@main.command()
@click.argument("query")
@click.option("--limit", default=5)
def query(query: str, limit: int) -> None:
    """Quick CLI for a hybrid search against content_vec."""
    from .client import client_session

    settings = get_settings()
    with client_session(settings) as client:
        coll = client.collections.get(settings.artifact_collection)
        response = coll.query.hybrid(query=query, limit=limit, target_vector="content_vec")
        out = []
        for o in response.objects:
            out.append({
                "uuid": str(o.uuid),
                "title": o.properties.get("title"),
                "source_type": o.properties.get("source_type"),
                "source_uri": o.properties.get("source_uri"),
                "summary": o.properties.get("summary"),
            })
    click.echo(json.dumps(out, indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()
