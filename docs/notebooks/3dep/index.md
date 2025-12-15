# 3DEP Canopy Height Model Workflows

Generate **Canopy Height Models (CHMs)** from USGS 3D Elevation Program (3DEP) lidar data for forest research sites across the USA.

## Overview

These notebooks provide workflows for:

- Accessing 3DEP point cloud data from AWS
- Generating Digital Surface Models (DSM) and Digital Terrain Models (DTM)
- Calculating Canopy Height Models (CHM = DSM - DTM)
- Batch processing multiple forest sites

**Key Features:**

- **Adaptive Resolution:** 0.5m for <12 pts/m², 0.333m for >=12 pts/m²
- **Direct CHM Calculation:** No smoothing or IDW interpolation
- **CyVerse Ready:** Designed for execution on CyVerse VICE

## Notebooks

### Modified Workflows

| Notebook | Description |
|----------|-------------|
| [chm_user_aoi.ipynb](modified/chm_user_aoi.ipynb) | Single-site CHM generation for user-defined AOI |
| [chm_forest_sites.ipynb](modified/chm_forest_sites.ipynb) | Batch processing multiple forest sites |

### Original OpenTopography Notebooks

Reference implementations from [OT_3DEP_Workflows](https://github.com/OpenTopography/OT_3DEP_Workflows):

| Notebook | Description |
|----------|-------------|
| [01_3DEP_Generate_DEM_User_AOI.ipynb](original/01_3DEP_Generate_DEM_User_AOI.ipynb) | DEM generation for user AOI |
| [02_3DEP_Generate_DEM_USGS_7.5_Quadrangles.ipynb](original/02_3DEP_Generate_DEM_USGS_7.5_Quadrangles.ipynb) | DEMs by USGS quadrangle |
| [03_3DEP_Generate_DEM_USGS_HUCs.ipynb](original/03_3DEP_Generate_DEM_USGS_HUCs.ipynb) | DEMs by hydrologic unit |
| [04_3DEP_Generate_DEM_Corridors.ipynb](original/04_3DEP_Generate_DEM_Corridors.ipynb) | DEMs for corridors |
| [05_3DEP_Generate_Canopy_Height_Models_User_AOI.ipynb](original/05_3DEP_Generate_Canopy_Height_Models_User_AOI.ipynb) | Original CHM workflow |
| [06_3DEP_Topographic_Differencing.ipynb](original/06_3DEP_Topographic_Differencing.ipynb) | Elevation change detection |
| [07_3DEP_Generate_Colorized_PointClouds.ipynb](original/07_3DEP_Generate_Colorized_PointClouds.ipynb) | Colorized point clouds |

## Forest Sites

The [forest_sites.yaml](forest_sites.yaml) configuration defines 18 US forest sites:

### Priority 1 (High-quality / Research Sites)

| Site | State | Forest Type | Max Height |
|------|-------|-------------|------------|
| Sequoia Giant Forest | CA | Giant Sequoia | ~95m |
| Humboldt Redwoods | CA | Coast Redwood | ~115m |
| Great Smoky Mountains | TN | Mixed Mesophytic | ~55m |
| Harvard Forest LTER | MA | Transition Hardwood | ~30m |
| Wind River Exp. Forest | WA | Douglas-fir | ~65m |

### Other Sites by Region

**Pacific Northwest:** Olympic Hoh, Tongass Mendenhall, Wind River

**Rocky Mountains:** Yellowstone, Rocky Mountain Subalpine

**Southwest:** Coconino, Gila Mixed Conifer

**Eastern:** Great Smoky, Mark Twain, White Mountain, Harvard Forest

**Boreal/Northern:** Boundary Waters, Superior Old Growth

**Southeast:** Ocala Longleaf, Conecuh Longleaf

## Setup

### Environment Installation

```bash
# Create conda environment
conda env create -f environments/3dep-environment.yml

# Activate
conda activate 3dep

# Verify
python -c "import pdal; import geopandas; print('Ready!')"
```

### CyVerse VICE

For execution on CyVerse:

1. Launch a JupyterLab VICE application
2. Install the 3dep environment (or use a pre-configured image)
3. Update `OUTPUT_BASE` paths to point to `/iplant/home/<username>/3dep/`

## Processing Configuration

From `forest_sites.yaml`:

```yaml
processing:
  density_threshold: 12  # points per m²
  resolution_high: 0.333  # for >= 12 pts/m²
  resolution_standard: 0.5  # for < 12 pts/m²

  # No smoothing or interpolation
  dsm_method: "max"
  dtm_method: "min"
  smoothing: "none"
```

## Output Structure

```
outputs/3dep/
├── chm/
│   └── <site_id>/
│       ├── <site_id>_chm.tif
│       ├── <site_id>_preview.png
│       └── <site_id>_metadata.json
├── dsm/
│   └── <site_id>/
│       └── <site_id>_dsm.tif
├── dtm/
│   └── <site_id>/
│       └── <site_id>_dtm.tif
└── logs/
    ├── batch_results_*.json
    └── batch_summary_*.csv
```

## References

- [USGS 3DEP Program](https://www.usgs.gov/3d-elevation-program)
- [OpenTopography](https://opentopography.org/)
- [PDAL Documentation](https://pdal.io/)
- [CyVerse](https://cyverse.org/)
