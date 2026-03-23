"""ModuleNode model."""
from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from .base import BaseNode, NoCompleteStatus, Wikilink


class ModuleNode(BaseNode):
    """Functional subsystem (e.g. Auth, Payments)."""
    type: Literal["module"] = "module"
    status: NoCompleteStatus
    belongs_to: Wikilink
    actors: list[Wikilink] = Field(default_factory=list)
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
