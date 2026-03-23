"""GoalNode model."""
from __future__ import annotations

from typing import Literal

from pydantic import Field

from .base import BaseNode, FullStatus, Wikilink


class GoalNode(BaseNode):
    """Strategic objective the project aims to achieve."""
    type: Literal["goal"] = "goal"
    status: FullStatus
    belongs_to: Wikilink
    related_to: list[Wikilink] = Field(default_factory=list)
