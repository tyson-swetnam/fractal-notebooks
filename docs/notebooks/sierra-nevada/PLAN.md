# Sierra Nevada Giant Forest LiDAR Analysis Project

## Project Overview

Analyze Airborne Laser Scanning (ALS) data from the **Giant Forest in Sequoia National Park**, California, collected in 2022 as part of the USGS 3DEP program. This project follows the fractal-notebooks workflow framework established for the Smithsonian BCI analysis.

**Data Source:** [USGS 3DEP - CA Sierra Nevada 2022](https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CA_SierraNevada_B22/CA_SierraNevada_9_2022/)

**Study Site:**
- **Location:** Giant Forest, Sequoia National Park, California
- **Coordinates:** Approximately 36.56°N, -118.75°W (center of Giant Forest)
- **Forest Type:** Mixed conifer forest with giant sequoia (*Sequoiadendron giganteum*)
- **Significance:** Home to the world's largest trees by volume; General Sherman Tree
- **Expected Canopy Height:** Up to ~85m for tallest giant sequoias

## Target Area: Giant Forest

### Geographic Bounds (Approximate)
- **Northwest Corner:** 36.58°N, -118.78°W
- **Southeast Corner:** 36.54°N, -118.72°W
- **UTM Zone 11N (EPSG:32611) Bounds:**
  - Easting: ~333,000 to 340,000
  - Northing: ~4,045,000 to 4,052,000

### Key Landmarks
- **General Sherman Tree:** 36.5819°N, -118.7514°W
- **Congress Trail:** 36.5800°N, -118.7550°W
- **Moro Rock:** 36.5458°N, -118.7647°W
- **Crescent Meadow:** 36.5536°N, -118.7450°W

## Data Acquisition

### USGS 3DEP Source Structure
```
https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CA_SierraNevada_B22/CA_SierraNevada_9_2022/
├── LAZ/                    # Point cloud tiles in LAZ format
├── browse/                 # Preview/visualization files
├── metadata/               # Dataset documentation
└── 0_file_download_links.txt  # Master download list
```

### Tile Identification Strategy

USGS 3DEP tiles typically use USNG (US National Grid) or UTM-based naming. To identify tiles covering Giant Forest:

1. **Download the file list:**
   ```bash
   wget -O ~/data-store/data/output/sierra-nevada/raw/0_file_download_links.txt \
     "https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CA_SierraNevada_B22/CA_SierraNevada_9_2022/0_file_download_links.txt"
   ```

2. **Parse tile names** - Expected format: `USGS_LPC_CA_SierraNevada_9_2022_<TILEID>.laz`
   - TILEID may be USNG grid reference (e.g., "11SKA1234") or UTM coordinates

3. **Use USGS National Map** to cross-reference tile coverage:
   - https://apps.nationalmap.gov/lidar-explorer/

### Expected Data Products

Unlike BCI (which had pre-computed CHM/DTM/DSM), USGS 3DEP provides only LAZ point clouds. We must generate raster products from point clouds.

| Product | Source | Processing Required |
|---------|--------|---------------------|
| **LAZ** | USGS download | None (raw data) |
| **DEM** | Generate from LAZ | Ground classification + interpolation |
| **DSM** | Generate from LAZ | First returns + interpolation |
| **CHM** | Compute | CHM = DSM - DEM |

## Output Directory Structure

```
~/data-store/data/output/sierra-nevada/
├── raw/
│   ├── laz/                    # Downloaded LAZ point clouds
│   ├── dem/                    # (unused - no pre-computed DEM)
│   ├── dsm/                    # (unused - no pre-computed DSM)
│   └── chm/                    # (unused - no pre-computed CHM)
├── processed/
│   ├── dem/                    # Generated DEM GeoTIFFs
│   ├── dsm/                    # Generated DSM GeoTIFFs
│   ├── chm/                    # Generated CHM GeoTIFFs
│   └── cog/                    # Cloud-Optimized GeoTIFFs
└── analysis/
    ├── chm_exploration/        # Height statistics, visualizations
    ├── fractal/                # Fractal dimension results
    └── fractal_hypotheses/     # Extended hypothesis testing
```

## Processing Pipeline

### Phase 1: Data Acquisition (Notebook 1)

#### `1_download_data.ipynb`

**Objectives:**
- [ ] Download USGS file list and identify Giant Forest tiles
- [ ] Calculate tile coverage using bounding box
- [ ] Download selected LAZ tiles (estimate: 10-20 tiles, ~10-50 GB)
- [ ] Validate downloads (file integrity)

**Key Steps:**
1. Parse `0_file_download_links.txt` for LAZ file URLs
2. Filter tiles by geographic bounds (UTM Zone 11N coordinates)
3. Download tiles using wget/curl with progress tracking
4. Log download metadata and checksums

**Expected Tile Coverage:**
- Giant Forest area: ~7km x 7km = ~49 km²
- Tile size: likely 1km x 1km = 1 km²
- Expected tiles: ~50-100 tiles depending on tile size

### Phase 2: Point Cloud Processing (Notebook 2)

#### `2_laz_to_raster.ipynb`

**Objectives:**
- [ ] Generate DEM from ground-classified points
- [ ] Generate DSM from first returns
- [ ] Compute CHM = DSM - DEM
- [ ] Convert to Cloud-Optimized GeoTIFF (COG) format

**Processing with PDAL:**
```python
import pdal
import json

# DEM pipeline (ground points only)
dem_pipeline = {
    "pipeline": [
        {
            "type": "readers.las",
            "filename": "input.laz"
        },
        {
            "type": "filters.range",
            "limits": "Classification[2:2]"  # Ground class
        },
        {
            "type": "writers.gdal",
            "filename": "dem.tif",
            "gdaldriver": "GTiff",
            "output_type": "min",  # or "idw" for interpolation
            "resolution": 0.5,
            "data_type": "float32"
        }
    ]
}

# DSM pipeline (first returns)
dsm_pipeline = {
    "pipeline": [
        {
            "type": "readers.las",
            "filename": "input.laz"
        },
        {
            "type": "filters.range",
            "limits": "ReturnNumber[1:1]"  # First returns
        },
        {
            "type": "writers.gdal",
            "filename": "dsm.tif",
            "gdaldriver": "GTiff",
            "output_type": "max",
            "resolution": 0.5,
            "data_type": "float32"
        }
    ]
}
```

**Processing with GDAL/rio-cogeo:**
```bash
# Convert to Cloud-Optimized GeoTIFF
rio cogeo create dem.tif dem_cog.tif --overview-level 5
rio cogeo create dsm.tif dsm_cog.tif --overview-level 5
rio cogeo create chm.tif chm_cog.tif --overview-level 5
```

**Target Resolution:** 0.5m (matches Smithsonian BCI for comparison)
**CRS:** EPSG:32611 (UTM Zone 11N)

### Phase 3: CHM Exploration (Notebook 3)

#### `3_chm_exploration.ipynb`

Adapt `smithsonian/1_chm_exploration.ipynb` for Sierra Nevada:

**Objectives:**
- [ ] Load and visualize CHM
- [ ] Calculate height statistics (min, max, mean, P95, P99)
- [ ] Vertical structure analysis (understory, canopy, emergent layers)
- [ ] Data quality assessment (NoData, artifacts)
- [ ] Compare with published giant sequoia measurements

**Expected Statistics:**
- **Giant Sequoias:** 60-85m typical height
- **Mixed Conifers:** 30-50m (sugar pine, white fir, incense cedar)
- **Understory:** Dense in meadow edges, sparse under sequoia canopy

### Phase 4: Fractal Analysis (Notebook 4)

#### `4_fractal_analysis.ipynb`

Adapt `smithsonian/2_fractal_analysis.ipynb` for Sierra Nevada:

**Hypotheses to Test:**

**H1: Optimal Filling (Self-Affine Surface Complexity)**
- Method: Differential Box Counting (DBC)
- Expected: Lower D than tropical (less vertical layering)

**H2: Scale Invariance (Power-Law Gap Scaling)**
- Method: Lacunarity analysis
- Expected: Different pattern due to fire history, giant sequoia spacing

**H3: Gap Size Distribution**
- Method: Power-law fitting on gap CCDFs
- Expected: Fire-created gaps may differ from tropical gap dynamics

**H4: Emergent Tree Spacing**
- Method: Clark-Evans R statistic
- Expected: Giant sequoias may show regular spacing (fire-competition)

### Phase 5: Comparative Analysis (Notebook 5)

#### `5_comparative_analysis.ipynb`

Compare Giant Forest with:
- **Smithsonian BCI** (tropical moist forest)
- **Other 3DEP sites** (redwoods, boreal, temperate deciduous)

| Metric | Giant Forest | BCI (Expected) |
|--------|--------------|----------------|
| Max Height | ~85m | ~50m |
| Mean Height | ~35m | ~20m |
| Canopy Layers | 2-3 | 3-4 |
| Gap Dynamics | Fire-influenced | Treefall |
| Fractal D | Lower? | 2.45 |

## Dependencies

Same as Smithsonian BCI analysis:

```yaml
dependencies:
  - pdal
  - python-pdal
  - geopandas
  - rioxarray
  - rio-cogeo
  - scikit-image
  - laspy
  - numpy
  - matplotlib
  - scipy
```

## Download Commands

### Step 1: Get File List
```bash
cd ~/data-store/data/output/sierra-nevada/raw/
wget "https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CA_SierraNevada_B22/CA_SierraNevada_9_2022/0_file_download_links.txt"
```

### Step 2: Filter for Giant Forest Tiles
```bash
# Once tile naming is understood, filter by coordinate range
# Example for UTM-based naming:
grep -E "11S.*(333|334|335|336|337|338|339|340)" 0_file_download_links.txt | \
  grep -E ".*(4045|4046|4047|4048|4049|4050|4051|4052)" > giant_forest_tiles.txt
```

### Step 3: Download Tiles
```bash
cd ~/data-store/data/output/sierra-nevada/raw/laz/
wget -i giant_forest_tiles.txt --continue --progress=dot:giga
```

## Milestones

### Session 1: Data Acquisition
- [ ] Download file list and analyze tile naming convention
- [ ] Identify tiles covering Giant Forest area
- [ ] Begin LAZ downloads (may span multiple sessions due to size)
- [ ] Create download tracking/resumption script

### Session 2: Point Cloud Processing
- [ ] Complete LAZ downloads
- [ ] Process LAZ → DEM (ground points)
- [ ] Process LAZ → DSM (first returns)
- [ ] Compute CHM = DSM - DEM
- [ ] Convert to Cloud-Optimized GeoTIFF

### Session 3: CHM Exploration
- [ ] Load and visualize whole-area CHM
- [ ] Calculate height statistics
- [ ] Assess data quality
- [ ] Generate exploration visualizations

### Session 4: Fractal Analysis
- [ ] Run H1-H4 hypothesis tests
- [ ] Compare with BCI results
- [ ] Document findings

### Session 5: Comparative Analysis
- [ ] Cross-forest comparison (Giant Forest vs BCI vs others)
- [ ] Publication-quality figures
- [ ] Summary report

## Scientific Context

### Giant Sequoia Forest Structure

Giant sequoias (*Sequoiadendron giganteum*) are:
- **Tallest:** Up to 85m (General Sherman: 83.8m)
- **Largest by volume:** General Sherman = 1,487 m³
- **Fire-adapted:** Thick bark (30-60cm), fire-dependent regeneration
- **Spacing:** Often widely spaced due to fire competition
- **Associated species:** Sugar pine, white fir, incense cedar, giant chinquapin

### Expected Structural Differences from Tropical Forest

| Feature | Giant Forest | BCI Tropical |
|---------|--------------|--------------|
| Canopy Layers | 2-3 | 3-4 |
| Gap Origin | Fire, insects | Treefall |
| Tree Spacing | Regular (fire) | Clustered |
| Height Range | 0-85m | 0-50m |
| Species Diversity | Low (~12 tree species) | High (~300 species) |
| Fractal Dimension | Expected lower | 2.45 |

### Research Questions

1. **Fire Effects:** How do fire scars and burned areas affect fractal dimension?
2. **Giant Tree Spacing:** Do sequoias show regular spacing patterns (fire competition)?
3. **Vertical Structure:** Is the 2-3 layer structure evident in CHM?
4. **Gap Dynamics:** Are gaps larger/more regular than tropical gaps?

## References

1. **USGS 3DEP:** https://www.usgs.gov/core-science-systems/ngp/3dep
2. **Giant Sequoia Ecology:** Stephenson, N.L. (1996). Ecology and management of giant sequoia groves. Sierra Nevada Ecosystem Project: Final Report to Congress.
3. **Sequoia Fire History:** Swetnam, T.W. (1993). Fire history and climate change in giant sequoia groves.
4. **LiDAR Processing:** PDAL Contributors. Point Data Abstraction Library. https://pdal.io/

## Status Tracking

| Phase | Status | Notes |
|-------|--------|-------|
| Project Setup | ✅ Complete | Folder structure created |
| Data Acquisition | 🔲 Not Started | Need to download file list |
| Point Cloud Processing | 🔲 Not Started | Awaiting LAZ downloads |
| CHM Exploration | 🔲 Not Started | Awaiting CHM generation |
| Fractal Analysis | 🔲 Not Started | Awaiting CHM |
| Comparative Analysis | 🔲 Not Started | Awaiting fractal results |

---

*Last Updated: December 25, 2025*
