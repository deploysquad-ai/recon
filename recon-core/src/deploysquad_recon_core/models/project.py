"""ProjectNode model."""
from __future__ import annotations

from typing import Literal

from pydantic import Field

from .base import BaseNode, FullStatus


class ProjectNode(BaseNode):
    """Top-level project container node."""
    type: Literal["project"] = "project"
    status: FullStatus
    description: str = Field(min_length=50)
