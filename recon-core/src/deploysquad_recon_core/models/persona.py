"""PersonaNode model."""
from __future__ import annotations

from typing import Literal

from pydantic import Field

from .base import BaseNode, NoCompleteStatus, Wikilink


class PersonaNode(BaseNode):
    """User/role/system actor with goals and context."""
    type: Literal["persona"] = "persona"
    status: NoCompleteStatus
    belongs_to: Wikilink
    related_to: list[Wikilink] = Field(default_factory=list)
