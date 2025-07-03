#!/usr/bin/env python3
"""Test script to verify Kubernetes connection using the KubernetesAPIConnector."""

import os
import sys

# Add src directory to path
src_path = os.path.join(os.path.dirname(__file__), "src")
sys.path.insert(0, src_path)

try:
    from src.connector.kubernetes_connector import KubernetesAPIConnector
except ImportError as e:
    print(f"❌ Failed to import KubernetesAPIConnector: {e}")
    print("Make sure you're running this script from the mcp_server directory")
    sys.exit(1)


def test_kubernetes_connection():
    """Test the Kubernetes connection."""
    print("🔍 Testing Kubernetes connection...")

    # Initialize the connector
    k8s = KubernetesAPIConnector()

    # Test 1: Get namespaces
    print("\n📋 Testing namespace retrieval...")
    namespaces = k8s.get_namespaces()
    if "error" in namespaces:
        print(f"❌ Failed to get namespaces: {namespaces['error']}")
        return False
    else:
        print(f"✅ Successfully retrieved {namespaces['total_count']} namespaces")
        for ns in namespaces["namespaces"][:3]:  # Show first 3
            print(f"   - {ns['name']} ({ns['status']})")

    # Test 2: Get pods in default namespace
    print("\n🚀 Testing pod retrieval...")
    pods = k8s.get_pods()
    if "error" in pods:
        print(f"❌ Failed to get pods: {pods['error']}")
    else:
        print(f"✅ Successfully retrieved {pods['total_count']} pods from default namespace")
        for pod in pods["pods"][:3]:  # Show first 3
            print(f"   - {pod['name']} ({pod['status']})")

    # Test 3: Get services
    print("\n🌐 Testing service retrieval...")
    services = k8s.get_services()
    if "error" in services:
        print(f"❌ Failed to get services: {services['error']}")
    else:
        print(f"✅ Successfully retrieved {services['total_count']} services from default namespace")
        for svc in services["services"][:3]:  # Show first 3
            print(f"   - {svc['name']} ({svc['type']})")

    # Test 4: Get deployments
    print("\n📦 Testing deployment retrieval...")
    deployments = k8s.get_deployments()
    if "error" in deployments:
        print(f"❌ Failed to get deployments: {deployments['error']}")
    else:
        print(f"✅ Successfully retrieved {deployments['total_count']} deployments from default namespace")
        for deploy in deployments["deployments"][:3]:  # Show first 3
            print(f"   - {deploy['name']} ({deploy['ready_replicas']}/{deploy['replicas']} ready)")

    print("\n🎉 Kubernetes connection test completed!")
    return True


if __name__ == "__main__":
    success = test_kubernetes_connection()
    sys.exit(0 if success else 1)
