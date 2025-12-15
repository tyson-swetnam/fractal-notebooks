# 3DEP Canopy Height Model Workflows Plan

## Overview

This document outlines the plan to integrate USGS 3D Elevation Program (3DEP) workflows from the [OpenTopography OT_3DEP_Workflows](https://github.com/OpenTopography/OT_3DEP_Workflows) repository into this project. The primary goal is to create modified notebooks that generate **Canopy Height Models (CHMs)** for selected forest sites across the USA and globally.

## Source Repository

**Repository:** https://github.com/OpenTopography/OT_3DEP_Workflows

### Available Notebooks (7 total)
| # | Notebook | Description |
|---|----------|-------------|
| 1 | `01_3DEP_Generate_DEM_User_AOI.ipynb` | Generate DTM/DSM for user-defined areas |
| 2 | `02_3DEP_Generate_DEM_USGS_7.5_Quadrangles.ipynb` | DEMs for USGS quadrangle tiles |
| 3 | `03_3DEP_Generate_DEM_USGS_HUCs.ipynb` | DEMs for watershed boundaries (HUCs) |
| 4 | `04_3DEP_Generate_DEM_Corridors.ipynb` | DEMs along linear corridors |
| 5 | `05_3DEP_Generate_Canopy_Height_Models_User_AOI.ipynb` | **Primary target** - CHM generation |
| 6 | `06_3DEP_Topographic_Differencing.ipynb` | Elevation change detection |
| 7 | `07_3DEP_Generate_Colorized_PointClouds.ipynb` | Point clouds with NAIP imagery |

### Key Dependencies
- GDAL, PDAL, python-pdal
- GeoPandas, rioxarray, pyproj
- matplotlib, ipyleaflet
- requests, notebook

---

## Phase 1: Environment Setup

### 1.1 Create Conda Environment

Create a new conda environment file: `environments/3dep-environment.yml`

```yaml
name: 3dep
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - gdal
  - geopandas
  - ipyleaflet
  - matplotlib
  - notebook
  - jupyterlab
  - pdal
  - pip
  - python-pdal
  - pyproj
  - requests
  - rioxarray
  - xarray
  - rasterio
  - shapely
  - fiona
  - numpy
  - pandas
  - scipy
  - scikit-image
  - folium
  - contextily
  - pip:
    - py3dep
    - pynhd
```

### 1.2 Installation Commands

```bash
# Create environment
conda env create -f environments/3dep-environment.yml

# Activate
conda activate 3dep

# Verify installation
python -c "import pdal; import geopandas; import rioxarray; print('All dependencies installed!')"
```

---

## Phase 2: Clone and Organize Notebooks

### 2.1 Directory Structure

```
docs/notebooks/3dep/
├── README.md                 # Overview and usage instructions
├── original/                 # Unmodified cloned notebooks (reference)
│   ├── 01_3DEP_Generate_DEM_User_AOI.ipynb
│   ├── 02_3DEP_Generate_DEM_USGS_7.5_Quadrangles.ipynb
│   ├── 03_3DEP_Generate_DEM_USGS_HUCs.ipynb
│   ├── 04_3DEP_Generate_DEM_Corridors.ipynb
│   ├── 05_3DEP_Generate_Canopy_Height_Models_User_AOI.ipynb
│   ├── 06_3DEP_Topographic_Differencing.ipynb
│   └── 07_3DEP_Generate_Colorized_PointClouds.ipynb
├── modified/                 # Our modified versions
│   ├── chm_user_aoi.ipynb   # Base CHM workflow
│   └── chm_forest_sites.ipynb # Multi-site forest CHM generator
└── forest_sites/            # Site-specific notebooks
    ├── chm_sequoia.ipynb
    ├── chm_tongass.ipynb
    ├── chm_yellowstone.ipynb
    └── ...
```

### 2.2 Clone Commands

```bash
# Clone to temporary location
git clone https://github.com/OpenTopography/OT_3DEP_Workflows.git /tmp/OT_3DEP_Workflows

# Create target directory
mkdir -p docs/notebooks/3dep/original

# Copy notebooks
cp /tmp/OT_3DEP_Workflows/notebooks/*.ipynb docs/notebooks/3dep/original/

# Cleanup
rm -rf /tmp/OT_3DEP_Workflows
```

---

## Phase 3: Notebook Modifications

### 3.1 Required Changes for Local Execution

1. **Remove Google Colab dependencies**
   - Remove `!pip install` cells
   - Remove Colab-specific mounting code
   - Update file paths for local storage

2. **Add environment validation**
   ```python
   # Cell 1: Environment check
   import sys
   required = ['pdal', 'geopandas', 'rioxarray', 'pyproj']
   missing = []
   for pkg in required:
       try:
           __import__(pkg)
       except ImportError:
           missing.append(pkg)
   if missing:
       raise ImportError(f"Missing packages: {missing}. Run: conda activate 3dep")
   ```

3. **Standardize output directories**
   ```python
   from pathlib import Path
   OUTPUT_DIR = Path("../../outputs/3dep")
   OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
   ```

4. **Add progress indicators**
   - Use `tqdm` for long-running operations
   - Add cell execution timestamps

5. **Parameterize AOI definitions**
   - Create configurable site definitions
   - Support GeoJSON, bounding boxes, and place names

### 3.2 CHM-Specific Enhancements

The Canopy Height Model workflow (Notebook 05) will be enhanced to:

1. **Batch processing** - Process multiple sites sequentially
2. **Quality metrics** - Add CHM statistics (max height, mean height, coverage %)
3. **Visualization** - Hillshade overlays, histogram analysis
4. **Export formats** - GeoTIFF, Cloud-Optimized GeoTIFF (COG), PNG previews
5. **Metadata** - Auto-generate JSON metadata for each output

---

## Phase 4: Forest Site Selection

### 4.1 Candidate Sites - USA

| Site | State | Forest Type | Approx. Coords | Notes |
|------|-------|-------------|----------------|-------|
| Sequoia National Forest | CA | Giant Sequoia | 36.5°N, 118.8°W | Tallest trees |
| Tongass National Forest | AK | Temperate Rainforest | 56.5°N, 133.0°W | Largest US forest |
| Olympic National Forest | WA | Temperate Rainforest | 47.8°N, 123.6°W | Old growth |
| Great Smoky Mountains | TN/NC | Mixed Deciduous | 35.6°N, 83.5°W | Biodiversity hotspot |
| Boundary Waters | MN | Boreal/Mixed | 48.0°N, 91.5°W | Wilderness area |
| Yellowstone | WY | Lodgepole Pine | 44.4°N, 110.6°W | Post-fire regeneration |
| Coconino | AZ | Ponderosa Pine | 35.2°N, 111.6°W | Largest ponderosa forest |
| Mark Twain | MO | Oak-Hickory | 37.5°N, 91.5°W | Eastern deciduous |
| Ocala | FL | Longleaf Pine | 29.2°N, 81.8°W | Sandhill ecosystem |
| White Mountain | NH | Northern Hardwood | 44.0°N, 71.5°W | Alpine/subalpine |

### 4.2 Candidate Sites - Global

| Site | Country | Forest Type | Data Source | Notes |
|------|---------|-------------|-------------|-------|
| Black Forest | Germany | Mixed Conifer | EU-DEM/Copernicus | Dense coverage |
| Amazon (Manaus) | Brazil | Tropical | GEDI/ICESat-2 | Canopy complexity |
| Białowieża | Poland/Belarus | Primeval | EU-DEM | Ancient forest |
| Daintree | Australia | Tropical | AusDEM | Rainforest |
| Yakushima | Japan | Temperate | Japan GSI | UNESCO site |

> **Note:** Global sites may require alternative data sources (GEDI, ICESat-2, national DEMs) as 3DEP coverage is USA-only.

### 4.3 Site Definition Format

```python
FOREST_SITES = {
    "sequoia": {
        "name": "Sequoia National Forest",
        "bbox": [-118.9, 36.4, -118.7, 36.6],  # [west, south, east, north]
        "crs": "EPSG:4326",
        "forest_type": "giant_sequoia",
        "expected_max_height": 95,  # meters
        "notes": "Contains General Sherman tree"
    },
    "tongass": {
        "name": "Tongass National Forest",
        "bbox": [-133.2, 56.3, -132.8, 56.7],
        "crs": "EPSG:4326",
        "forest_type": "temperate_rainforest",
        "expected_max_height": 60,
        "notes": "Sitka spruce and western hemlock"
    },
    # ... additional sites
}
```

---

## Phase 5: New Notebook Development

### 5.1 Core Notebooks to Create

#### `chm_forest_sites.ipynb` - Master Multi-Site Processor

```
1. Configuration
   - Load site definitions from JSON/YAML
   - Set output parameters (resolution, format, etc.)

2. Data Access
   - Query 3DEP availability for each site
   - Check for cached data
   - Download point clouds via OpenTopography API

3. Processing Pipeline
   - Generate DTM (ground surface)
   - Generate DSM (canopy surface)
   - Calculate CHM = DSM - DTM
   - Apply quality filters

4. Analysis
   - Compute height statistics per site
   - Compare across forest types
   - Generate summary visualizations

5. Export
   - Save CHM rasters (GeoTIFF/COG)
   - Generate PNG previews
   - Create metadata JSON
   - Build comparison report
```

#### `chm_analysis.ipynb` - CHM Analysis and Visualization

```
1. Load CHM outputs
2. Height distribution analysis
3. Canopy gap detection
4. Cross-site comparisons
5. Time series (if multi-temporal data available)
```

### 5.2 Utility Modules

Create `docs/notebooks/3dep/utils/`:

```python
# utils/sites.py - Site management
# utils/download.py - Data acquisition helpers
# utils/processing.py - PDAL pipeline wrappers
# utils/visualization.py - Plotting functions
# utils/export.py - Output format handlers
```

---

## Phase 6: Integration with Project

### 6.1 Documentation Updates

1. Add `docs/3dep.md` - Overview page for MkDocs
2. Update `mkdocs.yml` - Add 3DEP section to navigation
3. Create gallery of CHM outputs

### 6.2 MkDocs Navigation Addition

```yaml
nav:
  # ... existing sections ...
  - 3DEP Lidar Workflows:
    - Overview: 3dep.md
    - Notebooks:
      - Canopy Height Models: notebooks/3dep/index.md
      - Forest Sites: notebooks/3dep/forest_sites.md
```

### 6.3 Output Storage

```
outputs/3dep/
├── chm/
│   ├── sequoia/
│   │   ├── chm_sequoia_2024.tif
│   │   ├── chm_sequoia_2024_preview.png
│   │   └── metadata.json
│   ├── tongass/
│   └── ...
├── dem/
└── point_clouds/
```

---

## Phase 7: Implementation Timeline

### Step 1: Setup (Do First)
- [ ] Create `environments/3dep-environment.yml`
- [ ] Create directory structure
- [ ] Clone original notebooks

### Step 2: Adaptation
- [ ] Modify notebook 05 for local execution
- [ ] Test with small AOI
- [ ] Document changes

### Step 3: Site Configuration
- [ ] Create `forest_sites.yaml` with 5+ US sites
- [ ] Validate 3DEP coverage for each site
- [ ] Add site boundary GeoJSON files

### Step 4: Batch Processing
- [ ] Build `chm_forest_sites.ipynb`
- [ ] Test with 2-3 sites
- [ ] Optimize for larger areas

### Step 5: Analysis & Visualization
- [ ] Create analysis notebook
- [ ] Build comparison visualizations
- [ ] Generate documentation outputs

### Step 6: Documentation
- [ ] Write MkDocs pages
- [ ] Add notebook to navigation
- [ ] Create README for 3dep directory

---

## Open Questions

1. **Storage:** Where should large CHM outputs be stored? (Git LFS, external bucket, etc.)
2. **API Keys:** Does OpenTopography require API keys for bulk downloads?
3. **Resolution:** What spatial resolution to target? (1m, 3m, 10m)
4. **Temporal:** Include multi-year comparisons for change detection?
5. **Global Sites:** Which alternative data sources to prioritize for non-US sites?

---

## References

- [3DEP Program](https://www.usgs.gov/3d-elevation-program)
- [OpenTopography](https://opentopography.org/)
- [OT_3DEP_Workflows GitHub](https://github.com/OpenTopography/OT_3DEP_Workflows)
- [PDAL Documentation](https://pdal.io/)
- [py3dep Python Package](https://github.com/hyriver/py3dep)
