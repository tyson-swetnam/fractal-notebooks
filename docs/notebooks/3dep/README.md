# 3DEP Canopy Height Model Workflows

Generate **Canopy Height Models (CHMs)** from USGS 3D Elevation Program (3DEP) lidar data for forest research sites across the USA.

## Overview

These notebooks provide workflows for:

- Accessing 3DEP point cloud data from AWS
- Generating Digital Surface Models (DSM) and Digital Terrain Models (DTM)
- Calculating Canopy Height Models (CHM = DSM - DTM)
- Batch processing multiple forest sites
- Fractal analysis of canopy structure

**Key Features:**

- **Adaptive Resolution:** 0.5m for <12 pts/m², 0.333m for >=12 pts/m²
- **Direct CHM Calculation:** No smoothing or IDW interpolation
- **CyVerse Ready:** Designed for execution on CyVerse VICE

## Directory Structure

```
3dep/
├── README.md                    # This file
├── forest_sites.yaml            # Site configuration (18 US forests)
├── original/                    # Unmodified OpenTopography notebooks
│   ├── 01_3DEP_Generate_DEM_User_AOI.ipynb
│   ├── 02_3DEP_Generate_DEM_USGS_7.5_Quadrangles.ipynb
│   ├── 03_3DEP_Generate_DEM_USGS_HUCs.ipynb
│   ├── 04_3DEP_Generate_DEM_Corridors.ipynb
│   ├── 05_3DEP_Generate_Canopy_Height_Models_User_AOI.ipynb
│   ├── 06_3DEP_Topographic_Differencing.ipynb
│   └── 07_3DEP_Generate_Colorized_PointClouds.ipynb
└── modified/                    # Our modified versions
    ├── 1_forest_sites_map.ipynb       # Interactive map of forest sites
    ├── 2_chm_user_aoi.ipynb           # Single-site CHM workflow
    ├── 3_chm_fractal_analysis.ipynb   # Fractal dimension analysis
    └── chm_forest_sites.ipynb         # Multi-site batch processing
```

## Notebooks

### Modified Workflows

| Notebook | Description |
|----------|-------------|
| [1_forest_sites_map.ipynb](modified/1_forest_sites_map.ipynb) | Interactive Leaflet map of 18 forest sites with 3DEP lidar boundaries |
| [2_chm_user_aoi.ipynb](modified/2_chm_user_aoi.ipynb) | Single-site CHM generation for user-defined AOI |
| [3_chm_fractal_analysis.ipynb](modified/3_chm_fractal_analysis.ipynb) | Fractal dimension analysis of canopy structure |
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

## Quick Start

```bash
# Create conda environment
conda env create -f environments/3dep-environment.yml

# Activate
conda activate 3dep

# Verify
python -c "import pdal; import geopandas; print('Ready!')"

# Run notebooks
jupyter lab modified/1_forest_sites_map.ipynb
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

## Key Modifications from Original

1. **Removed Google Colab dependencies** - Runs locally or on CyVerse
2. **Adaptive resolution** - 0.333m or 0.5m based on point density
3. **No smoothing/IDW** - Direct max/min gridding for DSM/DTM
4. **Batch processing** - Process multiple sites from YAML config
5. **Metadata generation** - JSON metadata with statistics for each output

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
