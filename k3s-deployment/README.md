# K3s Kubernetes Deployment

This folder contains Kubernetes manifests for deploying the fractal-notebooks repository as a remote, scalable service on a K3s cluster. The deployment creates a GPU-accelerated environment suitable for running Jupyter notebooks, Streamlit applications, and vector database operations on a virtual machine.

## Deployment Architecture

### Core Components
- **JupyterLab**: GPU-accelerated notebook environment for fractal computation
- **Weaviate**: Vector database for AI/ML workloads and data storage
- **Persistent Storage**: Local storage provisioning for data persistence
- **GPU Support**: NVIDIA device plugin integration for CUDA acceleration

### Kubernetes Resources
- **Deployments**: Application pod management and scaling
- **Services**: Internal networking and service discovery
- **PersistentVolumeClaims**: Data storage with node affinity
- **ConfigMaps**: Environment configuration management

## Manifest Files

### JupyterLab Deployment
- **`jupyterlab-deployment.yaml`** - Main JupyterLab container with PyTorch and CUDA support
- **`jupyterlab-service.yaml`** - ClusterIP service for internal access
- **`jupyterlab-pvc.yaml`** - Persistent storage for notebooks and data
- **`jupyterlab-to-weaviate.yaml`** - Service configuration for database connectivity

### Weaviate Vector Database  
- **`weaviate-deployment.yaml`** - Vector database for AI workloads
- **`weaviate-service.yaml`** - Database service endpoints
- **`weaviate-pvc.yaml`** - Persistent storage for vector data

### Infrastructure Support
- **`storageclass.yaml`** - Local storage class configuration
- **`nvidia-device-plugin-daemonset.yaml`** - GPU device plugin for CUDA access
- **`nvdp.yaml`** - NVIDIA device plugin configuration

## Step-by-Step Deployment Guide

### Prerequisites

1. **Install K3s with Docker Runtime**
```bash
# Install K3s with Docker support and disable Traefik
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--disable traefik" sh -s - --docker

# Set up kubeconfig for current user
sudo chmod 644 /etc/rancher/k3s/k3s.yaml
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Verify installation
kubectl get nodes
```

2. **Set up GPU Support (if using GPU nodes)**
```bash
# Create directories for GPU feature discovery
sudo mkdir -p /etc/kubernetes/node-feature-discovery/source.d/
sudo mkdir -p /etc/kubernetes/node-feature-discovery/features.d/

# Install NVIDIA device plugin using Helm
helm repo add nvdp https://nvidia.github.io/k8s-device-plugin
helm repo update
helm upgrade --install --set gfd.enabled=true nvidia-device-plugin nvdp/nvidia-device-plugin \
  --version 0.14.0 --namespace nvidia-device-plugin --create-namespace \
  --set-file config.map.config=./nvdp.yaml

# Label GPU nodes (replace with your actual node name)
kubectl label nodes <your-gpu-node-name> nvidia.com/gpu.present=true
```

3. **Update Node Annotations**
Edit the PVC files to match your actual node name:
```bash
# Update both PVC files with your node name
sed -i 's/gpu06.cyverse.org/<your-actual-node-name>/g' jupyterlab-pvc.yaml
sed -i 's/gpu06.cyverse.org/<your-actual-node-name>/g' weaviate-pvc.yaml
```

### Deployment Steps

#### Step 1: Create Namespace and Storage
```bash
# Create the namespace
kubectl apply -f namespace.yaml

# Create the storage class
kubectl apply -f storageclass.yaml

# Verify namespace creation
kubectl get namespaces | grep ai-workloads
```

#### Step 2: Deploy GPU Support (Optional)
```bash
# Deploy NVIDIA device plugin DaemonSet
kubectl apply -f nvidia-device-plugin-daemonset.yaml

# Verify GPU plugin is running
kubectl get pods -n kube-system | grep nvidia
```

#### Step 3: Deploy Weaviate Vector Database
```bash
# Create Weaviate persistent volume claim
kubectl apply -f weaviate-pvc.yaml

# Deploy Weaviate
kubectl apply -f weaviate-deployment.yaml

# Create Weaviate service
kubectl apply -f weaviate-service.yaml

# Verify Weaviate deployment
kubectl get pods -n ai-workloads -l app=weaviate
kubectl logs -f deployment/weaviate -n ai-workloads
```

#### Step 4: Deploy JupyterLab
```bash
# Create JupyterLab persistent volume claim
kubectl apply -f jupyterlab-pvc.yaml

# Deploy JupyterLab
kubectl apply -f jupyterlab-deployment.yaml

# Create JupyterLab service
kubectl apply -f jupyterlab-service.yaml

# Apply network policy for Jupyter-Weaviate communication
kubectl apply -f jupyterlab-to-weaviate.yaml

# Verify JupyterLab deployment
kubectl get pods -n ai-workloads -l app=jupyterlab
kubectl logs -f deployment/jupyterlab -n ai-workloads
```

#### Step 5: Verify Complete Deployment
```bash
# Check all resources
kubectl get all -n ai-workloads

# Check persistent volumes
kubectl get pv,pvc -n ai-workloads

# Check GPU allocation (if using GPU)
kubectl describe nodes | grep -A 5 "Allocated resources"
```

### Access Applications

#### Method 1: NodePort Services (Recommended for VM deployment)
```bash
# Get node IP
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')
if [ -z "$NODE_IP" ]; then
  NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
fi

# Access JupyterLab (NodePort 30088)
echo "JupyterLab URL: http://$NODE_IP:30088"

# Access Weaviate (NodePort 30080)
echo "Weaviate URL: http://$NODE_IP:30080/v1"

# Access Weaviate gRPC (NodePort 30051)
echo "Weaviate gRPC: $NODE_IP:30051"
```

#### Method 2: Port Forwarding (for local testing)
```bash
# Port forward JupyterLab (runs in foreground)
kubectl port-forward service/jupyterlab 8888:8888 -n ai-workloads &

# Port forward Weaviate HTTP
kubectl port-forward service/weaviate 8080:8080 -n ai-workloads &

# Port forward Weaviate gRPC
kubectl port-forward service/weaviate 50051:50051 -n ai-workloads &

# Access locally
echo "JupyterLab: http://localhost:8888 (no password required)"
echo "Weaviate: http://localhost:8080/v1"
```

### One-Command Deployment

For experienced users, deploy everything at once:
```bash
# Deploy in correct order
kubectl apply -f namespace.yaml && \
kubectl apply -f storageclass.yaml && \
kubectl apply -f nvidia-device-plugin-daemonset.yaml && \
sleep 10 && \
kubectl apply -f weaviate-pvc.yaml && \
kubectl apply -f weaviate-deployment.yaml && \
kubectl apply -f weaviate-service.yaml && \
kubectl apply -f jupyterlab-pvc.yaml && \
kubectl apply -f jupyterlab-deployment.yaml && \
kubectl apply -f jupyterlab-service.yaml && \
kubectl apply -f jupyterlab-to-weaviate.yaml

# Wait for deployment and show status
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/weaviate -n ai-workloads
kubectl wait --for=condition=available --timeout=300s deployment/jupyterlab -n ai-workloads
kubectl get all -n ai-workloads
```

## Resource Allocation

### JupyterLab Resources
- **GPU**: 1 NVIDIA GPU (configurable)
- **CPU**: 2-16 cores with burstable limits  
- **Memory**: 4-64GB RAM allocation
- **Storage**: 5GB persistent volume

### Weaviate Resources  
- **CPU**: 1-4 cores (no GPU required)
- **Memory**: 2-8GB RAM allocation
- **Storage**: 10GB persistent volume

### Storage Configuration
- **Storage Class**: `local-storage` using rancher.io/local-path provisioner
- **Volume Binding**: `WaitForFirstConsumer` for optimal node placement
- **Reclaim Policy**: `Delete` (data will be lost when PVC is deleted)
- **Node Affinity**: Volumes bound to specific nodes via annotations

## Integration with Other Folders

### Relationship to `apps/`
- JupyterLab environment can run Streamlit applications from the `apps/` folder
- GPU acceleration enables real-time fractal rendering for complex applications
- Remote deployment allows multiple users to access applications simultaneously
- Container environment includes all dependencies from `apps/` requirements

### Relationship to `docs/`
- JupyterLab provides an environment for editing and running documentation notebooks
- MkDocs site can be served from within the cluster for documentation hosting
- Documentation build process can be automated within the Kubernetes environment
- Remote access enables collaborative documentation development

### Relationship to `docker/`
- Kubernetes deployments use containerized versions of applications
- JupyterLab container includes the same Python environment as Docker builds
- Container registry integration allows automated deployment of updated applications
- Scaling benefits from containerization strategies developed in `docker/` folder

### Relationship to Repository Root
- Persistent volumes mount the entire repository for development access
- Git integration within JupyterLab allows version control of notebooks and code
- Environment replication ensures consistent behavior between local and remote execution
- Backup and restore capabilities for research data and computational results

## Configuration Details

### Node Affinity and Tolerations
```yaml
nodeSelector:
  nvidia.com/gpu.present: "true"
tolerations:
  - key: "nvidia.com/gpu"
    operator: "Exists"
    effect: "NoSchedule"
```

### Persistent Storage Configuration
- **Storage Class**: `local-storage` for high-performance local disk access
- **Node Binding**: Specific node assignment for data locality
- **Access Mode**: `ReadWriteOnce` for single-node attachment
- **Reclaim Policy**: Data persistence across pod restarts

### Security Considerations
- **Password Authentication**: JupyterLab secured with SHA1 password hash
- **Network Policies**: ClusterIP services for internal-only access
- **Resource Limits**: Prevents resource exhaustion and ensures fair sharing
- **RBAC**: Kubernetes role-based access control for cluster security

## Monitoring and Management

### Health Checks
```bash
# Check pod status
kubectl get pods -n ai-workloads

# View logs
kubectl logs -f deployment/jupyterlab -n ai-workloads
kubectl logs -f deployment/weaviate -n ai-workloads

# Describe resources for troubleshooting
kubectl describe pod <pod-name> -n ai-workloads
```

### Scaling Operations
```bash
# Scale JupyterLab instances
kubectl scale deployment jupyterlab --replicas=2 -n ai-workloads

# Update deployment with new configuration
kubectl apply -f jupyterlab-deployment.yaml -n ai-workloads
```

### Cleanup
```bash
# Remove all resources
kubectl delete namespace ai-workloads

# Individual resource cleanup
kubectl delete -f k3s-deployment/ -n ai-workloads
```

## Troubleshooting

### Common Issues

#### Pods Stuck in Pending State
```bash
# Check pod events for scheduling issues
kubectl describe pod <pod-name> -n ai-workloads

# Common causes:
# - Insufficient resources (CPU/Memory/GPU)
# - Node affinity constraints  
# - Missing storage class or PVC binding issues
# - GPU node labels missing
```

#### GPU Not Available
```bash
# Verify NVIDIA device plugin is running
kubectl get pods -n nvidia-device-plugin

# Check GPU node labels
kubectl get nodes --show-labels | grep gpu

# Label GPU nodes if missing
kubectl label nodes <node-name> nvidia.com/gpu.present=true

# Check GPU resources on nodes
kubectl describe nodes | grep -A 10 "Allocated resources"
```

#### Persistent Volume Issues
```bash
# Check PVC status
kubectl get pvc -n ai-workloads

# Check storage class
kubectl get storageclass

# Check if local-path provisioner is running
kubectl get pods -n kube-system | grep local-path

# Check node annotations match actual node names
kubectl get nodes
```

#### Service Connectivity Problems
```bash
# Check service endpoints
kubectl get endpoints -n ai-workloads

# Test internal connectivity
kubectl run test-pod --image=curlimages/curl -i --tty --rm -- sh
# Inside pod: curl http://weaviate.ai-workloads.svc.cluster.local:8080/v1

# Check network policies
kubectl get networkpolicies -n ai-workloads
```

#### Application Logs and Debugging
```bash
# Check JupyterLab logs
kubectl logs deployment/jupyterlab -n ai-workloads

# Check Weaviate logs  
kubectl logs deployment/weaviate -n ai-workloads

# Get shell access to troubleshoot
kubectl exec -it deployment/jupyterlab -n ai-workloads -- /bin/bash

# Check GPU access from within container
kubectl exec -it deployment/jupyterlab -n ai-workloads -- nvidia-smi
```

### Resource Monitoring
```bash
# Check overall resource usage
kubectl top pods -n ai-workloads
kubectl top nodes

# Check detailed node resources
kubectl describe nodes

# Monitor GPU utilization  
kubectl exec -it deployment/jupyterlab -n ai-workloads -- nvidia-smi

# Watch pod status in real-time
kubectl get pods -n ai-workloads -w
```

### Performance Optimization
```bash
# Check if pods are CPU/Memory throttled
kubectl describe pod <pod-name> -n ai-workloads | grep -A 5 "Limits\|Requests"

# Monitor resource usage over time
kubectl top pods -n ai-workloads --containers

# Check storage performance
kubectl exec -it deployment/jupyterlab -n ai-workloads -- df -h
```