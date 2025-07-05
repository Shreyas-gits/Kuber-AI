# MicroK8s Setup

This document provides instructions for setting up a single-node Kubernetes cluster using MicroK8s for local development purposes.

## Quick Start Guide

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

The above script will generate a `kubeconfig-microk8s.yaml` file containing the necessary certificates and credentials.  
This kubeconfig file is required by the MCP server to connect to the Kubernetes API.
