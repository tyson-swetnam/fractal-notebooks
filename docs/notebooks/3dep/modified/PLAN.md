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

## Workflow

### Phase 1: CHM Generation

For each site, run `2_chm_user_aoi.ipynb` to generate:
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

For each CHM, run `3_chm_fractal_analysis.ipynb` to compute:
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
│   └── [18 more sites]/
├── fractal/
│   ├── sequoia_giant_forest/
│   │   ├── sequoia_giant_forest_fractal.json
│   │   ├── sequoia_giant_forest_boxcount.png
│   │   └── sequoia_giant_forest_lacunarity.png
│   └── [18 more sites]/
└── summary/
    ├── all_sites_chm_stats.csv
    └── all_sites_fractal_dims.csv
```

## Batch Processing Approach

### Option A: Sequential (Simple)
Process sites one at a time in priority order. Slower but simpler to debug.

### Option B: Parallel by Region (Recommended)
Process sites in parallel groups:
1. Pacific Northwest (5 sites)
2. Rocky Mountains/Southwest (4 sites)
3. Eastern Forests (4 sites)
4. Boreal/Northern (2 sites)
5. Southeastern (2 sites)
6. Research Sites (2 sites - some overlap)

### Option C: Full Parallel
Launch all 19 sites simultaneously. Fastest but requires significant memory/compute.

## Implementation Tasks

- [ ] Create batch processing script for CHM generation
- [ ] Modify `2_chm_user_aoi.ipynb` to accept site_id parameter
- [ ] Create batch processing script for fractal analysis
- [ ] Modify `3_chm_fractal_analysis.ipynb` to accept CHM path parameter
- [ ] Create summary aggregation script
- [ ] Add progress tracking and error handling
- [ ] Test with Priority 1 sites first
- [ ] Run full batch for all 19 sites
- [ ] Generate comparative analysis report

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
