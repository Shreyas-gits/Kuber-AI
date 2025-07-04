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

# Generate kubeconfig file directly
microk8s config > kubeconfig-microk8s.yaml

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

