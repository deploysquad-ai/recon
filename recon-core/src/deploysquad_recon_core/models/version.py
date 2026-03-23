"""VersionNode model."""
from __future__ import annotations

from typing import Literal

from pydantic import Field

from .base import BaseNode, FullStatus, Wikilink


class VersionNode(BaseNode):
    """Release target (MVP, v1.0, v2.0)."""
    type: Literal["version"] = "version"
    status: FullStatus
    belongs_to: Wikilink
    sequence: int = Field(ge=1)
    target_date: str | None = None
