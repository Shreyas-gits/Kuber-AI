"""Tool loader for mcp_server."""

import logging
import os

from mcp.server.fastmcp import FastMCP

from ..connectors.kubernetes_connector import KubernetesAPIConnector
from ..models.kubernetes_read_tool_model import KubernetesReadTool
from ..tools.kubernetes_read_tool import kubernetes_read

logger = logging.getLogger(__name__)


def register_kubernetes_tools(mcp: FastMCP):
    """Register Kubernetes API tools with the MCP server."""
    env = os.environ.get("ENV", "DEVELOPMENT").strip('"').upper()

    logger.info("🔌 Initializing Kubernetes API Client.")
    if env == "DEVELOPMENT":
        kubenetes_config_file = os.environ.get("KUBERNETES_CONFIG_FILE", None)
        k8s_connector = KubernetesAPIConnector.from_config(kubenetes_config_file)
    else:
        k8s_connector = KubernetesAPIConnector()

    logger.info("🛠️ Registering Kubernetes API tools with the MCP server.")

    def kubernetes_read_tool(input: KubernetesReadTool) -> str:
        """Wrapper that uses dependency-injected connector."""
        result = kubernetes_read(
            resource_type=input.resource_type,
            namespace=input.namespace,
            label_selector=input.label_selector,
            k8s_connector=k8s_connector,
        )
        return result[0].text if result else "No response"

    mcp.tool(
        description=(
            "Use this tool to read information from the Kubernetes cluster. "
            "You can query resource types like pods, deployments, services, or namespaces. "
            "Arguments:\n"
            "- resource_type: (pods | deployments | services | namespaces)\n"
            "- namespace: Kubernetes namespace (optional for cluster-wide resources)\n"
            "- label_selector: Optional label selector for filtering (useful for pods)\n"
            "Example: To list all pods in the 'default' namespace with label '', "
            "set resource_type='pods', namespace='default', label_selector=''"
        )
    )(kubernetes_read_tool)
    logger.info("✅ Kubernetes API tools registered successfully.")
