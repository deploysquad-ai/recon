"""FeatureNode model."""
from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from .base import BaseNode, FullStatus, Wikilink


class FeatureNode(BaseNode):
    """Leaf node -- handed off to spec-kit."""
    type: Literal["feature"] = "feature"
    status: FullStatus
    belongs_to: Wikilink
    implements: list[Wikilink] = Field(min_length=1)
    actors: list[Wikilink] = Field(default_factory=list)
    supports: list[Wikilink] = Field(default_factory=list)
    target_version: Wikilink | None = None
    epic: Wikilink | None = None
    spec_path: str | None = None
    depends_on: list[Wikilink] = Field(default_factory=list)
    governed_by: list[Wikilink] = Field(default_factory=list)
    related_to: list[Wikilink] = Field(default_factory=list)

    @field_validator("actors")
    @classmethod
    def actors_must_be_personas(cls, v: list[str]) -> list[str]:
        for link in v:
            if not link.startswith("[[Persona - "):
                raise ValueError(f"actors must reference Personas, got: {link}")
        return v
