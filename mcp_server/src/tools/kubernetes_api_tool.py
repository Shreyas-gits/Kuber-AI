"""Kubernetes API tool for mcp_server."""

import json
from typing import List

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from ..connector.kubernetes_connector import KubernetesAPIConnector


def register_kubernetes_tools(mcp: FastMCP):
    """Register Kubernetes API tools with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    k8s_tool = KubernetesAPIConnector()

    @mcp.tool()
    def kubernetes_api_request(
        action: str,
        resource_type: str = "pods",
        namespace: str = "default",
        resource_name: str = "",
        label_selector: str = "",
        lines: int = 100,
    ) -> List[TextContent]:
        """Send a request to the Kubernetes API server and return the response.

        Args:
            action: The action to perform (get, logs, describe)
            resource_type: The type of resource (pods, deployments, services, namespaces)
            namespace: The namespace to query (default: "default")
            resource_name: Specific resource name (for logs or describe actions)
            label_selector: Label selector to filter resources
            lines: Number of log lines to retrieve (for logs action)

        Returns:
            List of TextContent with the API response
        """
        try:
            if action == "get":
                if resource_type in ["pod", "pods"]:
                    result = k8s_tool.get_pods(namespace, label_selector if label_selector else None)
                elif resource_type in ["deployment", "deployments", "deploy"]:
                    result = k8s_tool.get_deployments(namespace)
                elif resource_type in ["service", "services", "svc"]:
                    result = k8s_tool.get_services(namespace)
                elif resource_type in ["namespace", "namespaces", "ns"]:
                    result = k8s_tool.get_namespaces()
                else:
                    result = {"error": f"Resource type '{resource_type}' not supported"}

            elif action == "logs":
                if not resource_name:
                    result = {"error": "Pod name is required for logs action"}
                else:
                    result = k8s_tool.get_pod_logs(resource_name, namespace, lines=lines)

            elif action == "kubectl":
                # For executing kubectl-like commands
                command = f"get {resource_type}"
                if resource_name:
                    command += f" {resource_name}"
                result = k8s_tool.execute_kubectl_command(command, namespace)

            else:
                result = {"error": f"Action '{action}' not supported"}

            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": f"Tool execution failed: {str(e)}"}, indent=2))]
