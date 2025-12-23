# Cloud Optimized GeoTIFF (COG) Implementation Plan

## Overview

This plan documents the changes needed to update all 3DEP notebooks to produce Cloud Optimized GeoTIFFs (COGs) with internal overviews and thumbnails, using GDAL instead of rasterio for COG creation.

## Current State

### TIF Generation Points

1. **PDAL `writers.gdal` stage** (DSM/DTM):
   - Function: `make_dem_pipeline()`
   - Options: `"gdalopts": "COMPRESS=LZW,TILED=YES,BLOCKXSIZE=256,BLOCKYSIZE=256"`
   - Files: `{site}_dsm.tif`, `{site}_dtm.tif`

2. **rioxarray `rio.to_raster()`** (CHM/DEM):
   - Call: `chm.rio.to_raster(chm_path, driver="GTiff", compress="LZW", tiled=True)`
   - Files: `{site}_chm.tif`, `{site}_dem.tif`

### Notebooks Requiring Updates

- **Main template**: `2_chm_user_aoi.ipynb`
- **19 site notebooks**: `sites/*/chm_*.ipynb`
  - `great_smoky_cove/chm_great_smoky_cove.ipynb`
  - `olympic_hoh/chm_olympic_hoh.ipynb`
  - `redwood_humboldt/chm_redwood_humboldt.ipynb`
  - `rocky_mountain_subalpine/chm_rocky_mountain_subalpine.ipynb`
  - `sequoia_giant_forest/chm_sequoia_giant_forest.ipynb`
  - `shenandoah_limberlost/chm_shenandoah_limberlost.ipynb`
  - `sitka_spruce_coastal/chm_sitka_spruce_coastal.ipynb`
  - `superior_old_growth/chm_superior_old_growth.ipynb`
  - `tahoe_old_growth/chm_tahoe_old_growth.ipynb`
  - `tongass_mendenhall/chm_tongass_mendenhall.ipynb`
  - `white_mountain_northern/chm_white_mountain_northern.ipynb`
  - `yellowstone_lodgepole/chm_yellowstone_lodgepole.ipynb`
  - `adirondack_hemlock/chm_adirondack_hemlock.ipynb`
  - `big_thicket_floodplain/chm_big_thicket_floodplain.ipynb`
  - `black_hills_ponderosa/chm_black_hills_ponderosa.ipynb`
  - `cades_cove_heritage/chm_cades_cove_heritage.ipynb`
  - `congaree_bottomland/chm_congaree_bottomland.ipynb`
  - `glacier_cedar_hemlock/chm_glacier_cedar_hemlock.ipynb`
  - `acadia_coastal/chm_acadia_coastal.ipynb`

### Current COG Status

Files are partially COG-compliant (tiled, compressed) but **lack internal overviews**:
```
Is COG: True
Warnings: ['The file is greater than 512xH or 512xW, it is recommended to include internal overviews']
```

---

## Implementation Tasks

### Phase 1: Create COG Utility Module

**File**: `utils/cog_utils.py`

```python
"""Cloud Optimized GeoTIFF (COG) utilities for 3DEP workflows."""

from pathlib import Path
from typing import Optional, List, Tuple
import subprocess
import numpy as np
from osgeo import gdal
import rasterio
from rasterio.enums import Resampling
from rio_cogeo.cogeo import cog_validate
import matplotlib.pyplot as plt

# Default settings
DEFAULT_OVERVIEW_LEVELS = [2, 4, 8, 16, 32]
THUMBNAIL_MAX_DIM = 512


def create_cog_gdal(
    input_path: Path,
    output_path: Optional[Path] = None,
    overview_resampling: str = "AVERAGE",
    compress: str = "LZW",
    predictor: int = 2,
    in_place: bool = False
) -> Path:
    """
    Convert GeoTIFF to COG using GDAL's COG driver.

    The COG driver automatically creates internal overviews.

    Args:
        input_path: Path to input GeoTIFF
        output_path: Path for output COG (default: replace in-place)
        overview_resampling: Resampling algorithm (AVERAGE, NEAREST, etc.)
        compress: Compression method (LZW, DEFLATE, ZSTD)
        predictor: Predictor for compression (2 for horizontal differencing)
        in_place: Replace input file with COG

    Returns:
        Path to created COG
    """
    input_path = Path(input_path)

    if output_path is None:
        if in_place:
            output_path = input_path
        else:
            output_path = input_path.parent / f"{input_path.stem}_cog.tif"

    temp_path = input_path.with_suffix('.tmp.tif')

    cmd = [
        "gdal_translate",
        "-of", "COG",
        "-co", f"COMPRESS={compress}",
        "-co", f"PREDICTOR={predictor}",
        "-co", "BLOCKSIZE=512",
        "-co", f"OVERVIEW_RESAMPLING={overview_resampling}",
        "-co", "BIGTIFF=IF_SAFER",
        str(input_path),
        str(temp_path)
    ]

    subprocess.run(cmd, check=True, capture_output=True)

    # Replace original if in-place
    import shutil
    shutil.move(str(temp_path), str(output_path))

    return output_path


def validate_cog(tif_path: Path) -> Tuple[bool, List[str], List[str]]:
    """
    Validate that a GeoTIFF is a valid Cloud Optimized GeoTIFF.

    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    return cog_validate(str(tif_path))


def create_thumbnail(
    tif_path: Path,
    output_path: Optional[Path] = None,
    max_dim: int = THUMBNAIL_MAX_DIM,
    colormap: str = "Greens"
) -> Path:
    """
    Create a thumbnail PNG from a GeoTIFF.

    Args:
        tif_path: Path to input GeoTIFF
        output_path: Path for output PNG
        max_dim: Maximum dimension in pixels
        colormap: Matplotlib colormap name

    Returns:
        Path to created thumbnail
    """
    tif_path = Path(tif_path)

    if output_path is None:
        output_path = tif_path.parent / f"{tif_path.stem}_thumb.png"

    with rasterio.open(tif_path) as src:
        scale = max_dim / max(src.height, src.width)
        new_width = int(src.width * scale)
        new_height = int(src.height * scale)

        data = src.read(
            1,
            out_shape=(new_height, new_width),
            resampling=Resampling.bilinear
        )

        if src.nodata is not None:
            data = np.ma.masked_equal(data, src.nodata)

    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    vmin, vmax = np.nanpercentile(data.compressed() if hasattr(data, 'compressed') else data, [2, 98])
    im = ax.imshow(data, cmap=colormap, vmin=vmin, vmax=vmax)
    ax.axis('off')
    plt.colorbar(im, ax=ax, shrink=0.8, label='Height (m)')
    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()

    return output_path


def get_cog_info(tif_path: Path) -> dict:
    """Get COG information for metadata."""
    is_cog, errors, warnings = validate_cog(tif_path)

    ds = gdal.Open(str(tif_path))
    band = ds.GetRasterBand(1)
    overview_count = band.GetOverviewCount()
    ds = None

    return {
        "is_cog": is_cog,
        "overview_count": overview_count,
        "file_size_mb": round(tif_path.stat().st_size / 1e6, 2),
        "cog_warnings": warnings,
        "cog_errors": errors
    }
```

**File**: `utils/__init__.py`

```python
"""3DEP COG utilities."""
from .cog_utils import create_cog_gdal, validate_cog, create_thumbnail, get_cog_info
```

---

### Phase 2: Create COG Validator Script

**File**: `utils/validate_cogs.py`

```python
#!/usr/bin/env python
"""
COG Validator Script for 3DEP Outputs.

Usage:
    python validate_cogs.py [--dir /path/to/tifs] [--verbose] [--fix]
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple
import json

from cog_utils import validate_cog, create_cog_gdal, get_cog_info

DEFAULT_OUTPUT_DIR = Path("/home/jovyan/data-store/data/output/3dep")


def find_tifs(directory: Path) -> List[Path]:
    """Find all TIF files in directory and subdirectories."""
    return list(directory.rglob("*.tif"))


def validate_all_cogs(
    directory: Path,
    verbose: bool = False,
    fix: bool = False
) -> Tuple[int, int, int]:
    """
    Validate all TIF files in a directory as COGs.

    Returns:
        Tuple of (total, valid, fixed)
    """
    tifs = find_tifs(directory)

    total = len(tifs)
    valid = 0
    fixed = 0
    invalid = []

    print(f"Found {total} TIF files in {directory}")
    print("-" * 60)

    for tif_path in sorted(tifs):
        is_cog, errors, warnings = validate_cog(tif_path)

        status = "VALID" if is_cog else "INVALID"

        if is_cog:
            valid += 1
            if warnings and verbose:
                status = "VALID (warnings)"
        else:
            invalid.append(tif_path)

        print(f"[{status:^18}] {tif_path.name}")

        if verbose:
            info = get_cog_info(tif_path)
            print(f"    Size: {info['file_size_mb']:.1f} MB, Overviews: {info['overview_count']}")
            for w in warnings:
                print(f"    WARNING: {w}")
            for e in errors:
                print(f"    ERROR: {e}")

    if fix and invalid:
        print(f"\nConverting {len(invalid)} invalid files to COG...")
        for tif_path in invalid:
            print(f"  {tif_path.name}...", end=" ", flush=True)
            try:
                create_cog_gdal(tif_path, in_place=True)
                fixed += 1
                print("DONE")
            except Exception as e:
                print(f"FAILED: {e}")

    print("\n" + "=" * 60)
    print(f"Total: {total} | Valid: {valid} | Invalid: {len(invalid)} | Fixed: {fixed}")

    return total, valid, fixed


def main():
    parser = argparse.ArgumentParser(description="Validate COG files")
    parser.add_argument("--dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--json", type=Path, help="Output JSON report")

    args = parser.parse_args()

    if not args.dir.exists():
        print(f"Error: Directory not found: {args.dir}")
        sys.exit(1)

    total, valid, fixed = validate_all_cogs(args.dir, args.verbose, args.fix)

    if args.json:
        report = {"directory": str(args.dir), "total": total, "valid": valid, "fixed": fixed}
        report["files"] = [get_cog_info(p) for p in find_tifs(args.dir)]
        args.json.write_text(json.dumps(report, indent=2, default=str))
        print(f"Report saved: {args.json}")

    sys.exit(0 if valid == total else 1)


if __name__ == "__main__":
    main()
```

---

### Phase 3: Update Notebook Template

**File**: `2_chm_user_aoi.ipynb`

Add the following cells after CHM/DEM generation:

#### Cell: COG Conversion

```python
# === Convert to Cloud Optimized GeoTIFFs ===
import subprocess
import shutil

def convert_to_cog(input_path, compress="LZW", overview_resampling="AVERAGE"):
    """Convert GeoTIFF to COG with internal overviews using GDAL."""
    from pathlib import Path
    input_path = Path(input_path)
    temp_path = input_path.with_suffix('.tmp.tif')

    cmd = [
        "gdal_translate",
        "-of", "COG",
        "-co", f"COMPRESS={compress}",
        "-co", "PREDICTOR=2",
        "-co", "BLOCKSIZE=512",
        "-co", f"OVERVIEW_RESAMPLING={overview_resampling}",
        "-co", "BIGTIFF=IF_SAFER",
        str(input_path),
        str(temp_path)
    ]

    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    shutil.move(str(temp_path), str(input_path))
    return input_path

print("Converting to Cloud Optimized GeoTIFFs...")
for tif_path in [chm_path, dem_path, dsm_path, dtm_path]:
    if tif_path.exists():
        print(f"  {tif_path.name}...", end=" ", flush=True)
        convert_to_cog(tif_path)
        print("done")

print("COG conversion complete!")
```

#### Cell: Validate COGs

```python
# === Validate COG Files ===
from rio_cogeo.cogeo import cog_validate
from osgeo import gdal

print("Validating COG files...")
print("-" * 50)

for tif_path in [chm_path, dem_path, dsm_path, dtm_path]:
    if tif_path.exists():
        is_cog, errors, warnings = cog_validate(str(tif_path))

        # Get overview count
        ds = gdal.Open(str(tif_path))
        overview_count = ds.GetRasterBand(1).GetOverviewCount()
        ds = None

        status = "VALID" if is_cog else "INVALID"
        print(f"[{status}] {tif_path.name} ({overview_count} overviews)")

        for w in warnings:
            print(f"  WARNING: {w}")
        for e in errors:
            print(f"  ERROR: {e}")

print("-" * 50)
```

#### Cell: Generate Thumbnails

```python
# === Generate Thumbnails ===
import matplotlib.pyplot as plt
from rasterio.enums import Resampling

def create_thumbnail(input_tif, output_png, max_size=512, cmap='Greens'):
    """Create thumbnail PNG from GeoTIFF."""
    with rasterio.open(input_tif) as src:
        scale = max_size / max(src.height, src.width)
        new_width = int(src.width * scale)
        new_height = int(src.height * scale)

        data = src.read(1, out_shape=(new_height, new_width), resampling=Resampling.bilinear)
        data = np.ma.masked_equal(data, src.nodata)

    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    vmin, vmax = np.nanpercentile(data.compressed(), [2, 98])
    im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.axis('off')
    plt.colorbar(im, ax=ax, shrink=0.8, label='Height (m)')
    plt.tight_layout()
    plt.savefig(output_png, dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()

print("Generating thumbnails...")
chm_thumb = LOCAL_OUTPUT_CHM / f"{SITE_NAME}_chm_thumb.png"
create_thumbnail(chm_path, chm_thumb)
print(f"  {chm_thumb.name}")

dem_thumb = LOCAL_OUTPUT_CHM / f"{SITE_NAME}_dem_thumb.png"
create_thumbnail(dem_path, dem_thumb, cmap='terrain')
print(f"  {dem_thumb.name}")

print("Thumbnails complete!")
```

#### Cell: Update Metadata with COG Info

```python
# === Update Metadata with COG Info ===
def get_cog_info(tif_path):
    """Get COG metadata."""
    is_cog, errors, warnings = cog_validate(str(tif_path))
    ds = gdal.Open(str(tif_path))
    overview_count = ds.GetRasterBand(1).GetOverviewCount()
    ds = None

    return {
        "is_cog": is_cog,
        "overview_count": overview_count,
        "file_size_mb": round(tif_path.stat().st_size / 1e6, 2),
        "cog_warnings": warnings,
        "cog_errors": errors
    }

# Add to stats dict
stats['outputs'] = {
    'chm': get_cog_info(chm_path) if chm_path.exists() else None,
    'dem': get_cog_info(dem_path) if dem_path.exists() else None,
    'dsm': get_cog_info(dsm_path) if dsm_path.exists() else None,
    'dtm': get_cog_info(dtm_path) if dtm_path.exists() else None,
    'thumbnails': [str(chm_thumb), str(dem_thumb)]
}
```

---

### Phase 4: Update All Site Notebooks

Apply identical changes to all 19 site notebooks. The changes are:

1. **Add COG conversion cell** after CHM generation
2. **Add COG validation cell**
3. **Add thumbnail generation cell**
4. **Update metadata cell** to include COG info

---

## Directory Structure

```
docs/notebooks/3dep/modified/
├── utils/
│   ├── __init__.py              # NEW: Package init
│   ├── cog_utils.py             # NEW: COG utility functions
│   └── validate_cogs.py         # NEW: COG validator script
├── 2_chm_user_aoi.ipynb         # MODIFIED: Add COG cells
├── plan.md                      # THIS FILE
└── sites/
    ├── acadia_coastal/
    │   └── chm_acadia_coastal.ipynb    # MODIFIED
    ├── adirondack_hemlock/
    │   └── chm_adirondack_hemlock.ipynb
    ├── big_thicket_floodplain/
    │   └── chm_big_thicket_floodplain.ipynb
    ├── black_hills_ponderosa/
    │   └── chm_black_hills_ponderosa.ipynb
    ├── cades_cove_heritage/
    │   └── chm_cades_cove_heritage.ipynb
    ├── congaree_bottomland/
    │   └── chm_congaree_bottomland.ipynb
    ├── glacier_cedar_hemlock/
    │   └── chm_glacier_cedar_hemlock.ipynb
    ├── great_smoky_cove/
    │   └── chm_great_smoky_cove.ipynb
    ├── olympic_hoh/
    │   └── chm_olympic_hoh.ipynb
    ├── redwood_humboldt/
    │   └── chm_redwood_humboldt.ipynb
    ├── rocky_mountain_subalpine/
    │   └── chm_rocky_mountain_subalpine.ipynb
    ├── sequoia_giant_forest/
    │   └── chm_sequoia_giant_forest.ipynb
    ├── shenandoah_limberlost/
    │   └── chm_shenandoah_limberlost.ipynb
    ├── sitka_spruce_coastal/
    │   └── chm_sitka_spruce_coastal.ipynb
    ├── superior_old_growth/
    │   └── chm_superior_old_growth.ipynb
    ├── tahoe_old_growth/
    │   └── chm_tahoe_old_growth.ipynb
    ├── tongass_mendenhall/
    │   └── chm_tongass_mendenhall.ipynb
    ├── white_mountain_northern/
    │   └── chm_white_mountain_northern.ipynb
    └── yellowstone_lodgepole/
        └── chm_yellowstone_lodgepole.ipynb
```

---

## Summary Table

| Component | Current | Proposed |
|-----------|---------|----------|
| **PDAL output** | Tiled LZW GeoTIFF | Same (no change) |
| **rioxarray output** | Tiled LZW GeoTIFF | Same (no change) |
| **Post-processing** | None | GDAL COG conversion |
| **Overviews** | None | Auto-generated by COG driver |
| **Block size** | 256x256 | 512x512 |
| **Validation** | None | rio-cogeo validation |
| **Thumbnails** | Preview PNG only | Add 512px thumbnails |

---

## Execution Order

1. Create `utils/__init__.py`
2. Create `utils/cog_utils.py`
3. Create `utils/validate_cogs.py`
4. Update `2_chm_user_aoi.ipynb` template
5. Update each site notebook (19 total)
6. Test with `python utils/validate_cogs.py --dir /path/to/output --verbose`

---

## Testing Commands

```bash
# Validate existing TIFs
cd /home/jovyan/fractal-notebooks/docs/notebooks/3dep/modified
python utils/validate_cogs.py --dir /home/jovyan/data-store/data/output/3dep --verbose

# Fix non-COG files in place
python utils/validate_cogs.py --dir /home/jovyan/data-store/data/output/3dep --fix

# Generate JSON report
python utils/validate_cogs.py --dir /home/jovyan/data-store/data/output/3dep --json cog_report.json
```

---

## Dependencies

All required packages are already in the `3dep` environment:
- `gdal>=3.6` - COG driver support
- `rio-cogeo>=5.0` - COG validation
- `rasterio>=1.3` - Raster I/O
- `matplotlib` - Thumbnail generation
