"""Tool loader for mcp_server."""

import logging
import os

from mcp.server.fastmcp import FastMCP

from ..connectors.kubernetes_connector import KubernetesAPIConnector
from ..tools.kubernetes_read_tool import kubernetes_read_tool

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

    def kubernetes_read_tool_wrapper(*args, **kwargs):
        return kubernetes_read_tool(*args, k8s_connector=k8s_connector, **kwargs)

    mcp.tool()(kubernetes_read_tool_wrapper)
    logger.info("✅ Kubernetes API tools registered successfully.")
