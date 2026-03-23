"""DecisionNode model."""
from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from .base import BaseNode, NoCompleteStatus, Wikilink


class DecisionNode(BaseNode):
    """ADR-style decision with rationale."""
    type: Literal["decision"] = "decision"
    status: NoCompleteStatus
    belongs_to: Wikilink
    governed_by: list[Wikilink] = Field(default_factory=list)
    related_to: list[Wikilink] = Field(default_factory=list)

    @field_validator("governed_by")
    @classmethod
    def governed_by_constraints_only(cls, v: list[str]) -> list[str]:
        for link in v:
            if not link.startswith("[[Constraint - "):
                raise ValueError(f"Decision governed_by must only reference Constraints, got: {link}")
        return v
