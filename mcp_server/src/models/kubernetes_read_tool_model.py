"""Kubernetes read tool model definitions.

This module contains Pydantic models for Kubernetes read operations,
defining the structure and validation for reading Kubernetes resources.
"""

from typing import Optional

from pydantic import BaseModel, Field


class KubernetesReadTool(BaseModel):
    """Model for Kubernetes resource read operations.

    This model defines the parameters needed to read Kubernetes resources,
    including resource type, namespace, and optional label filtering.
    """

    resource_type: str = Field(
        description="The type of Kubernetes resource to read (e.g., 'pods', 'services', 'deployments')"
    )
    namespace: Optional[str] = Field(
        default="default",
        description="The Kubernetes namespace to query. Defaults to 'default' if not specified",
    )
    label_selector: Optional[str] = Field(
        default="",
        description=(
            "Label selector to filter resources (e.g., 'app=myapp,version=v1'). " "Empty string means no filtering"
        ),
    )
