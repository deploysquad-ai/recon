"""Tests for PersonaNode model."""
import pytest
from pydantic import ValidationError

from deploysquad_recon_core.models.persona import PersonaNode


def test_valid_persona():
    p = PersonaNode(
        type="persona", name="Developer", status="active",
        belongs_to="[[Project - My App]]",
    )
    assert p.name == "Developer"
    assert p.belongs_to == "[[Project - My App]]"


def test_no_complete_status():
    with pytest.raises(ValidationError):
        PersonaNode(type="persona", name="X", status="complete",
                    belongs_to="[[Project - Y]]")


def test_related_to_optional():
    p = PersonaNode(
        type="persona", name="X", status="draft",
        belongs_to="[[Project - Y]]",
        related_to=["[[Persona - Admin]]"]
    )
    assert p.related_to == ["[[Persona - Admin]]"]


def test_belongs_to_must_be_wikilink():
    with pytest.raises(ValidationError):
        PersonaNode(type="persona", name="X", status="draft", belongs_to="not a link")


def test_type_must_be_persona():
    with pytest.raises(ValidationError):
        PersonaNode(type="project", name="X", status="draft",
                    belongs_to="[[Project - Y]]")
