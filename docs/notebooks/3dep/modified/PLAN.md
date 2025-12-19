# Plan: CHM Generation & Fractal Analysis for All Forest Sites

## Objective

Generate Canopy Height Models (CHM) and perform fractal dimension analysis for all 19 forest sites defined in `forest_sites.yaml`.

## Forest Sites (19 total)

### Priority 1 - High-Quality Research Sites (5)
| Site ID | Name | State | Forest Type | Expected Height |
|---------|------|-------|-------------|-----------------|
| `sequoia_giant_forest` | Sequoia Giant Forest | CA | Giant Sequoia | ~95m |
| `redwood_humboldt` | Humboldt Redwoods | CA | Coast Redwood | ~115m |
| `great_smoky_cove` | Great Smoky Mountains | TN | Mixed Mesophytic | ~55m |
| `harvard_forest` | Harvard Forest LTER | MA | Transition Hardwood | ~30m |
| `wind_river` | Wind River Exp. Forest | WA | Douglas-fir | ~65m |

### Priority 2 - Regional Representatives (7)
| Site ID | Name | State | Forest Type | Expected Height |
|---------|------|-------|-------------|-----------------|
| `olympic_hoh` | Olympic Hoh Rainforest | WA | Temperate Rainforest | ~75m |
| `tongass_mendenhall` | Tongass Mendenhall | AK | Temperate Rainforest | ~60m |
| `yellowstone_lodgepole` | Yellowstone Lodgepole | WY | Lodgepole Pine | ~30m |
| `coconino_ponderosa` | Coconino Ponderosa | AZ | Ponderosa Pine | ~40m |
| `white_mountain_northern` | White Mountain | NH | Northern Hardwood | ~35m |
| `ocala_longleaf` | Ocala Longleaf | FL | Longleaf Pine | ~35m |
| `niwot_ridge` | Niwot Ridge LTER | CO | Subalpine | ~20m |

### Priority 3 - Additional Sites (7)
| Site ID | Name | State | Forest Type | Expected Height |
|---------|------|-------|-------------|-----------------|
| `rocky_mountain_subalpine` | Rocky Mountain Subalpine | CO | Spruce-Fir | ~35m |
| `gila_mixed_conifer` | Gila Mixed Conifer | NM | Mixed Conifer | ~35m |
| `mark_twain_ozark` | Mark Twain Ozark | MO | Oak-Hickory | ~35m |
| `boundary_waters` | Boundary Waters | MN | Boreal Mixed | ~25m |
| `superior_old_growth` | Superior Old Growth | MN | Boreal Conifer | ~30m |
| `conecuh_longleaf` | Conecuh Longleaf | AL | Longleaf Pine | ~35m |

## Notebook Structure

Create a dedicated notebook for each site by copying templates:

```
modified/
├── 1_forest_sites_map.ipynb          # Interactive map (shared)
├── 2_chm_user_aoi.ipynb              # Template for CHM generation
├── 3_chm_fractal_analysis.ipynb      # Template for fractal analysis
│
├── sites/
│   ├── sequoia_giant_forest/
│   │   ├── chm_sequoia_giant_forest.ipynb
│   │   └── fractal_sequoia_giant_forest.ipynb
│   ├── redwood_humboldt/
│   │   ├── chm_redwood_humboldt.ipynb
│   │   └── fractal_redwood_humboldt.ipynb
│   ├── great_smoky_cove/
│   │   ├── chm_great_smoky_cove.ipynb
│   │   └── fractal_great_smoky_cove.ipynb
│   ├── harvard_forest/
│   │   ├── chm_harvard_forest.ipynb
│   │   └── fractal_harvard_forest.ipynb
│   ├── wind_river/
│   │   ├── chm_wind_river.ipynb
│   │   └── fractal_wind_river.ipynb
│   ├── olympic_hoh/
│   │   ├── chm_olympic_hoh.ipynb
│   │   └── fractal_olympic_hoh.ipynb
│   ├── tongass_mendenhall/
│   │   ├── chm_tongass_mendenhall.ipynb
│   │   └── fractal_tongass_mendenhall.ipynb
│   ├── yellowstone_lodgepole/
│   │   ├── chm_yellowstone_lodgepole.ipynb
│   │   └── fractal_yellowstone_lodgepole.ipynb
│   ├── coconino_ponderosa/
│   │   ├── chm_coconino_ponderosa.ipynb
│   │   └── fractal_coconino_ponderosa.ipynb
│   ├── white_mountain_northern/
│   │   ├── chm_white_mountain_northern.ipynb
│   │   └── fractal_white_mountain_northern.ipynb
│   ├── ocala_longleaf/
│   │   ├── chm_ocala_longleaf.ipynb
│   │   └── fractal_ocala_longleaf.ipynb
│   ├── niwot_ridge/
│   │   ├── chm_niwot_ridge.ipynb
│   │   └── fractal_niwot_ridge.ipynb
│   ├── rocky_mountain_subalpine/
│   │   ├── chm_rocky_mountain_subalpine.ipynb
│   │   └── fractal_rocky_mountain_subalpine.ipynb
│   ├── gila_mixed_conifer/
│   │   ├── chm_gila_mixed_conifer.ipynb
│   │   └── fractal_gila_mixed_conifer.ipynb
│   ├── mark_twain_ozark/
│   │   ├── chm_mark_twain_ozark.ipynb
│   │   └── fractal_mark_twain_ozark.ipynb
│   ├── boundary_waters/
│   │   ├── chm_boundary_waters.ipynb
│   │   └── fractal_boundary_waters.ipynb
│   ├── superior_old_growth/
│   │   ├── chm_superior_old_growth.ipynb
│   │   └── fractal_superior_old_growth.ipynb
│   └── conecuh_longleaf/
│       ├── chm_conecuh_longleaf.ipynb
│       └── fractal_conecuh_longleaf.ipynb
```

## Workflow

### Phase 1: CHM Generation

For each site, the `chm_<site_id>.ipynb` notebook generates:
- Digital Surface Model (DSM) - highest returns
- Digital Terrain Model (DTM) - ground returns
- Canopy Height Model (CHM = DSM - DTM)
- Metadata JSON with statistics

**Processing Parameters:**
- Resolution: 0.333m (if ≥12 pts/m²) or 0.5m (if <12 pts/m²)
- DSM method: max (highest point per cell)
- DTM method: min (lowest ground point per cell)
- No smoothing or interpolation

### Phase 2: Fractal Analysis

For each site, the `fractal_<site_id>.ipynb` notebook computes:
- Box-counting fractal dimension (2D surface complexity)
- Lacunarity analysis (gap distribution)
- Multiscale roughness metrics
- Height distribution statistics

## Output Structure

```
outputs/3dep/
├── chm/
│   ├── sequoia_giant_forest/
│   │   ├── sequoia_giant_forest_chm.tif
│   │   ├── sequoia_giant_forest_preview.png
│   │   └── sequoia_giant_forest_metadata.json
│   ├── redwood_humboldt/
│   │   └── ...
│   └── [17 more sites]/
├── fractal/
│   ├── sequoia_giant_forest/
│   │   ├── sequoia_giant_forest_fractal.json
│   │   ├── sequoia_giant_forest_boxcount.png
│   │   └── sequoia_giant_forest_lacunarity.png
│   └── [17 more sites]/
└── summary/
    ├── all_sites_chm_stats.csv
    └── all_sites_fractal_dims.csv
```

## Implementation Tasks

- [ ] Create `sites/` directory structure (19 site folders)
- [ ] Create script to generate site-specific CHM notebooks from template
- [ ] Create script to generate site-specific fractal notebooks from template
- [ ] Generate all 19 CHM notebooks with site-specific parameters
- [ ] Generate all 19 fractal notebooks with site-specific CHM paths
- [ ] Run Priority 1 sites first (5 sites) to validate workflow
- [ ] Run Priority 2 sites (7 sites)
- [ ] Run Priority 3 sites (7 sites)
- [ ] Create summary aggregation notebook
- [ ] Generate comparative analysis report

## Notebook Generation

Each site notebook will be created by:
1. Copying the template notebook
2. Updating the site configuration cell with:
   - `SITE_ID` - site identifier from YAML
   - `SITE_NAME` - human-readable name
   - `BBOX` - bounding box coordinates
   - `EXPECTED_MAX_HEIGHT` - for validation
3. Updating output paths to use site-specific directories

Example configuration cell for CHM notebook:
```python
# Site Configuration
SITE_ID = "sequoia_giant_forest"
SITE_NAME = "Sequoia Giant Forest"
BBOX = [-118.77, 36.55, -118.72, 36.60]
EXPECTED_MAX_HEIGHT = 95  # meters

# Output paths
OUTPUT_BASE = Path("outputs/3dep")
CHM_DIR = OUTPUT_BASE / "chm" / SITE_ID
```

Example configuration cell for fractal notebook:
```python
# Site Configuration
SITE_ID = "sequoia_giant_forest"
SITE_NAME = "Sequoia Giant Forest"

# Input/Output paths
CHM_PATH = Path("outputs/3dep/chm") / SITE_ID / f"{SITE_ID}_chm.tif"
FRACTAL_DIR = Path("outputs/3dep/fractal") / SITE_ID
```

## Expected Results

### CHM Statistics
- Height distributions by forest type
- Point density variations across regions
- Data quality assessment

### Fractal Dimensions
- Compare fractal dimensions across forest types
- Correlate with expected canopy structure:
  - Old-growth (complex, high D) vs plantation (uniform, low D)
  - Deciduous vs coniferous
  - Fire-maintained vs closed canopy

## Notes

- Some sites may lack 3DEP coverage - check availability first
- Alaska site (Tongass) may have limited lidar coverage
- LTER sites (Harvard, Niwot) have ground truth for validation
- Each notebook is self-contained and can be run independently
- Site notebooks can be run in parallel on multi-core systems
