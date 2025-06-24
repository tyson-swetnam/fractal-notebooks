# Docker Containerization

This folder contains Docker configuration files for containerizing the fractal-notebooks applications, enabling consistent deployment across different environments and platforms. The containerization focuses on Streamlit applications with a complete scientific Python stack.

## Container Configuration

### Core Files
- **`Dockerfile`** - Multi-stage container definition for Streamlit applications
- **`requirements.txt`** - Python dependencies optimized for containerized deployment

### Container Specifications
- **Base Image**: `python:3.11-slim` for lightweight, secure foundation
- **Runtime Environment**: Streamlit web server with scientific computing libraries
- **Port Exposure**: Port 8501 for Streamlit application access
- **Working Directory**: `/app` with application code and dependencies

## Docker Image Features

### Scientific Python Stack
```dockerfile
# Core scientific computing libraries
numpy
matplotlib
plotly
scipy
numba

# Data manipulation and analysis
pandas
pillow
imageio

# Web application framework
streamlit

# Jupyter integration
ipykernel
ipywidgets
nbformat
```

### Optimizations
- **Layer Caching**: Optimized layer ordering for faster rebuilds
- **Security**: Non-root user execution and minimal attack surface
- **Size**: Slim base image with only necessary system dependencies
- **Performance**: Pre-compiled scientific libraries for faster startup

## Building and Running

### Local Build
```bash
# Build the container image
cd docker/
docker build -t fractal-app .

# Run with port mapping
docker run -p 8501:8501 fractal-app

# Run with volume mounting for development
docker run -p 8501:8501 -v /path/to/fractal-notebooks:/app fractal-app
```

### Development Mode
```bash
# Run with live code reloading
docker run -p 8501:8501 \
  -v $(pwd)/../apps:/app/apps \
  -v $(pwd)/../docs:/app/docs \
  fractal-app
```

### Production Deployment
```bash
# Build optimized production image
docker build --target production -t fractal-app:prod .

# Run with resource limits
docker run -d \
  --name fractal-production \
  --memory=2g \
  --cpus=2 \
  -p 8501:8501 \
  fractal-app:prod
```

## Integration with Other Folders

### Relationship to `apps/`
- **Primary Target**: Containerizes Streamlit applications from the `apps/` folder
- **Dependency Management**: Includes all required Python packages for fractal applications
- **Runtime Environment**: Provides consistent execution environment for all apps
- **Default Application**: Configured to run `apps/branching_tree.py` by default

### Relationship to `docs/`
- **Documentation Access**: Container can mount documentation for integrated viewing
- **Notebook Execution**: Jupyter kernel support enables notebook execution within container
- **Asset Serving**: Can serve documentation assets alongside applications
- **Development Workflow**: Supports documentation development within containerized environment

### Relationship to `k3s-deployment/`
- **Base Image**: Kubernetes deployments can use this Docker image as foundation
- **Registry Integration**: Image can be pushed to container registry for K8s deployment
- **Configuration Consistency**: Ensures identical runtime environment between local and K8s
- **Resource Specifications**: Container resource requirements inform K8s resource limits

### Relationship to Repository Root
- **Code Access**: Mounts entire repository for full application access
- **Version Control**: Git integration within container for development workflows
- **Configuration Files**: Access to root-level configuration files (requirements.txt, etc.)
- **Data Persistence**: Volume mounting for persistent data storage

## Container Variants

### Development Container
```dockerfile
# Extended with development tools
FROM fractal-app:base as development
RUN pip install --no-cache-dir jupyter lab code-server
EXPOSE 8888 8080
CMD ["jupyter", "lab", "--allow-root", "--ip=0.0.0.0"]
```

### Production Container
```dockerfile
# Optimized for production deployment
FROM fractal-app:base as production
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1
```

## Security Considerations

### Container Security
- **Non-Root Execution**: Applications run as unprivileged user
- **Minimal Base**: Slim base image reduces attack surface
- **Dependency Scanning**: Regular vulnerability scans of dependencies
- **Network Isolation**: Default network policies restrict unnecessary connections

### Runtime Security
```dockerfile
# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Set secure permissions
COPY --chmod=755 apps/ /app/apps/
COPY --chmod=644 requirements.txt /app/
```

## Performance Optimization

### Build Optimization
- **Multi-Stage Builds**: Separate build and runtime stages
- **Layer Caching**: Optimized COPY instruction ordering
- **Dependency Caching**: Requirements installed before code copy
- **Image Size**: Minimal runtime dependencies

### Runtime Optimization
```dockerfile
# Environment variables for performance
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV NUMBA_CACHE_DIR=/tmp/numba_cache

# Resource limits awareness
ENV STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
ENV STREAMLIT_SERVER_MAX_MESSAGE_SIZE=200
```

## Monitoring and Debugging

### Health Checks
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1
```

### Logging Configuration
```dockerfile
# Structured logging
ENV STREAMLIT_LOGGER_LEVEL=INFO
ENV PYTHONPATH=/app
VOLUME ["/app/logs"]
```

### Debugging Support
```bash
# Interactive debugging
docker run -it --entrypoint=/bin/bash fractal-app

# Log monitoring
docker logs -f fractal-app

# Resource monitoring
docker stats fractal-app
```

## Environment Variables

### Streamlit Configuration
- `STREAMLIT_SERVER_PORT` - Application port (default: 8501)
- `STREAMLIT_SERVER_ADDRESS` - Bind address (default: 0.0.0.0)
- `STREAMLIT_SERVER_HEADLESS` - Headless mode for production
- `STREAMLIT_BROWSER_GATHER_USAGE_STATS` - Disable usage tracking

### Python Environment
- `PYTHONPATH` - Python module search path
- `PYTHONUNBUFFERED` - Unbuffered output for logging
- `NUMBA_CACHE_DIR` - JIT compilation cache location

## Registry and Distribution

### Image Tagging Strategy
```bash
# Version tagging
docker tag fractal-app:latest fractal-app:v1.0.0
docker tag fractal-app:latest fractal-app:$(git rev-parse --short HEAD)

# Environment tagging
docker tag fractal-app:latest fractal-app:development
docker tag fractal-app:latest fractal-app:production
```

### Registry Push
```bash
# Push to registry
docker push registry.example.com/fractal-app:latest
docker push registry.example.com/fractal-app:v1.0.0
```