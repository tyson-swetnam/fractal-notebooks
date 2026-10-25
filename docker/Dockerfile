# Streamlit fractal apps (apps/*.py). Build from the repository root:
#   docker build -f docker/Dockerfile -t fractal-app . && docker run -p 8501:8501 fractal-app
FROM python:3.11-slim

WORKDIR /app

# Scientific-Python stack used by the Streamlit apps (requirements-docs.txt is the docs toolchain, not this).
RUN pip install --no-cache-dir streamlit numpy scipy matplotlib plotly pillow imageio pandas shapely

COPY apps/ ./apps/

EXPOSE 8501

# tree_roots_3d.py is a Streamlit app; branching_tree.py (the previous CMD) is a plain matplotlib script.
CMD ["streamlit", "run", "apps/tree_roots_3d.py", "--server.address=0.0.0.0"]
