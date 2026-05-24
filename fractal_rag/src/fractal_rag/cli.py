"""Click-based entrypoint for the fractal-rag command line."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from .client import client_session
from .concepts.loader import load_seed
from .config import get_settings
from .schema import bootstrap


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
    """Create FractalArtifact and Concept collections if missing."""
    with client_session() as client:
        result = bootstrap(client, drop_existing=drop)
    click.echo(json.dumps({
        "created": result.created,
        "already_present": result.already_present,
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
    """Run the MCP server on stdio transport (Phase F)."""
    click.echo("[stub] serve — implemented in Phase F", err=True)
    sys.exit(2)


@main.command()
@click.argument("query")
@click.option("--limit", default=5)
def query(query: str, limit: int) -> None:
    """Quick CLI for a hybrid search against content_vec."""
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
