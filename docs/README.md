# Documentation Site

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.

This folder contains the MkDocs Material documentation site that provides comprehensive theoretical background, mathematical foundations, and educational content for fractal geometry and self-affine fractal simulations.

## Structure Overview

### Core Documentation Pages
- **`index.md`** - Main landing page and project overview
- **`introduction.md`** - Introduction to fractal geometry concepts  
- **`methods.md`** - Mathematical methods and algorithms
- **`results.md`** - Research findings and computational results
- **`discussion.md`** - Analysis and interpretation of results
- **`conclusion.md`** - Summary and future directions
- **`references.md`** - Academic citations and further reading

### Educational Content
- **`installation.md`** - Setup instructions for the entire repository
- **`dims.md`** - Dimensionality theory and fractal dimensions
- **`glossary.md`** - Mathematical terminology and definitions
- **`applications.md`** - Practical applications setup guide
- **`dbc.md`** - Differential Box Counting methodology
- **`tree_roots.md`** - 3D branching visualization techniques

### Interactive Notebooks
Located in `notebooks/` subdirectory:
- **`fractal_generators.ipynb`** - Core fractal generation algorithms
- **`fractals.ipynb`** - Self-similar fractal examples
- **`ferns.ipynb`** - Barnsley fern implementations
- **`dla.ipynb`** - Diffusion Limited Aggregation simulations
- **`dbc.ipynb`** - Differential Box Counting analysis
- **`zeta_space.ipynb`** - Riemann Zeta function visualizations (2D)
- **`zeta_3d.ipynb`** - Riemann Zeta function visualizations (3D)
- **`torch_test.ipynb`** - PyTorch integration testing

### Supporting Assets
- **`assets/`** - Images, diagrams, and visual aids
- **`stylesheets/extra.css`** - Custom styling for Material theme
- **`javascripts/mathjax.js`** - MathJax configuration for LaTeX rendering
- **`overrides/main.html`** - Template customizations

## Documentation Features

### Mathematical Rendering
- **MathJax Integration**: Full LaTeX equation support with inline and display math
- **Custom Styling**: Fractal-themed color schemes and typography
- **Interactive Equations**: Hover effects and equation numbering

### Jupyter Notebook Integration
- **Live Rendering**: Notebooks embedded directly in documentation
- **Source Code Access**: Toggle between rendered output and source code
- **Interactive Widgets**: Preserved notebook interactivity where possible

### Navigation Structure
- **Hierarchical Organization**: Theory → Methods → Results → Applications
- **Tabbed Interface**: Separate tabs for documentation and interactive notebooks
- **Search Functionality**: Full-text search across all content
- **Cross-References**: Links between related concepts and implementations

## Building and Serving

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Serve locally with live reload
python -m mkdocs serve
# Access at http://localhost:8000
```

### Production Build
```bash
# Build static site
python -m mkdocs build
# Output in site/ directory
```

### GitHub Pages Deployment
The site is configured for automatic deployment to GitHub Pages via GitHub Actions.

## Integration with Other Folders

### Relationship to `apps/`
- Documentation explains the mathematical theory behind Streamlit applications
- Provides educational context for interactive visualizations
- Links to specific applications that demonstrate documented concepts
- Serves as a reference guide for application users

### Relationship to `notebooks/`
- Jupyter notebooks are embedded directly in the documentation
- Notebooks provide hands-on examples of documented algorithms
- Documentation explains the theoretical background of notebook implementations
- Cross-references between explanatory text and executable code

### Relationship to `k3s-deployment/`
- Documentation can be served from the Kubernetes cluster
- JupyterLab deployment provides an environment for running embedded notebooks
- Remote access enables collaborative documentation editing

### Relationship to `docker/`
- Docker containers can serve the built documentation site
- Containerized deployment ensures consistent documentation rendering
- Supports documentation hosting alongside applications

## Configuration Details

### MkDocs Configuration (`mkdocs.yml`)
- **Theme**: Material theme with custom fractal color scheme
- **Plugins**: 
  - `mkdocs-jupyter` for notebook rendering
  - `mkdocstrings` for API documentation
  - `git-revision-date` for version tracking
- **Extensions**: 
  - PyMdown extensions for enhanced markdown
  - MathJax for mathematical notation
  - Code highlighting and syntax support

### Content Management
- **Markdown Format**: All documentation written in GitHub-flavored Markdown
- **Asset Organization**: Images and media files organized by topic
- **Version Control**: Git-based content management with revision tracking
- **Collaborative Editing**: Multiple author support with attribution

## Mathematical Content Standards

### LaTeX Notation
- Consistent mathematical notation throughout documentation
- Proper equation formatting and numbering
- Cross-references between equations and explanations

### Code Integration
- Syntax highlighting for Python, YAML, and shell commands
- Inline code snippets with proper escaping
- Code block annotations and explanations

### Visual Standards
- High-quality fractal images and diagrams
- Consistent color schemes matching the application outputs
- Accessible design with proper contrast ratios