"""ConstraintNode model."""
from __future__ import annotations

from typing import Literal

from pydantic import Field

from .base import BaseNode, NoCompleteStatus, Wikilink


class ConstraintNode(BaseNode):
    """Hard limit -- tech stack, compliance, performance."""
    type: Literal["constraint"] = "constraint"
    status: NoCompleteStatus
    belongs_to: Wikilink
    related_to: list[Wikilink] = Field(default_factory=list)
