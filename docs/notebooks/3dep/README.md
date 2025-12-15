# 3DEP Canopy Height Model Workflows

Jupyter notebooks for generating Canopy Height Models (CHMs) from USGS 3DEP lidar data.

## Directory Structure

```
3dep/
├── README.md                    # This file
├── index.md                     # MkDocs index page
├── forest_sites.yaml            # Site configuration (18 US forests)
├── original/                    # Unmodified OpenTopography notebooks
│   ├── 01_3DEP_Generate_DEM_User_AOI.ipynb
│   ├── 02_3DEP_Generate_DEM_USGS_7.5_Quadrangles.ipynb
│   ├── 03_3DEP_Generate_DEM_USGS_HUCs.ipynb
│   ├── 04_3DEP_Generate_DEM_Corridors.ipynb
│   ├── 05_3DEP_Generate_Canopy_Height_Models_User_AOI.ipynb
│   ├── 06_3DEP_Topographic_Differencing.ipynb
│   └── 07_3DEP_Generate_Colorized_PointClouds.ipynb
├── modified/                    # Our modified versions
│   ├── chm_user_aoi.ipynb      # Single-site CHM workflow
│   └── chm_forest_sites.ipynb  # Multi-site batch processing
├── forest_sites/               # (future) Site-specific notebooks
└── utils/                      # (future) Shared utility modules
```

## Quick Start

```bash
# Install environment
conda env create -f ../../environments/3dep-environment.yml
conda activate 3dep

# Run single-site notebook
jupyter lab modified/chm_user_aoi.ipynb

# Run batch processing
jupyter lab modified/chm_forest_sites.ipynb
```

## Key Modifications from Original

1. **Removed Google Colab dependencies** - Runs locally or on CyVerse
2. **Adaptive resolution** - 0.333m or 0.5m based on point density
3. **No smoothing/IDW** - Direct max/min gridding for DSM/DTM
4. **Batch processing** - Process multiple sites from YAML config
5. **Metadata generation** - JSON metadata with statistics for each output

## Source

Original notebooks from [OpenTopography/OT_3DEP_Workflows](https://github.com/OpenTopography/OT_3DEP_Workflows)
