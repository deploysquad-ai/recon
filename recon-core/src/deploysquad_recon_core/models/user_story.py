"""UserStoryNode model."""
from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from .base import BaseNode, FullStatus, Wikilink


class UserStoryNode(BaseNode):
    """'As a [persona], I want [goal], so that [benefit]' user story."""
    type: Literal["user-story"] = "user-story"
    status: FullStatus
    belongs_to: Wikilink
    actors: list[Wikilink] = Field(min_length=1)
    supports: list[Wikilink] = Field(default_factory=list)
    target_version: Wikilink | None = None
    governed_by: list[Wikilink] = Field(default_factory=list)
    related_to: list[Wikilink] = Field(default_factory=list)

    @field_validator("actors")
    @classmethod
    def actors_must_be_personas(cls, v: list[str]) -> list[str]:
        for link in v:
            if not link.startswith("[[Persona - "):
                raise ValueError(f"actors must reference Personas, got: {link}")
        return v
