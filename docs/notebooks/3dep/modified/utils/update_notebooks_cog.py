#!/usr/bin/env python
"""
Batch update CHM notebooks to add COG support.

This script modifies all chm_*.ipynb notebooks in the sites/ directory
to add Cloud Optimized GeoTIFF conversion, validation, and thumbnail generation.

Usage:
    python update_notebooks_cog.py [--dry-run]
"""

import json
import sys
from pathlib import Path


# New imports to add to cell-3
COG_IMPORTS = """
# COG utilities
import subprocess
from osgeo import gdal
from rio_cogeo.cogeo import cog_validate"""


# New cells to insert after metadata cell
COG_MARKDOWN_CELL = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 11.5 Convert to Cloud Optimized GeoTIFFs (COG)\n",
        "\n",
        "Convert all output TIFs to COG format with internal overviews for efficient streaming and web access."
    ]
}

COG_CONVERT_CELL = {
    "cell_type": "code",
    "metadata": {},
    "outputs": [],
    "execution_count": None,
    "source": [
        "# === Convert to Cloud Optimized GeoTIFFs ===\n",
        "\n",
        "def convert_to_cog(input_path, compress=\"LZW\", overview_resampling=\"AVERAGE\"):\n",
        "    \"\"\"Convert GeoTIFF to COG with internal overviews using GDAL.\n",
        "    \n",
        "    Args:\n",
        "        input_path: Path to input GeoTIFF\n",
        "        compress: Compression method (LZW, DEFLATE, ZSTD)\n",
        "        overview_resampling: Resampling for overviews (AVERAGE, NEAREST, etc.)\n",
        "        \n",
        "    Returns:\n",
        "        Path to converted COG (same as input - in-place conversion)\n",
        "    \"\"\"\n",
        "    from pathlib import Path\n",
        "    input_path = Path(input_path)\n",
        "    temp_path = input_path.with_suffix('.tmp.tif')\n",
        "\n",
        "    cmd = [\n",
        "        \"gdal_translate\",\n",
        "        \"-of\", \"COG\",\n",
        "        \"-co\", f\"COMPRESS={compress}\",\n",
        "        \"-co\", \"PREDICTOR=2\",\n",
        "        \"-co\", \"BLOCKSIZE=512\",\n",
        "        \"-co\", f\"OVERVIEW_RESAMPLING={overview_resampling}\",\n",
        "        \"-co\", \"BIGTIFF=IF_SAFER\",\n",
        "        str(input_path),\n",
        "        str(temp_path)\n",
        "    ]\n",
        "\n",
        "    result = subprocess.run(cmd, check=True, capture_output=True, text=True)\n",
        "    shutil.move(str(temp_path), str(input_path))\n",
        "    return input_path\n",
        "\n",
        "print(\"Converting outputs to Cloud Optimized GeoTIFFs...\")\n",
        "print(\"-\" * 50)\n",
        "\n",
        "tif_outputs = [\n",
        "    (\"CHM\", chm_path),\n",
        "    (\"DEM\", dem_path),\n",
        "    (\"DSM\", dsm_path),\n",
        "    (\"DTM\", dtm_path),\n",
        "]\n",
        "\n",
        "for name, tif_path in tif_outputs:\n",
        "    if tif_path.exists():\n",
        "        print(f\"  Converting {name}: {tif_path.name}...\", end=\" \", flush=True)\n",
        "        try:\n",
        "            convert_to_cog(tif_path)\n",
        "            print(\"done\")\n",
        "        except Exception as e:\n",
        "            print(f\"FAILED: {e}\")\n",
        "\n",
        "print(\"-\" * 50)\n",
        "print(\"COG conversion complete!\")"
    ]
}

COG_VALIDATE_CELL = {
    "cell_type": "code",
    "metadata": {},
    "outputs": [],
    "execution_count": None,
    "source": [
        "# === Validate COG Files ===\n",
        "print(\"Validating COG compliance...\")\n",
        "print(\"-\" * 50)\n",
        "\n",
        "for name, tif_path in tif_outputs:\n",
        "    if tif_path.exists():\n",
        "        is_cog, errors, warnings = cog_validate(str(tif_path))\n",
        "        \n",
        "        # Get overview count\n",
        "        ds = gdal.Open(str(tif_path))\n",
        "        overview_count = ds.GetRasterBand(1).GetOverviewCount()\n",
        "        ds = None\n",
        "        \n",
        "        status = \"VALID\" if is_cog else \"INVALID\"\n",
        "        print(f\"  [{status}] {name}: {tif_path.name} ({overview_count} overviews)\")\n",
        "        \n",
        "        for w in warnings:\n",
        "            print(f\"         WARNING: {w}\")\n",
        "        for e in errors:\n",
        "            print(f\"         ERROR: {e}\")\n",
        "\n",
        "print(\"-\" * 50)\n",
        "print(\"Validation complete!\")"
    ]
}

COG_THUMBNAIL_CELL = {
    "cell_type": "code",
    "metadata": {},
    "outputs": [],
    "execution_count": None,
    "source": [
        "# === Generate Thumbnails ===\n",
        "import rasterio\n",
        "\n",
        "def create_thumbnail(input_tif, output_png, max_size=512, cmap='Greens'):\n",
        "    \"\"\"Create thumbnail PNG from GeoTIFF using rasterio and matplotlib.\"\"\"\n",
        "    with rasterio.open(input_tif) as src:\n",
        "        scale = max_size / max(src.height, src.width)\n",
        "        new_width = int(src.width * scale)\n",
        "        new_height = int(src.height * scale)\n",
        "\n",
        "        data = src.read(1, out_shape=(new_height, new_width), resampling=Resampling.bilinear)\n",
        "        if src.nodata is not None:\n",
        "            data = np.ma.masked_equal(data, src.nodata)\n",
        "\n",
        "    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)\n",
        "    valid_data = data.compressed() if hasattr(data, 'compressed') else data[~np.isnan(data)]\n",
        "    if len(valid_data) > 0:\n",
        "        vmin, vmax = np.percentile(valid_data, [2, 98])\n",
        "    else:\n",
        "        vmin, vmax = 0, 1\n",
        "    im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)\n",
        "    ax.axis('off')\n",
        "    plt.colorbar(im, ax=ax, shrink=0.8, label='Height (m)')\n",
        "    plt.tight_layout()\n",
        "    plt.savefig(output_png, dpi=100, bbox_inches='tight', facecolor='white')\n",
        "    plt.close()\n",
        "    return output_png\n",
        "\n",
        "print(\"Generating thumbnails...\")\n",
        "\n",
        "# CHM thumbnail\n",
        "chm_thumb = LOCAL_OUTPUT_CHM / f\"{SITE_NAME}_chm_thumb.png\"\n",
        "create_thumbnail(chm_path, chm_thumb, cmap='Greens')\n",
        "print(f\"  CHM: {chm_thumb.name}\")\n",
        "\n",
        "# DEM thumbnail\n",
        "dem_thumb = LOCAL_OUTPUT_CHM / f\"{SITE_NAME}_dem_thumb.png\"\n",
        "create_thumbnail(dem_path, dem_thumb, cmap='terrain')\n",
        "print(f\"  DEM: {dem_thumb.name}\")\n",
        "\n",
        "print(\"Thumbnails complete!\")"
    ]
}

COG_METADATA_UPDATE_CELL = {
    "cell_type": "code",
    "metadata": {},
    "outputs": [],
    "execution_count": None,
    "source": [
        "# === Update Metadata with COG Info ===\n",
        "def get_cog_metadata(tif_path):\n",
        "    \"\"\"Get COG-specific metadata.\"\"\"\n",
        "    is_cog, errors, warnings = cog_validate(str(tif_path))\n",
        "    ds = gdal.Open(str(tif_path))\n",
        "    overview_count = ds.GetRasterBand(1).GetOverviewCount()\n",
        "    ds = None\n",
        "    \n",
        "    return {\n",
        "        \"is_cog\": is_cog,\n",
        "        \"overview_count\": overview_count,\n",
        "        \"file_size_mb\": round(tif_path.stat().st_size / 1e6, 2),\n",
        "        \"cog_warnings\": warnings,\n",
        "        \"cog_errors\": errors\n",
        "    }\n",
        "\n",
        "# Add COG info to metadata\n",
        "stats['cog_outputs'] = {\n",
        "    'chm': get_cog_metadata(chm_path) if chm_path.exists() else None,\n",
        "    'dem': get_cog_metadata(dem_path) if dem_path.exists() else None,\n",
        "    'dsm': get_cog_metadata(dsm_path) if dsm_path.exists() else None,\n",
        "    'dtm': get_cog_metadata(dtm_path) if dtm_path.exists() else None,\n",
        "}\n",
        "\n",
        "stats['thumbnails'] = {\n",
        "    'chm': str(chm_thumb),\n",
        "    'dem': str(dem_thumb)\n",
        "}\n",
        "\n",
        "# Re-save metadata with COG info\n",
        "with open(metadata_path, 'w') as f:\n",
        "    json.dump(stats, f, indent=2)\n",
        "\n",
        "print(f\"Metadata updated with COG info: {metadata_path.name}\")"
    ]
}


def find_cell_index(cells, search_text):
    """Find cell index containing specific text."""
    for i, cell in enumerate(cells):
        source = cell.get("source", [])
        if isinstance(source, list):
            source_text = "".join(source)
        else:
            source_text = source
        if search_text in source_text:
            return i
    return -1


def update_notebook(notebook_path, dry_run=False):
    """Update a single notebook with COG support."""

    with open(notebook_path, 'r') as f:
        nb = json.load(f)

    cells = nb.get("cells", [])

    # Find import cell (cell with "import json")
    import_idx = find_cell_index(cells, "import json")
    if import_idx == -1:
        print(f"  ERROR: Could not find import cell")
        return False

    # Check if already updated
    if find_cell_index(cells, "rio_cogeo.cogeo import cog_validate") != -1:
        print(f"  Already updated (COG imports found)")
        return True

    # Add COG imports to import cell
    import_cell = cells[import_idx]
    source = import_cell.get("source", [])
    if isinstance(source, list):
        source_text = "".join(source)
    else:
        source_text = source

    # Add imports at end
    source_text = source_text.rstrip() + "\n" + COG_IMPORTS
    cells[import_idx]["source"] = source_text

    # Find metadata save cell (cell with "metadata_path =")
    metadata_idx = find_cell_index(cells, "metadata_path =")
    if metadata_idx == -1:
        print(f"  ERROR: Could not find metadata cell")
        return False

    # Insert COG cells after metadata cell
    insert_idx = metadata_idx + 1
    new_cells = [
        COG_MARKDOWN_CELL,
        COG_CONVERT_CELL,
        COG_VALIDATE_CELL,
        COG_THUMBNAIL_CELL,
        COG_METADATA_UPDATE_CELL,
    ]

    for i, cell in enumerate(new_cells):
        cells.insert(insert_idx + i, cell.copy())

    # Find copy files cell and add thumbnails
    copy_idx = find_cell_index(cells, "files_to_copy = [")
    if copy_idx != -1:
        copy_cell = cells[copy_idx]
        source = copy_cell.get("source", [])
        if isinstance(source, list):
            source_text = "".join(source)
        else:
            source_text = source

        # Add thumbnail entries before the closing bracket
        if "(chm_thumb," not in source_text:
            source_text = source_text.replace(
                "    (preview_path, DATASTORE_CHM / preview_path.name),\n]",
                "    (preview_path, DATASTORE_CHM / preview_path.name),\n"
                "    (chm_thumb, DATASTORE_CHM / chm_thumb.name),\n"
                "    (dem_thumb, DATASTORE_CHM / dem_thumb.name),\n]"
            )
            cells[copy_idx]["source"] = source_text

    nb["cells"] = cells

    if not dry_run:
        with open(notebook_path, 'w') as f:
            json.dump(nb, f, indent=1)

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Update CHM notebooks with COG support")
    parser.add_argument("--dry-run", action="store_true", help="Don't write changes")
    args = parser.parse_args()

    # Find all CHM notebooks
    sites_dir = Path(__file__).parent.parent / "sites"
    notebooks = sorted(sites_dir.glob("*/chm_*.ipynb"))

    # Filter out checkpoint files
    notebooks = [nb for nb in notebooks if ".ipynb_checkpoints" not in str(nb)]

    print(f"Found {len(notebooks)} CHM notebooks to update")
    print("=" * 60)

    if args.dry_run:
        print("DRY RUN - no changes will be written")
        print("=" * 60)

    success = 0
    failed = 0

    for nb_path in notebooks:
        print(f"\nProcessing: {nb_path.parent.name}/{nb_path.name}")
        try:
            if update_notebook(nb_path, dry_run=args.dry_run):
                success += 1
                print(f"  SUCCESS")
            else:
                failed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"COMPLETE: {success} succeeded, {failed} failed")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
