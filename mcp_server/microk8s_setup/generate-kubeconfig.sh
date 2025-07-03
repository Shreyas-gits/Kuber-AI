#!/bin/bash

# Script to generate kubeconfig for MicroK8s cluster
# This script extracts the necessary certificates and credentials from MicroK8s

set -e

echo "Generating kubeconfig for MicroK8s cluster..."

# Check if MicroK8s is installed
if ! command -v microk8s &> /dev/null; then
    echo "Error: MicroK8s is not installed or not in PATH"
    exit 1
fi

# Check if MicroK8s is running
if ! microk8s status --wait-ready --timeout=10 &> /dev/null; then
    echo "Error: MicroK8s is not running or not ready"
    echo "Please start MicroK8s with: microk8s start"
    exit 1
fi

# Get MicroK8s config
MICROK8S_CONFIG=$(microk8s config)

# Extract server URL (default is https://127.0.0.1:16443)
SERVER_URL=$(echo "$MICROK8S_CONFIG" | grep -o 'server: https://[^[:space:]]*' | head -1 | cut -d' ' -f2)

# Extract certificate-authority-data
CA_DATA=$(echo "$MICROK8S_CONFIG" | grep 'certificate-authority-data:' | head -1 | cut -d' ' -f4)

# Extract client-certificate-data
CLIENT_CERT_DATA=$(echo "$MICROK8S_CONFIG" | grep 'client-certificate-data:' | head -1 | cut -d' ' -f4)

# Extract client-key-data
CLIENT_KEY_DATA=$(echo "$MICROK8S_CONFIG" | grep 'client-key-data:' | head -1 | cut -d' ' -f4)

# Generate kubeconfig file
cat > kubeconfig-microk8s.yaml << EOF
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: ${CA_DATA}
    server: ${SERVER_URL}
  name: microk8s-cluster
contexts:
- context:
    cluster: microk8s-cluster
    user: microk8s-admin
  name: microk8s
current-context: microk8s
kind: Config
preferences: {}
users:
- name: microk8s-admin
  user:
    client-certificate-data: ${CLIENT_CERT_DATA}
    client-key-data: ${CLIENT_KEY_DATA}
EOF

echo "✅ kubeconfig-microk8s.yaml generated successfully!"
echo "📁 Location: $(pwd)/kubeconfig-microk8s.yaml"
echo ""
echo "To use this kubeconfig:"
echo "  export KUBECONFIG=$(pwd)/kubeconfig-microk8s.yaml"
echo "  kubectl get nodes"
echo ""
echo "Or to merge with your existing kubeconfig:"
echo "  KUBECONFIG=~/.kube/config:$(pwd)/kubeconfig-microk8s.yaml kubectl config view --flatten > ~/.kube/config.new"
echo "  mv ~/.kube/config.new ~/.kube/config"
