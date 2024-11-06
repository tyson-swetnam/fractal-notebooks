# K3s Deployment: Weaviate and Jupyter Lab

This repository provides step-by-step instructions to deploy **Weaviate** and **Jupyter Lab** on a **K3s** Kubernetes cluster. Both applications are deployed within the `ai-workloads` namespace and utilize PersistentVolumeClaims (PVCs) for persistent storage.

---

## Prerequisites

Before you begin, ensure you have the following:

- **Kubernetes Cluster:** A running K3s cluster. Instructions are provided below.
- **kubectl Installed:** Ensure `kubectl` is installed and configured to interact with your K3s cluster.
- **Access to Cluster Nodes:** SSH or physical access to nodes if needed.
- **Sufficient Resources:** Ensure your cluster has enough CPU, memory, and GPU resources (if deploying GPU-intensive applications).

---

## 1. Install K3s

If you haven't installed K3s yet, follow these steps:

1. **Run the K3s Installation Script:**

   ```bash
   curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--disable traefik" sh -s - --docker
   ```

2. **Verify Installation:**

   ```bash
   sudo k3s kubectl get nodes
   ```

   You should see your node listed with the status `Ready`.

3. **Verify NVIDIA**

  ```bash
  sudo chmod 644 /etc/rancher/k3s/k3s.yaml
  sudo mkdir -p /etc/kubernetes/node-feature-discovery/source.d/
  sudo mkdir -p /etc/kubernetes/node-feature-discovery/features.d/

  export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
  helm repo add nvdp https://nvidia.github.io/k8s-device-plugin
  helm repo update
  helm upgrade --install --set gfd.enabled=true nvidia-device-plugin nvdp/nvidia-device-plugin --version 0.14.0 --namespace nvidia-device-plugin --create-namespace --set-file config.map.config=./nvdp.yaml
  ```
  
---

## 2. Create Namespace

Organize your deployments by creating a dedicated namespace.

```bash
sudo k3s kubectl create namespace ai-workloads
```

Verify the namespace creation:

```bash
sudo k3s kubectl get namespaces
```

You should see `ai-workloads` listed among the namespaces.

---

## 3. Deploy Weaviate

Weaviate is an open-source vector search engine.

### 3.1. Create PersistentVolumeClaim for Weaviate

files created in the Pods will be mounted in `/opt/local-path-provisioner`

Create a file named `weaviate-pvc.yaml` with the following content:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: weaviate-pvc
  namespace: ai-workloads
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 32Gi
  storageClassName: local-path
```

Apply the PVC:

```bash
sudo k3s kubectl apply -f weaviate-pvc.yaml -n ai-workloads
```

### 3.2. Apply Weaviate Deployment and Service

Create a file named `weaviate-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weaviate
  namespace: ai-workloads
  labels:
    app: weaviate
spec:
  replicas: 1
  selector:
    matchLabels:
      app: weaviate
  template:
    metadata:
      labels:
        app: weaviate
    spec:
      containers:
        - name: weaviate
          image: semitechnologies/weaviate:1.27.0
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8080
          env:
            - name: QUERY_DEFAULTS_LIMIT
              value: "100"
            - name: AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED
              value: "true"
            - name: PERSISTENCE_DATA_PATH
              value: "/var/lib/weaviate"
            - name: CLUSTER_GOSSIP_BIND_PORT
              value: "7000"
            - name: CLUSTER_DATA_BIND_PORT
              value: "7001"
            - name: RAFT_BOOTSTRAP_TIMEOUT
              value: "600"
            - name: GOGC
              value: "100"
          volumeMounts:
            - name: weaviate-data
              mountPath: /var/lib/weaviate
      volumes:
        - name: weaviate-data
          persistentVolumeClaim:
            claimName: weaviate-pvc
```

Create a file named `weaviate-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: weaviate
  namespace: ai-workloads
  labels:
    app: weaviate
spec:
  type: ClusterIP
  selector:
    app: weaviate
  ports:
    - name: http
      port: 8080
      targetPort: 8080
    - name: health
      port: 8888
      targetPort: 8888
```

Apply the Deployment and Service:

```bash
sudo k3s kubectl apply -f weaviate-deployment.yaml -n ai-workloads
sudo k3s kubectl apply -f weaviate-service.yaml -n ai-workloads
```

---

## 4. Deploy Jupyter Lab

Jupyter Lab provides an interactive development environment for notebooks, code, and data.

### 4.1. Create PersistentVolumeClaim for Jupyter Lab

Create a file named `jupyterlab-pvc.yaml`:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: jupyterlab-pvc
  namespace: ai-workloads
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: local-path
```

Apply the PVC:

```bash
sudo k3s kubectl apply -f jupyterlab-pvc.yaml -n ai-workloads
```

### 4.2. Apply Jupyter Lab Deployment and Service

Create a file named `jupyterlab-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jupyterlab
  namespace: ai-workloads
  labels:
    app: jupyterlab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jupyterlab
  template:
    metadata:
      labels:
        app: jupyterlab
    spec:
      containers:
        - name: jupyterlab
          image: quay.io/jupyter/pytorch-notebook:cuda12-latest
          imagePullPolicy: IfNotPresent
          args:
            - start-notebook.sh
          env:
            - name: JUPYTER_ENABLE_LAB
              value: "yes"
            - name: JUPYTER_PASSWORD
              value: "sha1:abcd1234efgh5678ijkl9101mnopqrstu" # Replace with your generated hash
          ports:
            - containerPort: 8888
            - containerPort: 8080
          resources:
            requests:
              cpu: "2"
              memory: "4Gi"
              nvidia.com/gpu: "2"
            limits:
              cpu: "16"
              memory: "64Gi"
              nvidia.com/gpu: "2"
          volumeMounts:
            - name: jupyterlab-data
              mountPath: /home/jovyan
      volumes:
        - name: jupyterlab-data
          persistentVolumeClaim:
            claimName: jupyterlab-pvc
      nodeSelector:
        nvidia.com/gpu.present: "true"
      tolerations:
        - key: "nvidia.com/gpu"
          operator: "Exists"
          effect: "NoSchedule"
```

Create a file named `jupyterlab-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: jupyterlab
  namespace: ai-workloads
  labels:
    app: jupyterlab
spec:
  type: ClusterIP
  selector:
    app: jupyterlab
  ports:
    - name: http
      port: 8888
      targetPort: 8888
    - name: weaviate
      port: 8080
      targetPort: 8080
```

**Important:** Replace the `JUPYTER_PASSWORD` value with a secure password hash. To generate a password hash, use the following Python commands:

```python
from notebook.auth import passwd
print(passwd('your_secure_password'))
```

**Apply the Deployment and Service:**

```bash
sudo k3s kubectl apply -f jupyterlab-deployment.yaml -n ai-workloads
sudo k3s kubectl apply -f jupyterlab-service.yaml -n ai-workloads
```

---

## 5. Verify Deployments

Ensure that both Weaviate and Jupyter Lab are deployed successfully.

```bash
sudo k3s kubectl get all -n ai-workloads
```

**Expected Output:**

```
NAME                             READY   STATUS    RESTARTS   AGE
pod/jupyterlab-765bc9857-zk5jm   1/1     Running   0          5m
pod/weaviate-6678bf4f-g6j79      1/1     Running   0          6m

NAME                 TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)             AGE
service/jupyterlab   ClusterIP   10.43.182.60   <none>        8888/TCP,8080/TCP   6m
service/weaviate     ClusterIP   10.43.79.218   <none>        8080/TCP,8888/TCP   6m

NAME                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/jupyterlab   1/1     1            1           6m
deployment.apps/weaviate     1/1     1            1           6m

NAME                                   DESIRED   CURRENT   READY   AGE
replicaset.apps/jupyterlab-765bc9857   1         1         1       6m
replicaset.apps/weaviate-6678bf4f      1         1         1       6m
```

---

## 6. Troubleshooting

If your pods are not running as expected, follow these steps:

1. **Check Pod Status:**

   ```bash
   sudo k3s kubectl get pods -n ai-workloads
   ```

2. **Describe Pod for Details:**

   ```bash
   sudo k3s kubectl describe pod <pod-name> -n ai-workloads
   ```

3. **Check Logs:**

   ```bash
   sudo k3s kubectl logs <pod-name> -n ai-workloads
   ```

4. **Verify PVCs:**

   ```bash
   sudo k3s kubectl get pvc -n ai-workloads
   ```

5. **Ensure StorageClass and Provisioner are Correctly Configured.**

---

## 8. Security Best Practices

- **Secure Jupyter Lab:**
  - Always use a strong password.
  - Consider setting up HTTPS using Ingress with TLS.
  - Restrict access using Network Policies.

- **Limit Resource Usage:**
  - Define resource requests and limits to prevent resource contention.

- **Regular Updates:**
  - Keep your K3s cluster and applications up to date with security patches.

---

## 9. Cleanup

To remove the deployments and namespace:

```bash
sudo k3s kubectl delete namespace ai-workloads
```

**Note:** This will delete all resources within the `ai-workloads` namespace, including PVCs and their associated data.

---

## Finding Pods

### List All Pods

Retrieve all pods across all namespaces:

```bash
sudo k3s kubectl get pods --all-namespaces
```

### List Pods in a Specific Namespace

List pods within a particular namespace:

```bash
sudo k3s kubectl get pods -n <namespace>
```

*Replace `<namespace>` with the name of your namespace, e.g., `ai-workloads`.*

### Get Detailed Information About a Pod

Obtain detailed information, including events and status, for a specific pod:

```bash
sudo k3s kubectl describe pod <pod-name> -n <namespace>
```

*Replace `<pod-name>` and `<namespace>` accordingly.*

---

## Stopping (Deleting) Pods

### Delete a Specific Pod

Terminate a specific pod. Kubernetes will attempt to gracefully shut it down and may restart it based on the deployment configuration:

```bash
sudo k3s kubectl delete pod <pod-name> -n <namespace>
```

### Delete All Pods in a Namespace

Remove all pods within a specific namespace:

```bash
sudo k3s kubectl delete pods --all -n <namespace>
```

*Use with caution as this will disrupt all applications running in the namespace.*

---

## Finding Namespaces

### List All Namespaces

View all namespaces in the cluster:

```bash
kubectl get namespaces
```

### Get Detailed Information About a Namespace

Get comprehensive details about a specific namespace:

```bash
kubectl describe namespace <namespace>
```

*Replace `<namespace>` with the name of your namespace.*

---

## Stopping (Deleting) Namespaces

### Delete a Namespace

Remove an entire namespace and all its contained resources:

```bash
kubectl delete namespace <namespace>
```

*Note:* Deleting a namespace is irreversible and will remove all resources within it, including pods, services, and deployments.

---

## Additional Tips

- **Check Current Context and Namespace:**

  Ensure you are operating in the correct context and namespace:

  ```bash
  kubectl config current-context
  kubectl config view --minify | grep namespace:
  ```

- **Switch Namespace:**

  Temporarily switch the default namespace for your `kubectl` commands:

  ```bash
  kubectl config set-context --current --namespace=<namespace>
  ```

- **Force Delete a Stuck Namespace:**

  If a namespace is stuck in the `Terminating` state, you may need to remove its finalizers. **Proceed with caution**:

  ```bash
  kubectl get namespace <namespace> -o json > tmp.json
  # Edit tmp.json and remove the "finalizers" section
  kubectl replace --raw "/api/v1/namespaces/<namespace>/finalize" -f ./tmp.json
  ```

---

## References

- [kubectl Documentation](https://kubernetes.io/docs/reference/kubectl/)
- [Managing Kubernetes Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)
- [Managing Pods](https://kubernetes.io/docs/concepts/workloads/pods/)




---

## License

