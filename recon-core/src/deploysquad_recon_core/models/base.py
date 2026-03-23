"""Base model, Wikilink type, and status enums for graph nodes."""
from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


# Wikilink: must match [[Type - Name]] format
# Allows multi-word types like "User Story"
Wikilink = Annotated[str, Field(pattern=r"^\[\[[A-Z][a-zA-Z ]*[a-zA-Z] - .+\]\]$")]


class FullStatus(str, Enum):
    """Status for node types that can be completed (Project, Goal, Version, User Story, Feature)."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETE = "complete"
    ARCHIVED = "archived"


class NoCompleteStatus(str, Enum):
    """Status for node types that are never 'complete' (Persona, Constraint, Module, Decision, Epic)."""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class BaseNode(BaseModel):
    """Base model for all graph node types."""
    type: str
    schema_version: int = Field(default=1, ge=1, le=1)
    name: str = Field(min_length=1)
    status: FullStatus  # Overridden by subclasses that use NoCompleteStatus
    tags: list[str] = Field(default_factory=list)
