# 3DEP Canopy Height Model Workflows

Generate **Canopy Height Models (CHMs)** from USGS 3D Elevation Program (3DEP) lidar data for forest research sites across the USA.

## Overview

This directory contains Jupyter notebook workflows for generating Canopy Height Models (CHMs) from 3DEP lidar point clouds. CHMs represent the height of vegetation above ground level, calculated as the difference between the Digital Surface Model (DSM) and Digital Terrain Model (DTM).

**Key Features:**
- **Adaptive Resolution:** 0.333m for high-density lidar (>=12 pts/m²), 0.5m for standard density
- **Direct CHM Calculation:** Simple subtraction (DSM - DTM) with no smoothing or interpolation
- **Cloud-Optimized GeoTIFFs:** All outputs include internal overviews for efficient web visualization
- **18 US Forest Sites:** Diverse forest types from coast redwoods to boreal forests

## Directory Structure

```
3dep/
├── README.md                    # This file
├── forest_sites.yaml            # Site configuration (18 US forests)
├── geojson/                     # Site boundary files
│   ├── all_sites.geojson
│   ├── sequoia_giant_forest.geojson
│   ├── redwood_humboldt.geojson
│   └── ... (18 site files)
├── original/                    # Unmodified OpenTopography notebooks
│   ├── 01_3DEP_Generate_DEM_User_AOI.ipynb
│   ├── 02_3DEP_Generate_DEM_USGS_7.5_Quadrangles.ipynb
│   ├── 03_3DEP_Generate_DEM_USGS_HUCs.ipynb
│   ├── 04_3DEP_Generate_DEM_Corridors.ipynb
│   ├── 05_3DEP_Generate_Canopy_Height_Models_User_AOI.ipynb
│   ├── 06_3DEP_Topographic_Differencing.ipynb
│   └── 07_3DEP_Generate_Colorized_PointClouds.ipynb
└── modified/                    # Modified workflow notebooks
    ├── 1_forest_sites_map.ipynb       # Interactive map of all sites
    ├── 2_chm_user_aoi.ipynb           # Template: CHM generation
    ├── 3_chm_fractal_analysis.ipynb   # Template: Fractal analysis
    ├── chm_forest_sites.ipynb         # Batch processing notebook
    ├── generate_site_notebooks.py     # Script to generate site notebooks
    ├── utils/                         # Utility modules
    │   ├── __init__.py
    │   ├── cog_utils.py               # COG creation/validation
    │   ├── validate_cogs.py           # COG validation script
    │   └── update_notebooks_cog.py    # Notebook update utilities
    └── sites/                         # Site-specific notebooks
        ├── sequoia_giant_forest/
        │   ├── chm_sequoia_giant_forest.ipynb
        │   └── fractal_sequoia_giant_forest.ipynb
        ├── redwood_humboldt/
        │   ├── chm_redwood_humboldt.ipynb
        │   └── fractal_redwood_humboldt.ipynb
        └── ... (18 site directories)
```

## Forest Sites (18 total)

### Pacific Northwest - Temperate Rainforests

| Site ID | Name | State | Forest Type | Max Height |
|---------|------|-------|-------------|------------|
| `sequoia_giant_forest` | Sequoia Giant Forest | CA | Giant Sequoia | ~95m |
| `redwood_humboldt` | Humboldt Redwoods | CA | Coast Redwood | ~115m |
| `olympic_hoh` | Olympic Hoh Rainforest | WA | Temperate Rainforest | ~75m |
| `tongass_mendenhall` | Tongass Mendenhall | AK | Temperate Rainforest | ~60m |

### Rocky Mountains - Conifer Forests

| Site ID | Name | State | Forest Type | Max Height |
|---------|------|-------|-------------|------------|
| `yellowstone_lodgepole` | Yellowstone Lodgepole | WY | Lodgepole Pine | ~30m |
| `rocky_mountain_subalpine` | Rocky Mountain Subalpine | CO | Spruce-Fir | ~35m |

### Southwest - Ponderosa Pine

| Site ID | Name | State | Forest Type | Max Height |
|---------|------|-------|-------------|------------|
| `coconino_ponderosa` | Coconino Ponderosa | AZ | Ponderosa Pine | ~40m |
| `gila_mixed_conifer` | Gila Mixed Conifer | NM | Mixed Conifer | ~35m |

### Eastern Deciduous - Hardwood Forests

| Site ID | Name | State | Forest Type | Max Height |
|---------|------|-------|-------------|------------|
| `great_smoky_cove` | Great Smoky Cove Forest | TN | Mixed Mesophytic | ~55m |
| `mark_twain_ozark` | Mark Twain Ozark | MO | Oak-Hickory | ~35m |
| `white_mountain_northern` | White Mountain Northern | NH | Northern Hardwood | ~35m |

### Boreal/Northern - Mixed Forests

| Site ID | Name | State | Forest Type | Max Height |
|---------|------|-------|-------------|------------|
| `boundary_waters` | Boundary Waters | MN | Boreal Mixed | ~25m |
| `superior_old_growth` | Superior Old Growth | MN | Boreal Conifer | ~30m |

### Southeastern - Pine Forests

| Site ID | Name | State | Forest Type | Max Height |
|---------|------|-------|-------------|------------|
| `ocala_longleaf` | Ocala Longleaf | FL | Longleaf Pine | ~35m |
| `conecuh_longleaf` | Conecuh Longleaf | AL | Longleaf Pine | ~35m |

### Research Sites

| Site ID | Name | State | Forest Type | Max Height |
|---------|------|-------|-------------|------------|
| `harvard_forest` | Harvard Forest LTER | MA | Transition Hardwood | ~30m |
| `wind_river` | Wind River Exp. Forest | WA | Douglas-fir | ~65m |
| `niwot_ridge` | Niwot Ridge LTER | CO | Subalpine | ~20m |

## Modified Notebooks

### Templates

| Notebook | Description |
|----------|-------------|
| `1_forest_sites_map.ipynb` | Interactive Leaflet map displaying all 18 forest sites with 3DEP lidar coverage boundaries |
| `2_chm_user_aoi.ipynb` | Template for CHM generation - downloads point clouds, generates DSM/DTM, calculates CHM |
| `3_chm_fractal_analysis.ipynb` | Template for fractal dimension analysis of CHM surfaces using box-counting method |
| `chm_forest_sites.ipynb` | Batch processing workflow for multiple sites from `forest_sites.yaml` |

### Site-Specific Notebooks

Each site directory under `modified/sites/` contains:

- `chm_<site_id>.ipynb` - CHM generation configured for that specific site
- `fractal_<site_id>.ipynb` - Fractal analysis of the site's CHM

These notebooks are pre-configured with:
- Site bounding box coordinates
- Expected maximum tree heights for validation
- Output paths for CHM, DSM, DTM, and metadata

## Original Notebooks

Reference implementations from [OpenTopography/OT_3DEP_Workflows](https://github.com/OpenTopography/OT_3DEP_Workflows):

| Notebook | Description |
|----------|-------------|
| `01_3DEP_Generate_DEM_User_AOI.ipynb` | DEM generation for user-defined area of interest |
| `02_3DEP_Generate_DEM_USGS_7.5_Quadrangles.ipynb` | DEMs for USGS 7.5-minute quadrangle tiles |
| `03_3DEP_Generate_DEM_USGS_HUCs.ipynb` | DEMs for watershed boundaries (HUCs) |
| `04_3DEP_Generate_DEM_Corridors.ipynb` | DEMs along linear corridors |
| `05_3DEP_Generate_Canopy_Height_Models_User_AOI.ipynb` | Original CHM workflow (basis for modified version) |
| `06_3DEP_Topographic_Differencing.ipynb` | Elevation change detection between datasets |
| `07_3DEP_Generate_Colorized_PointClouds.ipynb` | Point clouds colorized with NAIP imagery |

## Utility Modules

### `utils/cog_utils.py`

Functions for Cloud-Optimized GeoTIFF (COG) creation and validation:

- `create_cog_gdal()` - Convert GeoTIFF to COG using GDAL's COG driver
- `validate_cog()` - Validate COG compliance using rio-cogeo
- `create_thumbnail()` - Generate PNG thumbnails from GeoTIFFs
- `get_cog_info()` - Get COG metadata (overview count, file size, validation status)

### `utils/validate_cogs.py`

Command-line script for batch COG validation:

```bash
# Validate all TIFs in a directory
python validate_cogs.py --dir /path/to/outputs --verbose

# Fix non-COG files in place
python validate_cogs.py --dir /path/to/outputs --fix

# Generate JSON report
python validate_cogs.py --dir /path/to/outputs --json report.json
```

## GeoJSON Files

The `geojson/` directory contains boundary polygons for each forest site:

- `all_sites.geojson` - Combined file with all 18 sites
- `<site_id>.geojson` - Individual site boundaries

These files are used by `1_forest_sites_map.ipynb` for interactive visualization.

## Processing Configuration

From `forest_sites.yaml`:

```yaml
processing:
  # Resolution determined by point density
  density_threshold: 12    # points per m²
  resolution_high: 0.333   # meters (>= 12 pts/m²)
  resolution_standard: 0.5 # meters (< 12 pts/m²)

  # Direct computation, no smoothing
  dsm_method: "max"        # Highest point per cell
  dtm_method: "min"        # Lowest ground point per cell
  smoothing: "none"
  interpolation: "none"

  # Output formats
  output_format: "GeoTIFF"
  compression: "LZW"
  generate_cog: true       # Cloud-Optimized GeoTIFF
  generate_preview: true   # PNG preview image
```

## Output Structure

CHM outputs are stored in:

```
outputs/3dep/
├── chm/
│   └── <site_id>/
│       ├── <site_id>_chm.tif          # Canopy Height Model (COG)
│       ├── <site_id>_chm_thumb.png    # Thumbnail preview
│       └── <site_id>_metadata.json    # Processing metadata
├── dsm/
│   └── <site_id>/
│       └── <site_id>_dsm.tif          # Digital Surface Model
├── dtm/
│   └── <site_id>/
│       └── <site_id>_dtm.tif          # Digital Terrain Model
└── fractal/
    └── <site_id>/
        ├── <site_id>_fractal.json     # Fractal dimension results
        ├── <site_id>_boxcount.png     # Box-counting plot
        └── <site_id>_lacunarity.png   # Lacunarity analysis
```

## Quick Start

### Environment Setup

```bash
# Create conda environment (if not using CyVerse)
conda env create -f environments/3dep-environment.yml
conda activate 3dep

# Verify installation
python -c "import pdal; import geopandas; import rioxarray; print('Ready!')"
```

### Running Notebooks

```bash
# View all forest sites on interactive map
jupyter lab modified/1_forest_sites_map.ipynb

# Generate CHM for a specific site
jupyter lab modified/sites/sequoia_giant_forest/chm_sequoia_giant_forest.ipynb

# Run fractal analysis on existing CHM
jupyter lab modified/sites/sequoia_giant_forest/fractal_sequoia_giant_forest.ipynb
```

### CyVerse Execution

For execution on CyVerse VICE:

1. Launch a JupyterLab VICE application
2. Clone this repository or upload notebooks
3. Update `OUTPUT_BASE` paths to `/iplant/home/<username>/3dep/`
4. Run notebooks - outputs persist in CyVerse Data Store

## Dependencies

Required Python packages (available in `3dep` conda environment):

- **PDAL Processing:** `pdal`, `python-pdal`
- **Geospatial:** `gdal`, `geopandas`, `rasterio`, `rioxarray`, `pyproj`, `shapely`, `fiona`
- **COG Support:** `rio-cogeo`
- **Visualization:** `matplotlib`, `ipyleaflet`, `folium`, `contextily`
- **Analysis:** `numpy`, `scipy`, `scikit-image`
- **Data:** `xarray`, `pandas`, `requests`

## References

- [USGS 3D Elevation Program](https://www.usgs.gov/3d-elevation-program)
- [OpenTopography](https://opentopography.org/)
- [OT_3DEP_Workflows GitHub](https://github.com/OpenTopography/OT_3DEP_Workflows)
- [PDAL Documentation](https://pdal.io/)
- [CyVerse](https://cyverse.org/)
