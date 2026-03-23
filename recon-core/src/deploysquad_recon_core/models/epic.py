"""EpicNode model."""
from __future__ import annotations

from typing import Literal

from pydantic import Field

from .base import BaseNode, NoCompleteStatus, Wikilink


class EpicNode(BaseNode):
    """Product-level body of work grouping Features."""
    type: Literal["epic"] = "epic"
    status: NoCompleteStatus
    belongs_to: Wikilink
    target_version: Wikilink | None = None
    supports: list[Wikilink] = Field(default_factory=list)
    related_to: list[Wikilink] = Field(default_factory=list)
