#!/usr/bin/env python3
"""
Generate site-specific CHM and fractal analysis notebooks from templates.

This script:
1. Reads forest_sites.yaml
2. Creates sites/ directory structure
3. Generates CHM notebooks from 2_chm_user_aoi.ipynb template
4. Generates fractal notebooks from 3_chm_fractal_analysis.ipynb template
"""

import json
import yaml
from pathlib import Path
from datetime import datetime


def load_forest_sites(yaml_path):
    """Load forest sites configuration from YAML."""
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    return config['sites']


def create_site_directories(base_dir, sites):
    """Create directory structure for all sites."""
    sites_dir = base_dir / 'sites'
    sites_dir.mkdir(exist_ok=True)

    for site_id in sites.keys():
        site_dir = sites_dir / site_id
        site_dir.mkdir(exist_ok=True)
        print(f"  Created: {site_dir.relative_to(base_dir)}")

    return sites_dir


def load_notebook(path):
    """Load a Jupyter notebook as JSON."""
    with open(path, 'r') as f:
        return json.load(f)


def save_notebook(notebook, path):
    """Save a Jupyter notebook as JSON."""
    with open(path, 'w') as f:
        json.dump(notebook, f, indent=1)


def update_chm_notebook(template_notebook, site_id, site_config):
    """Update CHM template notebook with site-specific configuration."""
    notebook = json.loads(json.dumps(template_notebook))  # Deep copy

    # Find the configuration cell (typically cell 5 with SITE_NAME)
    # Look for the cell containing "SITE_NAME = " or "AOI_GEOJSON"
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']

            # Update the AOI configuration cell
            if 'AOI_GEOJSON' in source and 'SITE_NAME' in source:
                bbox = site_config['bbox']

                # Create new configuration cell
                new_source = f'''# Define AOI using GeoJSON
# {site_config['name']}, {site_config['state']}

AOI_GEOJSON = {{
  "type": "FeatureCollection",
  "features": [
    {{
      "type": "Feature",
      "properties": {{}},
      "geometry": {{
        "coordinates": [
          [
            [{bbox[0]}, {bbox[3]}],
            [{bbox[0]}, {bbox[1]}],
            [{bbox[2]}, {bbox[1]}],
            [{bbox[2]}, {bbox[3]}],
            [{bbox[0]}, {bbox[3]}]
          ]
        ],
        "type": "Polygon"
      }}
    }}
  ]
}}

SITE_NAME = "{site_id}"

# Parse GeoJSON and create AOI
feature = AOI_GEOJSON['features'][0]
AOI_GCS = shape(feature['geometry'])
AOI_EPSG3857 = gcs_to_proj(AOI_GCS)

# Calculate bounding box for reference
AOI_BBOX = list(AOI_GCS.bounds)  # [west, south, east, north]

print(f"Site: {{SITE_NAME}}")
print(f"Bounding box (WGS84): {{AOI_BBOX}}")
print(f"Area: {{AOI_EPSG3857.area / 1e6:.4f}} km²")
'''
                cell['source'] = new_source.split('\n')

    # Update the title cell
    for cell in notebook['cells']:
        if cell['cell_type'] == 'markdown':
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if 'Canopy Height Model (CHM) Generation' in source and '## Key Features' in source:
                cell['source'] = [
                    f'# CHM Generation: {site_config["name"]}\n',
                    '\n',
                    f'**Site:** {site_config["name"]}, {site_config["state"]}\n',
                    f'**Forest Type:** {site_config["forest_type"].replace("_", " ").title()}\n',
                    f'**Expected Max Height:** {site_config["expected_max_height_m"]}m\n',
                    '\n',
                    f'**Description:** {site_config["description"]}\n',
                    '\n',
                    'Generate Canopy Height Models from USGS 3D Elevation Program (3DEP) lidar data.\n',
                    '\n',
                    '**Modified from:** [OpenTopography OT_3DEP_Workflows](https://github.com/OpenTopography/OT_3DEP_Workflows)\n'
                ]
                break

    return notebook


def update_fractal_notebook(template_notebook, site_id, site_config):
    """Update fractal template notebook with site-specific configuration."""
    notebook = json.loads(json.dumps(template_notebook))  # Deep copy

    # Look for configuration cells and update them
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']

            # Update SITE_ID and paths
            if 'SITE_ID' in source and 'CHM_PATH' in source:
                new_source = f'''# Site Configuration
SITE_ID = "{site_id}"
SITE_NAME = "{site_config['name']}"
EXPECTED_MAX_HEIGHT = {site_config['expected_max_height_m']}  # meters

# Input/Output paths
CHM_PATH = Path("/home/jovyan/data-store/data/output/3dep/chm") / f"{{SITE_ID}}_chm.tif"
DEM_PATH = Path("/home/jovyan/data-store/data/output/3dep/chm") / f"{{SITE_ID}}_dem.tif"
FRACTAL_DIR = Path("/home/jovyan/data-store/data/output/3dep/fractal") / SITE_ID

# Create output directory
FRACTAL_DIR.mkdir(parents=True, exist_ok=True)

print(f"Site: {{SITE_NAME}}")
print(f"CHM input: {{CHM_PATH}}")
print(f"DEM input: {{DEM_PATH}}")
print(f"Output directory: {{FRACTAL_DIR}}")
'''
                cell['source'] = new_source.split('\n')

    # Update title
    for cell in notebook['cells']:
        if cell['cell_type'] == 'markdown':
            source = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if 'Fractal Analysis' in source and len(source) < 200:
                cell['source'] = [
                    f'# Fractal Analysis: {site_config["name"]}\n',
                    '\n',
                    f'**Site:** {site_config["name"]}, {site_config["state"]}\n',
                    f'**Forest Type:** {site_config["forest_type"].replace("_", " ").title()}\n',
                    '\n',
                    'Perform fractal dimension analysis on the generated CHM.\n'
                ]
                break

    return notebook


def main():
    """Main execution function."""
    print("="*60)
    print("GENERATING SITE-SPECIFIC NOTEBOOKS")
    print("="*60)
    print()

    # Paths
    base_dir = Path(__file__).parent
    yaml_path = base_dir.parent / 'forest_sites.yaml'
    chm_template_path = base_dir / '2_chm_user_aoi.ipynb'
    fractal_template_path = base_dir / '3_chm_fractal_analysis.ipynb'

    # Load configuration
    print("Loading forest sites configuration...")
    sites = load_forest_sites(yaml_path)
    print(f"  Found {len(sites)} sites\n")

    # Create directory structure
    print("Creating sites/ directory structure...")
    sites_dir = create_site_directories(base_dir, sites)
    print()

    # Load templates
    print("Loading template notebooks...")
    chm_template = load_notebook(chm_template_path)
    fractal_template = load_notebook(fractal_template_path)
    print("  CHM template loaded")
    print("  Fractal template loaded")
    print()

    # Generate notebooks for each site
    print("Generating site-specific notebooks...")
    print()

    for site_id, site_config in sites.items():
        print(f"[{site_id}]")
        print(f"  Name: {site_config['name']}")
        print(f"  State: {site_config['state']}")
        print(f"  Type: {site_config['forest_type']}")

        site_dir = sites_dir / site_id

        # Generate CHM notebook
        chm_notebook = update_chm_notebook(chm_template, site_id, site_config)
        chm_path = site_dir / f'chm_{site_id}.ipynb'
        save_notebook(chm_notebook, chm_path)
        print(f"  ✓ CHM notebook: {chm_path.relative_to(base_dir)}")

        # Generate fractal notebook
        fractal_notebook = update_fractal_notebook(fractal_template, site_id, site_config)
        fractal_path = site_dir / f'fractal_{site_id}.ipynb'
        save_notebook(fractal_notebook, fractal_path)
        print(f"  ✓ Fractal notebook: {fractal_path.relative_to(base_dir)}")

        print()

    print("="*60)
    print("GENERATION COMPLETE!")
    print("="*60)
    print(f"\nGenerated {len(sites) * 2} notebooks ({len(sites)} CHM + {len(sites)} fractal)")
    print(f"Output directory: {sites_dir.relative_to(base_dir.parent)}")


if __name__ == '__main__':
    main()
