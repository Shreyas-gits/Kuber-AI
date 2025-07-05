"""Kubernetes API connector for mcp_server.

This module provides a singleton class for interacting with the Kubernetes API server.
It supports retrieving pods, deployments, services, namespaces, pod logs, and executing
kubectl-like commands using the Kubernetes Python client.
"""

import logging
import os
from typing import Any, Dict, Optional

from kubernetes import client, config
from kubernetes.client.rest import ApiException

from ..utils.singleton import Singleton

logger = logging.getLogger(__name__)


class KubernetesAPIConnector(metaclass=Singleton):
    """Singleton connector for interacting with the Kubernetes API server.

    This class provides methods to:
      - List pods, deployments, services, and namespaces
      - Retrieve pod logs
      - Execute basic kubectl-like commands via the API
    """

    def __init__(self, config_loaded: bool = False):
        """Initialize the Kubernetes API connector and clients using in-cluster config."""
        if not config_loaded:
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes configuration")
        self.api_client = client.ApiClient()
        self.v1_client = client.CoreV1Api()
        self.apps_v1_client = client.AppsV1Api()

    @classmethod
    def from_config(cls, kubeconfig_path: str = None):
        """Create an instance using a kubeconfig file."""
        if kubeconfig_path and os.path.exists(kubeconfig_path):
            config.load_kube_config(config_file=kubeconfig_path)
            logger.info(f"Loaded kubeconfig from {kubeconfig_path}")
        else:
            logger.error(f"Failed to load kubeconfig check if the file exists: {kubeconfig_path}")
            raise RuntimeError("Could not load any Kubernetes configuration")
        return cls(config_loaded=True)

    def get_pods(self, namespace: str = "default", label_selector: Optional[str] = None) -> Dict[str, Any]:
        """Get pods from the specified namespace.

        Args:
            namespace: The namespace to query (default: "default")
            label_selector: Optional label selector to filter pods

        Returns:
            Dictionary containing pod information
        """
        if not self.v1_client:
            return {"error": "Kubernetes client not initialized"}

        try:
            pods = self.v1_client.list_namespaced_pod(namespace=namespace, label_selector=label_selector)

            pod_list = []
            for pod in pods.items:
                pod_info = {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "node": pod.spec.node_name,
                    "created": (
                        pod.metadata.creation_timestamp.isoformat() if pod.metadata.creation_timestamp else None
                    ),
                    "labels": pod.metadata.labels or {},
                    "containers": [
                        {
                            "name": container.name,
                            "image": container.image,
                            "ready": any(
                                cs.ready for cs in pod.status.container_statuses or [] if cs.name == container.name
                            ),
                        }
                        for container in pod.spec.containers
                    ],
                }
                pod_list.append(pod_info)

            return {"pods": pod_list, "total_count": len(pod_list)}

        except ApiException as e:
            return {"error": f"Kubernetes API error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}

    def get_deployments(self, namespace: str = "default") -> Dict[str, Any]:
        """Get deployments from the specified namespace.

        Args:
            namespace: The namespace to query (default: "default")

        Returns:
            Dictionary containing deployment information
        """
        if not self.apps_v1_client:
            return {"error": "Kubernetes client not initialized"}

        try:
            deployments = self.apps_v1_client.list_namespaced_deployment(namespace=namespace)

            deployment_list = []
            for deployment in deployments.items:
                deployment_info = {
                    "name": deployment.metadata.name,
                    "namespace": deployment.metadata.namespace,
                    "replicas": deployment.spec.replicas,
                    "ready_replicas": deployment.status.ready_replicas or 0,
                    "available_replicas": deployment.status.available_replicas or 0,
                    "updated_replicas": deployment.status.updated_replicas or 0,
                    "created": (
                        deployment.metadata.creation_timestamp.isoformat()
                        if deployment.metadata.creation_timestamp
                        else None
                    ),
                    "labels": deployment.metadata.labels or {},
                    "selector": deployment.spec.selector.match_labels or {},
                }
                deployment_list.append(deployment_info)

            return {"deployments": deployment_list, "total_count": len(deployment_list)}

        except ApiException as e:
            return {"error": f"Kubernetes API error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}

    def get_services(self, namespace: str = "default") -> Dict[str, Any]:
        """Get services from the specified namespace.

        Args:
            namespace: The namespace to query (default: "default")

        Returns:
            Dictionary containing service information
        """
        if not self.v1_client:
            return {"error": "Kubernetes client not initialized"}

        try:
            services = self.v1_client.list_namespaced_service(namespace=namespace)

            service_list = []
            for service in services.items:
                service_info = {
                    "name": service.metadata.name,
                    "namespace": service.metadata.namespace,
                    "type": service.spec.type,
                    "cluster_ip": service.spec.cluster_ip,
                    "external_ips": service.spec.external_i_ps or [],
                    "ports": [
                        {
                            "name": port.name,
                            "port": port.port,
                            "target_port": port.target_port,
                            "protocol": port.protocol,
                        }
                        for port in service.spec.ports or []
                    ],
                    "selector": service.spec.selector or {},
                    "created": (
                        service.metadata.creation_timestamp.isoformat() if service.metadata.creation_timestamp else None
                    ),
                    "labels": service.metadata.labels or {},
                }
                service_list.append(service_info)

            return {"services": service_list, "total_count": len(service_list)}

        except ApiException as e:
            return {"error": f"Kubernetes API error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}

    def get_namespaces(self) -> Dict[str, Any]:
        """Get all namespaces in the cluster.

        Returns:
            Dictionary containing namespace information
        """
        if not self.v1_client:
            return {"error": "Kubernetes client not initialized"}

        try:
            namespaces = self.v1_client.list_namespace()

            namespace_list = []
            for namespace in namespaces.items:
                namespace_info = {
                    "name": namespace.metadata.name,
                    "status": namespace.status.phase,
                    "created": (
                        namespace.metadata.creation_timestamp.isoformat()
                        if namespace.metadata.creation_timestamp
                        else None
                    ),
                    "labels": namespace.metadata.labels or {},
                }
                namespace_list.append(namespace_info)

            return {"namespaces": namespace_list, "total_count": len(namespace_list)}

        except ApiException as e:
            return {"error": f"Kubernetes API error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}

    def get_pod_logs(
        self,
        pod_name: str,
        namespace: str = "default",
        container: Optional[str] = None,
        lines: int = 100,
    ) -> Dict[str, Any]:
        """Get logs from a specific pod.

        Args:
            pod_name: Name of the pod
            namespace: The namespace of the pod (default: "default")
            container: Specific container name (if pod has multiple containers)
            lines: Number of lines to retrieve (default: 100)

        Returns:
            Dictionary containing pod logs
        """
        if not self.v1_client:
            return {"error": "Kubernetes client not initialized"}

        try:
            logs = self.v1_client.read_namespaced_pod_log(
                name=pod_name, namespace=namespace, container=container, tail_lines=lines
            )

            return {
                "pod_name": pod_name,
                "namespace": namespace,
                "container": container,
                "logs": logs,
                "lines_retrieved": len(logs.split("\n")) if logs else 0,
            }

        except ApiException as e:
            return {"error": f"Kubernetes API error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}

    def execute_kubectl_command(self, command: str, namespace: str = "default") -> Dict[str, Any]:
        """Execute a kubectl-like command using the Kubernetes API.

        Args:
            command: The kubectl command to execute (e.g., "get pods", "describe pod myapp")
            namespace: The namespace to execute the command in (default: "default")

        Returns:
            Dictionary containing the command result
        """
        if not self.v1_client:
            return {"error": "Kubernetes client not initialized"}

        # Parse the command
        parts = command.strip().split()
        if not parts:
            return {"error": "Empty command"}

        # Remove 'kubectl' if present
        if parts[0] == "kubectl":
            parts = parts[1:]

        if not parts:
            return {"error": "No command specified"}

        try:
            action = parts[0].lower()

            if action == "get":
                if len(parts) < 2:
                    return {"error": "Resource type not specified"}

                resource_type = parts[1].lower()

                if resource_type in ["pod", "pods"]:
                    return self.get_pods(namespace)
                elif resource_type in ["deployment", "deployments", "deploy"]:
                    return self.get_deployments(namespace)
                elif resource_type in ["service", "services", "svc"]:
                    return self.get_services(namespace)
                elif resource_type in ["namespace", "namespaces", "ns"]:
                    return self.get_namespaces()
                else:
                    return {"error": f"Resource type '{resource_type}' not supported yet"}

            elif action == "logs":
                if len(parts) < 2:
                    return {"error": "Pod name not specified"}

                pod_name = parts[1]
                lines = 100
                container = None

                # Parse additional arguments
                for i, part in enumerate(parts[2:], 2):
                    if part == "--tail" and i + 1 < len(parts):
                        try:
                            lines = int(parts[i + 1])
                        except ValueError:
                            return {"error": "Invalid tail value"}
                    elif part == "-c" and i + 1 < len(parts):
                        container = parts[i + 1]

                return self.get_pod_logs(pod_name, namespace, container, lines)

            else:
                return {"error": f"Command '{action}' not supported yet"}

        except Exception as e:
            return {"error": f"Error executing command: {e}"}
