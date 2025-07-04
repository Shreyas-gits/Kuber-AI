"""Kubernetes API tool for mcp_server.

This tool provides a function to read various Kubernetes resources using the KubernetesAPIConnector.
Supported resource types include pods, deployments, services, and namespaces.
The function returns the API response as a list of TextContent objects.
"""

import json
from typing import List

from mcp.types import TextContent

from ..connectors.kubernetes_connector import KubernetesAPIConnector

KubernetesAPIConnector.__doc__ = """
KubernetesAPIConnector is a singleton class that provides methods to interact with the Kubernetes API server.
It supports listing pods, deployments, services, namespaces, retrieving pod logs, and executing kubectl-like commands.
Use `from_config` to initialize with a kubeconfig file or default to in-cluster configuration.
"""


def kubernetes_read_tool(
    resource_type: str = "pods",
    namespace: str = "default",
    label_selector: str = "",
    k8s_connector: KubernetesAPIConnector = None,
) -> List[TextContent]:
    """Query the Kubernetes API server for information about a specific resource type.

    Args:
        resource_type (str): The type of resource to query (e.g., "pods", "deployments", "services", "namespaces").
        namespace (str): The namespace to query within (default: "default"). Ignored for cluster-wide resources.
        label_selector (str): Optional label selector to filter resources (only applies to pods).
        k8s_connector (KubernetesAPIConnector, optional): An instance of KubernetesAPIConnector to use for API calls.
            If not provided, a new instance will be created.

    Returns:
        List[TextContent]: A list containing a single TextContent object with the API response as formatted JSON.
            If an error occurs, the response will contain an error message.
    """
    if k8s_connector is None:
        k8s_connector = KubernetesAPIConnector()
    try:
        if resource_type in ["pod", "pods"]:
            result = k8s_connector.get_pods(namespace, label_selector if label_selector else None)
        elif resource_type in ["deployment", "deployments", "deploy"]:
            result = k8s_connector.get_deployments(namespace)
        elif resource_type in ["service", "services", "svc"]:
            result = k8s_connector.get_services(namespace)
        elif resource_type in ["namespace", "namespaces", "ns"]:
            result = k8s_connector.get_namespaces()
        else:
            result = {"error": f"Resource type '{resource_type}' not supported"}

        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": f"Tool execution failed: {str(e)}"}, indent=2))]
