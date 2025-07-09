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

    def cleanup(self) -> Dict[str, Any]:
        """Cleanup all managed resources.

        Returns:
            Dictionary indicating success or failure
        """
        try:
            # Close API client to free resources
            if self.api_client:
                self.api_client.close()
            return {"status": "success", "message": "Cleaned up managed Kubernetes resources"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to cleanup resources: {str(e)}"}

    def exec_in_pod(
        self,
        pod_name: str,
        namespace: str = "default",
        command: list = None,
        container: str = None,
        stdout: bool = True,
        stderr: bool = True,
    ) -> Dict[str, Any]:
        """Execute a command in a Kubernetes pod or container and return the output.

        Args:
            pod_name: Name of the pod
            namespace: Namespace of the pod
            command: Command to execute as a list of strings
            container: Container name (if pod has multiple containers)
            stdout: Whether to capture stdout
            stderr: Whether to capture stderr

        Returns:
            Dictionary with command output
        """
        if not self.v1_client:
            return {"error": "Kubernetes client not initialized"}

        if command is None:
            command = ["/bin/sh", "-c", "ls"]

        try:
            resp = client.CoreV1Api.connect_get_namespaced_pod_exec(
                self.v1_client,
                pod_name,
                namespace,
                container=container,
                command=command,
                stdout=stdout,
                stderr=stderr,
                stdin=False,
                tty=False,
            )

            return {
                "pod_name": pod_name,
                "namespace": namespace,
                "container": container,
                "command": command,
                "output": resp,
            }
        except ApiException as e:
            return {"error": f"Kubernetes API error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}

    def explain_resource(self, resource_type: str, field_path: str = None) -> Dict[str, Any]:
        """Get documentation for a Kubernetes resource or field.

        Args:
            resource_type: Type of resource to explain (e.g., 'pod', 'deployment')
            field_path: Optional dot-notation field path to get specific field docs

        Returns:
            Dictionary with resource documentation
        """
        import subprocess

        try:
            cmd = ["kubectl", "explain", resource_type]
            if field_path:
                cmd.extend(["--recursive", field_path])

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {
                    "status": "error",
                    "resource_type": resource_type,
                    "field_path": field_path,
                    "error": result.stderr,
                }

            return {
                "status": "success",
                "resource_type": resource_type,
                "field_path": field_path,
                "explanation": result.stdout,
            }
        except Exception as e:
            return {"error": f"Failed to explain resource: {str(e)}"}

    def install_helm_chart(
        self,
        chart_name: str,
        release_name: str,
        namespace: str = "default",
        values: Dict[str, Any] = None,
        version: str = None,
        repo: str = None,
        create_namespace: bool = False,
        timeout: str = "5m0s",
    ) -> Dict[str, Any]:
        """Install a Helm chart.

        Args:
            chart_name: Name of the chart
            release_name: Name for the release
            namespace: Namespace to install into
            values: Dictionary of values to override
            version: Specific chart version
            repo: Chart repository URL
            create_namespace: Whether to create the namespace if it doesn't exist
            timeout: Timeout for installation

        Returns:
            Dictionary with installation result
        """
        import subprocess
        import tempfile

        import yaml

        try:
            cmd = ["helm", "install", release_name, chart_name, "--namespace", namespace]

            if create_namespace:
                cmd.extend(["--create-namespace"])

            if version:
                cmd.extend(["--version", version])

            if repo:
                cmd.extend(["--repo", repo])

            if timeout:
                cmd.extend(["--timeout", timeout])

            if values:
                with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as tmp:
                    yaml.dump(values, tmp)
                    tmp.flush()
                    cmd.extend(["-f", tmp.name])
                    result = subprocess.run(cmd, capture_output=True, text=True)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": result.stderr,
                    "chart_name": chart_name,
                    "release_name": release_name,
                    "namespace": namespace,
                }

            return {
                "status": "success",
                "message": result.stdout,
                "chart_name": chart_name,
                "release_name": release_name,
                "namespace": namespace,
            }
        except Exception as e:
            return {"error": f"Failed to install Helm chart: {str(e)}"}

    def kubectl_apply(
        self, manifest: str = None, filename: str = None, namespace: str = None, force: bool = False
    ) -> Dict[str, Any]:
        """Apply a Kubernetes YAML manifest from a string or file.

        Args:
            manifest: YAML manifest string
            filename: Path to YAML manifest file
            namespace: Namespace to apply to
            force: Force apply even if there are conflicts

        Returns:
            Dictionary with apply result
        """
        import subprocess
        import tempfile

        try:
            cmd = ["kubectl", "apply"]

            if namespace:
                cmd.extend(["-n", namespace])

            if force:
                cmd.append("--force")

            if manifest:
                with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as tmp:
                    tmp.write(manifest)
                    tmp.flush()
                    cmd.extend(["-f", tmp.name])
                    result = subprocess.run(cmd, capture_output=True, text=True)
            elif filename:
                cmd.extend(["-f", filename])
                result = subprocess.run(cmd, capture_output=True, text=True)
            else:
                return {"error": "Either manifest or filename must be provided"}

            if result.returncode != 0:
                return {"status": "error", "message": result.stderr}

            return {"status": "success", "message": result.stdout}
        except Exception as e:
            return {"error": f"Failed to apply manifest: {str(e)}"}

    def kubectl_context(self, action: str = "list", context_name: str = None) -> Dict[str, Any]:
        """Manage Kubernetes contexts - list, get, or set the current context.

        Args:
            action: Action to perform (list, get, set)
            context_name: Name of the context when using 'set'

        Returns:
            Dictionary with context information
        """
        import subprocess

        try:
            if action == "list":
                cmd = ["kubectl", "config", "get-contexts"]
            elif action == "get":
                cmd = ["kubectl", "config", "current-context"]
            elif action == "set" and context_name:
                cmd = ["kubectl", "config", "use-context", context_name]
            else:
                return {"error": "Invalid action or missing context name"}

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {"status": "error", "action": action, "message": result.stderr}

            return {"status": "success", "action": action, "result": result.stdout.strip()}
        except Exception as e:
            return {"error": f"Failed to manage context: {str(e)}"}

    def kubectl_create(
        self,
        resource_type: str = None,
        name: str = None,
        filename: str = None,
        namespace: str = None,
        image: str = None,
        command: list = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Create Kubernetes resources using various methods (from file or using subcommands).

        Args:
            resource_type: Type of resource to create (deployment, service, etc.)
            name: Name for the resource
            filename: Path to YAML file
            namespace: Namespace for the resource
            image: Container image (for pod/deployment creation)
            command: Command to run (for pod/job creation)
            dry_run: Whether to perform a dry run

        Returns:
            Dictionary with create result
        """
        import subprocess

        try:
            cmd = ["kubectl", "create"]

            if namespace:
                cmd.extend(["-n", namespace])

            if dry_run:
                cmd.append("--dry-run=client")

            if filename:
                cmd.extend(["-f", filename])
            elif resource_type and name:
                cmd.append(resource_type)
                cmd.append(name)

                if resource_type in ["deployment", "pod"] and image:
                    cmd.extend(["--image", image])

                if command:
                    cmd.extend(["--", *command])
            else:
                return {"error": "Either filename or resource_type and name must be provided"}

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {"status": "error", "message": result.stderr}

            return {"status": "success", "message": result.stdout}
        except Exception as e:
            return {"error": f"Failed to create resource: {str(e)}"}

    def kubectl_delete(
        self,
        resource_type: str = None,
        name: str = None,
        filename: str = None,
        namespace: str = None,
        label_selector: str = None,
        force: bool = False,
        grace_period: int = None,
    ) -> Dict[str, Any]:
        """Delete Kubernetes resources by resource type, name, labels, or from a manifest file.

        Args:
            resource_type: Type of resource to delete
            name: Name of the resource
            filename: Path to YAML manifest file
            namespace: Namespace of the resource
            label_selector: Label selector for filtering resources
            force: Whether to force delete
            grace_period: Grace period in seconds

        Returns:
            Dictionary with delete result
        """
        import subprocess

        try:
            cmd = ["kubectl", "delete"]

            if namespace:
                cmd.extend(["-n", namespace])

            if force:
                cmd.append("--force")

            if grace_period is not None:
                cmd.extend(["--grace-period", str(grace_period)])

            if filename:
                cmd.extend(["-f", filename])
            elif resource_type:
                cmd.append(resource_type)

                if name:
                    cmd.append(name)
                elif label_selector:
                    cmd.extend(["-l", label_selector])
                else:
                    return {"error": "Either name or label_selector must be provided with resource_type"}
            else:
                return {"error": "Either filename or resource_type must be provided"}

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {"status": "error", "message": result.stderr}

            return {"status": "success", "message": result.stdout}
        except Exception as e:
            return {"error": f"Failed to delete resource: {str(e)}"}

    def kubectl_describe(
        self, resource_type: str, name: str = None, namespace: str = None, label_selector: str = None
    ) -> Dict[str, Any]:
        """Describe Kubernetes resources by resource type, name, and optionally namespace.

        Args:
            resource_type: Type of resource to describe
            name: Name of the resource (optional)
            namespace: Namespace of the resource
            label_selector: Label selector for filtering resources

        Returns:
            Dictionary with description of the resource(s)
        """
        import subprocess

        try:
            cmd = ["kubectl", "describe", resource_type]

            if name:
                cmd.append(name)
            elif label_selector:
                cmd.extend(["-l", label_selector])

            if namespace:
                cmd.extend(["-n", namespace])

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {
                    "status": "error",
                    "resource_type": resource_type,
                    "name": name,
                    "namespace": namespace,
                    "message": result.stderr,
                }

            return {
                "status": "success",
                "resource_type": resource_type,
                "name": name,
                "namespace": namespace,
                "description": result.stdout,
            }
        except Exception as e:
            return {"error": f"Failed to describe resource: {str(e)}"}

    def kubectl_generic(self, args: list, capture_output: bool = True) -> Dict[str, Any]:
        """Execute any kubectl command with the provided arguments and flags.

        Args:
            args: List of arguments to pass to kubectl
            capture_output: Whether to capture and return the command output

        Returns:
            Dictionary with command result
        """
        import subprocess

        try:
            cmd = ["kubectl"] + args

            if capture_output:
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode != 0:
                    return {
                        "status": "error",
                        "command": " ".join(cmd),
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                    }

                return {"status": "success", "command": " ".join(cmd), "output": result.stdout}
            else:
                subprocess.run(cmd)
                return {
                    "status": "success",
                    "command": " ".join(cmd),
                    "output": "Command executed (output not captured)",
                }
        except Exception as e:
            return {"error": f"Failed to execute kubectl command: {str(e)}"}

    def kubectl_get(
        self,
        resource_type: str,
        name: str = None,
        namespace: str = None,
        label_selector: str = None,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """Get or list Kubernetes resources by resource type, name, and optionally namespace.

        Args:
            resource_type: Type of resource to get
            name: Name of the resource (optional)
            namespace: Namespace of the resource
            label_selector: Label selector for filtering resources
            output_format: Output format (json, yaml, wide, name, custom-columns, etc.)

        Returns:
            Dictionary with resource information
        """
        import json
        import subprocess

        try:
            cmd = ["kubectl", "get", resource_type]

            if name:
                cmd.append(name)

            if namespace:
                cmd.extend(["-n", namespace])

            if label_selector:
                cmd.extend(["-l", label_selector])

            cmd.extend(["-o", output_format])

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {
                    "status": "error",
                    "resource_type": resource_type,
                    "name": name,
                    "namespace": namespace,
                    "message": result.stderr,
                }

            if output_format == "json":
                try:
                    data = json.loads(result.stdout)
                    return {
                        "status": "success",
                        "resource_type": resource_type,
                        "name": name,
                        "namespace": namespace,
                        "data": data,
                    }
                except json.JSONDecodeError:
                    return {"status": "error", "message": "Failed to parse JSON output", "output": result.stdout}
            else:
                return {
                    "status": "success",
                    "resource_type": resource_type,
                    "name": name,
                    "namespace": namespace,
                    "output": result.stdout,
                }
        except Exception as e:
            return {"error": f"Failed to get resource: {str(e)}"}

    def kubectl_logs(
        self,
        resource_name: str,
        container: str = None,
        namespace: str = "default",
        previous: bool = False,
        since: str = None,
        tail: int = None,
        follow: bool = False,
        max_follow_seconds: int = 60,
    ) -> Dict[str, Any]:
        """Get logs from Kubernetes resources like pods, deployments, or jobs.

        Args:
            resource_name: Name of the resource
            container: Container name (if pod has multiple containers)
            namespace: Namespace of the resource
            previous: Whether to get logs from previous container instance
            since: Only return logs newer than relative duration like 5s, 2m, or 3h
            tail: Number of lines from the end of the logs to show
            follow: Whether to stream logs (will block for max_follow_seconds)
            max_follow_seconds: Maximum seconds to follow logs when follow=True

        Returns:
            Dictionary with logs
        """
        import subprocess
        from threading import Timer

        try:
            cmd = ["kubectl", "logs", resource_name, "-n", namespace]

            if container:
                cmd.extend(["-c", container])

            if previous:
                cmd.append("-p")

            if since:
                cmd.extend(["--since", since])

            if tail:
                cmd.extend(["--tail", str(tail)])

            if follow:
                cmd.append("-f")
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                output = []
                kill_timer = Timer(max_follow_seconds, process.kill)

                try:
                    kill_timer.start()
                    for line in process.stdout:
                        output.append(line)
                finally:
                    kill_timer.cancel()
                    process.terminate()

                stderr = process.stderr.read()
                if stderr:
                    return {
                        "status": "error",
                        "resource_name": resource_name,
                        "namespace": namespace,
                        "message": stderr,
                    }

                return {
                    "status": "success",
                    "resource_name": resource_name,
                    "namespace": namespace,
                    "container": container,
                    "logs": "".join(output),
                    "truncated": process.returncode is None,  # True if we had to kill the process
                }
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode != 0:
                    return {
                        "status": "error",
                        "resource_name": resource_name,
                        "namespace": namespace,
                        "message": result.stderr,
                    }

                return {
                    "status": "success",
                    "resource_name": resource_name,
                    "namespace": namespace,
                    "container": container,
                    "logs": result.stdout,
                }
        except Exception as e:
            return {"error": f"Failed to get logs: {str(e)}"}

    def kubectl_patch(
        self, resource_type: str, name: str, patch: str, namespace: str = None, patch_type: str = "strategic"
    ) -> Dict[str, Any]:
        """Update field(s) of a resource using strategic merge patch, JSON merge patch, or JSON patch.

        Args:
            resource_type: Type of resource to patch
            name: Name of the resource
            patch: Patch content (JSON string)
            namespace: Namespace of the resource
            patch_type: Type of patch ('strategic', 'merge', or 'json')

        Returns:
            Dictionary with patch result
        """
        import subprocess

        try:
            cmd = ["kubectl", "patch", resource_type, name]

            if namespace:
                cmd.extend(["-n", namespace])

            patch_type_flag = {"strategic": "--type=strategic", "merge": "--type=merge", "json": "--type=json"}.get(
                patch_type, "--type=strategic"
            )

            cmd.append(patch_type_flag)
            cmd.extend(["-p", patch])

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {
                    "status": "error",
                    "resource_type": resource_type,
                    "name": name,
                    "namespace": namespace,
                    "message": result.stderr,
                }

            return {
                "status": "success",
                "resource_type": resource_type,
                "name": name,
                "namespace": namespace,
                "result": result.stdout,
            }
        except Exception as e:
            return {"error": f"Failed to patch resource: {str(e)}"}

    def kubectl_rollout(
        self, subcommand: str, resource_type: str, name: str, namespace: str = None, timeout: str = None
    ) -> Dict[str, Any]:
        """Manage the rollout of a resource (e.g., deployment, daemonset, statefulset).

        Args:
            subcommand: Rollout subcommand (status, history, undo, pause, resume, restart)
            resource_type: Type of resource
            name: Name of the resource
            namespace: Namespace of the resource
            timeout: Timeout for the operation (for restart/status)

        Returns:
            Dictionary with rollout result
        """
        import subprocess

        try:
            cmd = ["kubectl", "rollout", subcommand, f"{resource_type}/{name}"]

            if namespace:
                cmd.extend(["-n", namespace])

            if timeout and subcommand in ["status", "restart"]:
                cmd.extend(["--timeout", timeout])

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {
                    "status": "error",
                    "subcommand": subcommand,
                    "resource_type": resource_type,
                    "name": name,
                    "namespace": namespace,
                    "message": result.stderr,
                }

            return {
                "status": "success",
                "subcommand": subcommand,
                "resource_type": resource_type,
                "name": name,
                "namespace": namespace,
                "result": result.stdout,
            }
        except Exception as e:
            return {"error": f"Failed to manage rollout: {str(e)}"}

    def kubectl_scale(self, resource_type: str, name: str, replicas: int, namespace: str = None) -> Dict[str, Any]:
        """Scale a Kubernetes deployment.

        Args:
            resource_type: Type of resource to scale (deployment, statefulset, etc.)
            name: Name of the resource
            replicas: Target number of replicas
            namespace: Namespace of the resource

        Returns:
            Dictionary with scale result
        """
        import subprocess

        try:
            cmd = ["kubectl", "scale", f"{resource_type}/{name}", f"--replicas={replicas}"]

            if namespace:
                cmd.extend(["-n", namespace])

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {
                    "status": "error",
                    "resource_type": resource_type,
                    "name": name,
                    "replicas": replicas,
                    "namespace": namespace,
                    "message": result.stderr,
                }

            return {
                "status": "success",
                "resource_type": resource_type,
                "name": name,
                "replicas": replicas,
                "namespace": namespace,
                "result": result.stdout,
            }
        except Exception as e:
            return {"error": f"Failed to scale resource: {str(e)}"}

    def list_api_resources(self) -> Dict[str, Any]:
        """List the API resources available in the cluster.

        Returns:
            Dictionary with API resources
        """
        import subprocess

        try:
            cmd = ["kubectl", "api-resources"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {"status": "error", "message": result.stderr}

            # Parse the output into a structured format
            resources = []
            lines = result.stdout.strip().split("\n")

            if len(lines) > 1:  # Skip header row
                lines[0]
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 5:
                        resource = {
                            "name": parts[0],
                            "shortnames": parts[1] if parts[1] != "none" else [],
                            "apiversion": parts[2],
                            "namespaced": parts[3] == "true",
                            "kind": parts[4],
                        }
                        resources.append(resource)

            return {"status": "success", "resources": resources, "total_count": len(resources)}
        except Exception as e:
            return {"error": f"Failed to list API resources: {str(e)}"}

    def ping(self) -> Dict[str, Any]:
        """Verify that the counterpart is still responsive and the connection is alive.

        Returns:
            Dictionary indicating connection status
        """
        try:
            # Simple API call to check if connection is alive
            self.v1_client.list_namespace(limit=1)
            return {"status": "success", "message": "Kubernetes API connection is active"}
        except ApiException as e:
            return {"status": "error", "message": f"Kubernetes API error: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Connection error: {str(e)}"}

    def port_forward(
        self,
        resource_type: str,
        name: str,
        local_port: int,
        remote_port: int,
        namespace: str = "default",
        address: str = "localhost",
    ) -> Dict[str, Any]:
        """Forward a local port to a port on a Kubernetes resource.

        Args:
            resource_type: Type of resource (pod, service, deployment, etc.)
            name: Name of the resource
            local_port: Local port to forward from
            remote_port: Remote port to forward to
            namespace: Namespace of the resource
            address: Local address to bind to

        Returns:
            Dictionary with port forwarding information
        """
        import subprocess
        import time

        try:
            cmd = [
                "kubectl",
                "port-forward",
                f"{resource_type}/{name}",
                f"{local_port}:{remote_port}",
                "-n",
                namespace,
                "--address",
                address,
            ]

            # Start port-forwarding in a separate process
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Store the process for later termination
            if not hasattr(self, "_port_forward_processes"):
                self._port_forward_processes = {}

            process_key = f"{namespace}/{resource_type}/{name}/{local_port}/{remote_port}"
            self._port_forward_processes[process_key] = process

            # Give the process time to start and check for immediate errors
            time.sleep(1)

            if process.poll() is not None:
                stderr = process.stderr.read()
                return {
                    "status": "error",
                    "resource_type": resource_type,
                    "name": name,
                    "namespace": namespace,
                    "local_port": local_port,
                    "remote_port": remote_port,
                    "message": stderr,
                }

            return {
                "status": "success",
                "resource_type": resource_type,
                "name": name,
                "namespace": namespace,
                "local_port": local_port,
                "remote_port": remote_port,
                "address": address,
                "process_key": process_key,
                "message": f"Port forwarding started: {address}:{local_port} -> {name}:{remote_port}",
            }
        except Exception as e:
            return {"error": f"Failed to set up port forwarding: {str(e)}"}

    def stop_port_forward(self, process_key: str = None) -> Dict[str, Any]:
        """Stop a port-forward process.

        Args:
            process_key: The key identifying the port-forward process to stop.
                         If None, stops all port-forwarding processes.

        Returns:
            Dictionary with operation result
        """
        if not hasattr(self, "_port_forward_processes"):
            return {"status": "warning", "message": "No port-forwarding processes exist"}

        try:
            if process_key:
                if process_key in self._port_forward_processes:
                    process = self._port_forward_processes[process_key]
                    process.terminate()
                    process.wait(timeout=5)
                    del self._port_forward_processes[process_key]
                    return {"status": "success", "message": f"Stopped port-forwarding for {process_key}"}
                else:
                    return {"status": "error", "message": f"No port-forwarding process found for key: {process_key}"}
            else:
                # Stop all port-forwarding processes
                stopped_count = 0
                for key, process in list(self._port_forward_processes.items()):
                    process.terminate()
                    process.wait(timeout=5)
                    del self._port_forward_processes[key]
                    stopped_count += 1

                return {
                    "status": "success",
                    "message": f"Stopped all port-forwarding processes ({stopped_count} total)",
                }
        except Exception as e:
            return {"error": f"Failed to stop port forwarding: {str(e)}"}

    def uninstall_helm_chart(
        self, release_name: str, namespace: str = "default", purge: bool = True, timeout: str = "5m0s"
    ) -> Dict[str, Any]:
        """Uninstall a Helm release.

        Args:
            release_name: Name of the release to uninstall
            namespace: Namespace of the release
            purge: Whether to purge release history and associated resources
            timeout: Timeout for the uninstallation

        Returns:
            Dictionary with uninstallation result
        """
        import subprocess

        try:
            cmd = ["helm", "uninstall", release_name, "--namespace", namespace]

            if not purge:
                cmd.append("--keep-history")

            if timeout:
                cmd.extend(["--timeout", timeout])

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {
                    "status": "error",
                    "release_name": release_name,
                    "namespace": namespace,
                    "message": result.stderr,
                }

            return {"status": "success", "release_name": release_name, "namespace": namespace, "message": result.stdout}
        except Exception as e:
            return {"error": f"Failed to uninstall Helm release: {str(e)}"}

    def upgrade_helm_chart(
        self,
        chart_name: str,
        release_name: str,
        namespace: str = "default",
        values: Dict[str, Any] = None,
        version: str = None,
        repo: str = None,
        install: bool = True,
        timeout: str = "5m0s",
    ) -> Dict[str, Any]:
        """Upgrade a Helm release.

        Args:
            chart_name: Name of the chart
            release_name: Name of the release
            namespace: Namespace of the release
            values: Dictionary of values to override
            version: Specific chart version
            repo: Chart repository URL
            install: Whether to install if release doesn't exist
            timeout: Timeout for the upgrade

        Returns:
            Dictionary with upgrade result
        """
        import subprocess
        import tempfile

        import yaml

        try:
            cmd = ["helm", "upgrade", release_name, chart_name, "--namespace", namespace]

            if install:
                cmd.append("--install")

            if version:
                cmd.extend(["--version", version])

            if repo:
                cmd.extend(["--repo", repo])

            if timeout:
                cmd.extend(["--timeout", timeout])

            if values:
                with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as tmp:
                    yaml.dump(values, tmp)
                    tmp.flush()
                    cmd.extend(["-f", tmp.name])
                    result = subprocess.run(cmd, capture_output=True, text=True)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {
                    "status": "error",
                    "chart_name": chart_name,
                    "release_name": release_name,
                    "namespace": namespace,
                    "message": result.stderr,
                }

            return {
                "status": "success",
                "chart_name": chart_name,
                "release_name": release_name,
                "namespace": namespace,
                "message": result.stdout,
            }
        except Exception as e:
            return {"error": f"Failed to upgrade Helm release: {str(e)}"}
