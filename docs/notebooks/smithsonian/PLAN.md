# Barro Colorado Island (BCI) LiDAR Analysis Project

## Project Overview

Analyze Airborne Laser Scanning (ALS) data from **Barro Colorado Island, Panama** collected in 2023 by the Smithsonian Tropical Research Institute (STRI). This project adapts the fractal-notebooks 3DEP workflow framework to work with raw LAZ point cloud data and pre-computed CHM products.

**Data Source:** [Smithsonian DataONE - ALS Panama 2023](https://smithsonian.dataone.org/datasets/ALS_Panama_2023/03_Barro_Colorado_Island/)

**Study Site:**
- **Location:** Barro Colorado Island, Gatun Lake, Panama Canal
- **Forest Type:** Tropical moist forest (Neotropical lowland rainforest)
- **Significance:** One of the most intensively studied tropical forests in the world; home to the 50-ha Forest Dynamics Plot (since 1980)
- **Expected Canopy Height:** Up to ~45-50m for emergent trees

## Data Inventory

### Pre-computed Products (Whole-Island GeoTIFFs)

| Product | Filename | Size | Resolution | Status |
|---------|----------|------|------------|--------|
| **CHM** | `BCI_whole_2023_05_26_chm.tif` | 1.1 GB | **0.5m** | Downloaded |
| **DTM** | `BCI_whole_2023_05_26_dtm.tif` | 1.1 GB | 0.5m | Downloaded |
| **DSM** | `BCI_whole_2023_05_26_dsm.tif` | 1.1 GB | 0.5m | Downloaded |

**Note:** The CHM is already at 0.5m resolution, which matches the 3DEP framework's standard resolution. This allows direct use with the existing `chm_` analysis notebooks without resampling.

### Point Cloud Data (LAZ Format)

| Directory | Contents | Count | Status |
|-----------|----------|-------|--------|
| `02_LAZ_Unclassified/` | Raw point clouds | ~127 tiles | Not downloaded |
| `03_LAZ_Classified/` | Classified point clouds | 113 tiles | **Downloaded (7.0 GB)** |

**Tile naming convention:** `BCI_2023_<easting>_<northing>.laz`
**Tile size:** 500m x 500m tiles
**File sizes:** Range from 20KB to 154MB per tile

### Additional Products

| Directory | Description |
|-----------|-------------|
| `05_Contour_0.5m/` | Topographic contours at 0.5m intervals |
| `08_Orthophoto/` | Aerial imagery |
| `09_Quality_Control/` | QC documentation |

## Output Directory

All downloaded data and outputs will be stored in:
```
~/data-store/data/output/smithsonian/
├── raw/
│   ├── chm/                    # Downloaded CHM GeoTIFF
│   ├── dtm/                    # Downloaded DTM GeoTIFF
│   ├── dsm/                    # Downloaded DSM GeoTIFF
│   └── laz/                    # Downloaded LAZ point clouds
├── processed/
│   ├── chm/                    # Processed CHM (COG format)
│   ├── subsets/                # AOI subsets for analysis
│   └── point_clouds/           # Processed point cloud outputs
└── analysis/
    ├── fractal/                # Fractal dimension results
    ├── figures/                # Publication-quality figures
    └── reports/                # Summary statistics and reports
```

## Notebook Structure

### Phase 1: Data Acquisition

#### `1_download_data.ipynb`
- Download pre-computed GeoTIFFs (CHM, DTM, DSM)
- Verify file integrity (checksums if available)
- Convert to Cloud-Optimized GeoTIFF (COG) format
- Generate metadata and thumbnails

**Key difference from 3DEP:** No point cloud processing needed for CHM generation; Smithsonian provides pre-computed products.

### Phase 2: CHM Exploration & Quality Assessment

#### `2_chm_exploration.ipynb`
- Load and visualize whole-island CHM
- Calculate summary statistics:
  - Min/max/mean/median canopy height
  - Height distribution histogram
  - Percentile analysis (P50, P95, P99)
- Compare with published BCI forest structure data
- Identify data quality issues (NoData areas, artifacts)
- Generate overview maps

### Phase 3: Subset Extraction for Analysis

#### `3_extract_subsets.ipynb`
- Define Areas of Interest (AOIs) for detailed analysis:
  - **50-ha Plot:** The famous BCI forest dynamics plot (~1000m x 500m)
  - **Young Forest:** Secondary growth areas
  - **Old Growth:** Mature forest stands
  - **Ridge/Valley Transects:** Topographic variation
- Extract CHM/DTM/DSM subsets for each AOI
- Compute AOI-specific statistics

### Phase 4: Fractal Analysis (Adapted from 3DEP Framework)

#### `4_fractal_analysis.ipynb`
Adapt `3dep/modified/3_chm_fractal_analysis.ipynb` for BCI data:

**Box-Counting Fractal Dimension:**
- 2D box-counting on CHM surface
- 3D box-counting treating canopy as volume
- Multi-scale analysis across box sizes

**Lacunarity Analysis:**
- Gap structure quantification
- Scale-dependent heterogeneity

**Height-Complexity Relationships:**
- Fractal dimension vs. mean canopy height
- Comparison with temperate forests (3DEP sites)

### Phase 5: Point Cloud Analysis (Optional Advanced)

#### `5_laz_processing.ipynb`
Direct LAZ processing for advanced metrics:

**Key adaptation from 3DEP:**
- Use `readers.las` instead of `readers.ept` (EPT is 3DEP-specific)
- Handle Panama-specific CRS (likely UTM Zone 17N, EPSG:32617)
- Process tiles individually or merge for AOI

**Metrics to compute:**
- Point density (pts/m²)
- Vertical profile distributions
- Canopy cover at multiple height thresholds
- Understory structure analysis

```python
# Example PDAL pipeline for LAZ (vs EPT for 3DEP)
pipeline = {
    "pipeline": [
        {
            "type": "readers.las",
            "filename": "BCI_2023_625000_1012000.laz"
        },
        # ... filters and writers
    ]
}
```

### Phase 6: Comparative Analysis

#### `6_comparative_analysis.ipynb`
- Compare BCI fractal dimensions with US temperate forests
- Tropical vs. temperate forest structure differences
- Scaling relationships across forest types

## Key Framework Adaptations

### From EPT to LAZ

| 3DEP Framework | BCI Adaptation |
|----------------|----------------|
| `readers.ept` (cloud-hosted) | `readers.las` (local LAZ files) |
| Dynamic AOI queries | Pre-tiled 500m x 500m |
| Single EPT endpoint | 127 individual tiles |
| EPSG:3857 output | EPSG:32617 (UTM 17N) native |

### Pre-computed Products

The 3DEP workflow generates CHM from point clouds:
```
Point Clouds → DSM (max) → DTM (min) → CHM = DSM - DTM
```

BCI already provides CHM, so we:
1. Use pre-computed CHM directly for most analyses
2. Optionally recompute from LAZ for validation/custom parameters

### CRS Handling

- **BCI Native CRS:** UTM Zone 17N (EPSG:32617) - appropriate for Panama
- **3DEP Default:** Web Mercator (EPSG:3857) - for web visualization
- **Analysis CRS:** Keep UTM for metric accuracy; convert for visualization

## Download Instructions

### Manual Download (Browser)

Navigate to each directory and download files:
```
https://smithsonian.dataone.org/datasets/ALS_Panama_2023/03_Barro_Colorado_Island/07_Canopy_Height_Model/TIFF/
https://smithsonian.dataone.org/datasets/ALS_Panama_2023/03_Barro_Colorado_Island/04_Digital_Terrain_Model/TIFF/
https://smithsonian.dataone.org/datasets/ALS_Panama_2023/03_Barro_Colorado_Island/06_Digital_Surface_Model/TIFF/
```

### Programmatic Download (wget/curl)

```bash
# Create directories
mkdir -p ~/data-store/data/output/smithsonian/raw/{chm,dtm,dsm,laz}

# Download pre-computed products
BASE_URL="https://smithsonian.dataone.org/datasets/ALS_Panama_2023/03_Barro_Colorado_Island"

# CHM (1.1 GB)
wget -O ~/data-store/data/output/smithsonian/raw/chm/BCI_whole_2023_05_26_chm.tif \
  "${BASE_URL}/07_Canopy_Height_Model/TIFF/BCI_whole_2023_05_26_chm.tif"

# DTM (1.1 GB)
wget -O ~/data-store/data/output/smithsonian/raw/dtm/BCI_whole_2023_05_26_dtm.tif \
  "${BASE_URL}/04_Digital_Terrain_Model/TIFF/BCI_whole_2023_05_26_dtm.tif"

# DSM (1.1 GB)
wget -O ~/data-store/data/output/smithsonian/raw/dsm/BCI_whole_2023_05_26_dsm.tif \
  "${BASE_URL}/06_Digital_Surface_Model/TIFF/BCI_whole_2023_05_26_dsm.tif"
```

### Download All LAZ Files (Optional)

```bash
# Download classified LAZ tiles (~5-10 GB total)
LAZ_URL="${BASE_URL}/03_LAZ_Classified"

# Get file list and download
wget -r -np -nH --cut-dirs=4 -A "*.laz" \
  -P ~/data-store/data/output/smithsonian/raw/laz/ \
  "${LAZ_URL}/"
```

## Dependencies

Uses the same 3DEP conda environment with additions:

```yaml
# Additional packages for BCI analysis
dependencies:
  - pdal           # Point cloud processing
  - python-pdal
  - geopandas      # Geospatial data
  - rioxarray      # Raster I/O
  - rio-cogeo      # COG conversion
  - scikit-image   # Fractal analysis
  - laspy          # Alternative LAZ reader
```

## Scientific Context

### Barro Colorado Island Research

- **Established:** 1923 as biological reserve
- **50-ha Plot:** Established 1980, all trees ≥1cm DBH mapped and identified (~300,000 stems)
- **Key Research:** Forest dynamics, carbon cycling, biodiversity, ecological modeling

### Expected Findings

Based on tropical forest structure:
- **Canopy Height:** 20-45m typical, emergents to ~50m
- **Fractal Dimension:** Expected higher than temperate forests due to:
  - Multi-layered canopy structure
  - High species diversity (~300 tree species)
  - Complex vertical stratification
- **Gap Dynamics:** Tropical forests have characteristic gap structure

### Comparison with 3DEP Sites

| Metric | BCI (Tropical) | Redwood (Temperate) | Boreal (Cold) |
|--------|----------------|---------------------|---------------|
| Max Height | ~50m | ~115m | ~30m |
| Canopy Layers | 3-4 | 1-2 | 1 |
| Species Diversity | High | Low | Low |
| Expected Fractal D | Higher | Medium | Lower |

## Download Status (Completed)

**Total Downloaded: 11 GB**

```
~/data-store/data/output/smithsonian/raw/
├── chm/
│   └── BCI_whole_2023_05_26_chm.tif     (1.1 GB)
├── dtm/
│   └── BCI_whole_2023_05_26_dtm.tif     (1.1 GB)
├── dsm/
│   └── BCI_whole_2023_05_26_dsm.tif     (1.1 GB)
└── laz/
    └── 113 LAZ files                     (7.0 GB)
```

## Milestones

1. **Data Acquisition:** Download and validate all GeoTIFFs
2. **Initial Exploration:** Load, visualize, and assess CHM quality
3. **Subset Extraction:** Define and extract AOIs for detailed analysis
4. **Fractal Analysis:** Compute box-counting dimensions and lacunarity
5. **Comparative Analysis:** Compare with US temperate forest results
6. **Documentation:** Generate figures and summary report

## References

1. **BCI Forest Dynamics Plot:** Hubbell, S.P. & Foster, R.B. (1983)
2. **Smithsonian ALS Data:** STRI Physical Monitoring Program
3. **3DEP Workflow:** OpenTopography OT_3DEP_Workflows
4. **Fractal Forest Analysis:** Methods adapted from fractal-notebooks project
