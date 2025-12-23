"""Cloud Optimized GeoTIFF (COG) utilities for 3DEP workflows.

This module provides functions for:
- Converting GeoTIFFs to COGs with internal overviews using GDAL
- Validating COG compliance using rio-cogeo
- Creating thumbnail images from GeoTIFFs
- Extracting COG metadata information
"""

from pathlib import Path
from typing import Optional, List, Tuple
import subprocess
import shutil

import numpy as np
from osgeo import gdal
import rasterio
from rasterio.enums import Resampling
from rio_cogeo.cogeo import cog_validate
import matplotlib.pyplot as plt


# Default settings
DEFAULT_OVERVIEW_LEVELS = [2, 4, 8, 16, 32]
THUMBNAIL_MAX_DIM = 512
THUMBNAIL_DPI = 100


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

    The COG driver automatically creates internal overviews at appropriate
    levels based on the raster dimensions.

    Args:
        input_path: Path to input GeoTIFF
        output_path: Path for output COG (default: same as input if in_place,
                     otherwise adds _cog suffix)
        overview_resampling: Resampling algorithm for overviews.
                            Options: AVERAGE, NEAREST, BILINEAR, CUBIC, etc.
        compress: Compression method. Options: LZW, DEFLATE, ZSTD
        predictor: Predictor for compression (2 = horizontal differencing,
                   good for elevation data)
        in_place: If True, replace input file with COG

    Returns:
        Path to created COG file

    Raises:
        subprocess.CalledProcessError: If gdal_translate fails
        FileNotFoundError: If input file doesn't exist
    """
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path is None:
        if in_place:
            output_path = input_path
        else:
            output_path = input_path.parent / f"{input_path.stem}_cog.tif"

    temp_path = input_path.with_suffix('.tmp.tif')

    # Build gdal_translate command with COG driver
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

    # Run conversion
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)

    # Move temp file to final destination
    shutil.move(str(temp_path), str(output_path))

    return output_path


def add_overviews_gdaladdo(
    tif_path: Path,
    levels: List[int] = None,
    resampling: str = "average"
) -> None:
    """
    Add internal overviews to an existing GeoTIFF using gdaladdo.

    Note: This is typically not needed when using create_cog_gdal, as the
    COG driver creates overviews automatically. Use this for existing TIFs
    that need overviews added without full COG conversion.

    Args:
        tif_path: Path to GeoTIFF
        levels: Overview decimation levels (e.g., [2, 4, 8, 16, 32])
                If None, uses DEFAULT_OVERVIEW_LEVELS
        resampling: Resampling method (average, nearest, gauss, cubic, etc.)

    Raises:
        subprocess.CalledProcessError: If gdaladdo fails
    """
    if levels is None:
        levels = DEFAULT_OVERVIEW_LEVELS

    cmd = [
        "gdaladdo",
        "-r", resampling,
        str(tif_path),
        *[str(level) for level in levels]
    ]

    subprocess.run(cmd, check=True, capture_output=True, text=True)


def validate_cog(tif_path: Path) -> Tuple[bool, List[str], List[str]]:
    """
    Validate that a GeoTIFF is a valid Cloud Optimized GeoTIFF.

    Uses rio-cogeo's validation which checks for:
    - Proper tile organization
    - Internal overviews (warns if missing for large files)
    - Header placement at file start

    Args:
        tif_path: Path to GeoTIFF to validate

    Returns:
        Tuple of (is_valid, errors, warnings)
        - is_valid: True if file is a valid COG
        - errors: List of validation errors (empty if valid)
        - warnings: List of validation warnings
    """
    return cog_validate(str(tif_path))


def create_thumbnail(
    tif_path: Path,
    output_path: Optional[Path] = None,
    max_dim: int = THUMBNAIL_MAX_DIM,
    colormap: str = "Greens",
    title: Optional[str] = None
) -> Path:
    """
    Create a thumbnail PNG from a GeoTIFF.

    Reads the raster at reduced resolution and creates a matplotlib
    figure with colorbar.

    Args:
        tif_path: Path to input GeoTIFF
        output_path: Path for output PNG (default: same name with _thumb.png)
        max_dim: Maximum dimension (width or height) in pixels
        colormap: Matplotlib colormap name (e.g., 'Greens', 'terrain', 'viridis')
        title: Optional title for the thumbnail

    Returns:
        Path to created thumbnail file
    """
    tif_path = Path(tif_path)

    if output_path is None:
        output_path = tif_path.parent / f"{tif_path.stem}_thumb.png"

    with rasterio.open(tif_path) as src:
        # Calculate thumbnail dimensions maintaining aspect ratio
        scale = max_dim / max(src.height, src.width)
        new_width = int(src.width * scale)
        new_height = int(src.height * scale)

        # Read and resample data
        data = src.read(
            1,
            out_shape=(new_height, new_width),
            resampling=Resampling.bilinear
        )

        # Mask nodata values
        if src.nodata is not None:
            data = np.ma.masked_equal(data, src.nodata)

    # Create figure
    fig, ax = plt.subplots(figsize=(6, 6), dpi=THUMBNAIL_DPI)

    # Use robust percentile-based color scaling
    if hasattr(data, 'compressed'):
        valid_data = data.compressed()
    else:
        valid_data = data[~np.isnan(data)]

    if len(valid_data) > 0:
        vmin, vmax = np.percentile(valid_data, [2, 98])
    else:
        vmin, vmax = 0, 1

    im = ax.imshow(data, cmap=colormap, vmin=vmin, vmax=vmax)
    ax.axis('off')

    if title:
        ax.set_title(title, fontsize=10)

    plt.colorbar(im, ax=ax, shrink=0.8, label='Height (m)')
    plt.tight_layout()
    plt.savefig(output_path, dpi=THUMBNAIL_DPI, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    return output_path


def get_cog_info(tif_path: Path) -> dict:
    """
    Get comprehensive information about a COG file.

    Args:
        tif_path: Path to GeoTIFF

    Returns:
        Dictionary containing:
        - path: File path
        - file_size_mb: File size in megabytes
        - width, height: Raster dimensions
        - bands: Number of bands
        - overview_count: Number of internal overviews
        - is_cog: Whether file passes COG validation
        - cog_warnings: List of validation warnings
        - cog_errors: List of validation errors
    """
    tif_path = Path(tif_path)

    # Get COG validation status
    is_cog, errors, warnings = validate_cog(tif_path)

    # Open with GDAL to get overview info
    ds = gdal.Open(str(tif_path))

    info = {
        "path": str(tif_path),
        "file_size_mb": round(tif_path.stat().st_size / 1e6, 2),
        "width": ds.RasterXSize,
        "height": ds.RasterYSize,
        "bands": ds.RasterCount,
    }

    # Get overview count from first band
    band = ds.GetRasterBand(1)
    info["overview_count"] = band.GetOverviewCount()

    # Clean up GDAL dataset
    ds = None

    # Add validation info
    info["is_cog"] = is_cog
    info["cog_warnings"] = warnings
    info["cog_errors"] = errors

    return info


def convert_all_to_cog(
    directory: Path,
    pattern: str = "*.tif",
    in_place: bool = True,
    verbose: bool = True
) -> List[Path]:
    """
    Convert all matching TIF files in a directory to COG format.

    Args:
        directory: Directory containing TIF files
        pattern: Glob pattern for matching files
        in_place: Replace original files with COGs
        verbose: Print progress messages

    Returns:
        List of converted file paths
    """
    directory = Path(directory)
    tif_files = list(directory.glob(pattern))
    converted = []

    for tif_path in tif_files:
        if verbose:
            print(f"  Converting {tif_path.name}...", end=" ", flush=True)

        try:
            create_cog_gdal(tif_path, in_place=in_place)
            converted.append(tif_path)
            if verbose:
                print("done")
        except Exception as e:
            if verbose:
                print(f"FAILED: {e}")

    return converted
