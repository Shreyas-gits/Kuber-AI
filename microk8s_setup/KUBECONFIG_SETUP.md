# MicroK8s Kubeconfig Setup

This directory contains utilities to set up kubeconfig for connecting to a MicroK8s cluster.

## Quick Setup

1. **Install MicroK8s** (if not already installed):
   ```bash
   sudo snap install microk8s --classic
   ```

2. **Start MicroK8s**:
   ```bash
   microk8s start
   ```

3. **Generate kubeconfig**:
   ```bash
   ./generate-kubeconfig.sh
   ```

This will create a `kubeconfig-microk8s.yaml` file with the correct certificates and credentials.

## Usage

### Option 1: Use with Environment Variable
```bash
export KUBECONFIG=/path/to/kubeconfig-microk8s.yaml
kubectl get nodes
```

### Option 2: Merge with Existing Kubeconfig
```bash
KUBECONFIG=~/.kube/config:./kubeconfig-microk8s.yaml kubectl config view --flatten > ~/.kube/config.new
mv ~/.kube/config.new ~/.kube/config
```

### Option 3: Use Directly with kubectl
```bash
kubectl --kubeconfig=./kubeconfig-microk8s.yaml get nodes
```

## Configuration Priority

The Kubernetes connector will try to load configuration in this order:

1. **In-cluster config** (if running inside a Kubernetes pod)
2. **MicroK8s kubeconfig** (`kubeconfig-microk8s.yaml` in the mcp_server directory)
3. **Default kubeconfig** (usually `~/.kube/config`)

## MicroK8s Specific Notes

- Default API server endpoint: `https://127.0.0.1:16443`
- MicroK8s uses self-signed certificates by default
- The cluster name is set to `microk8s-cluster`
- The context name is set to `microk8s`

## Troubleshooting

### MicroK8s Not Ready
```bash
microk8s status --wait-ready
```

### Check MicroK8s Services
```bash
microk8s kubectl get nodes
microk8s kubectl get pods --all-namespaces
```

### Verify Kubeconfig
```bash
kubectl --kubeconfig=./kubeconfig-microk8s.yaml cluster-info
```

### Enable MicroK8s Add-ons (Optional)
```bash
microk8s enable dns dashboard storage
```

## Security Considerations

- The kubeconfig file contains sensitive credentials
- Keep the file secure and don't commit it to version control
- Consider using RBAC to limit permissions for the service account
- For production, consider using token-based authentication instead of certificates

## Testing the Connection

After setting up the kubeconfig, you can test the connection:

```python
from connector.kubernetes_connector import KubernetesAPIConnector

# Initialize the connector
k8s = KubernetesAPIConnector()

# Test the connection
namespaces = k8s.get_namespaces()
print(namespaces)
```
