"""Tests for ModuleNode model."""
import pytest
from pydantic import ValidationError

from deploysquad_recon_core.models.module import ModuleNode


def test_valid_module():
    m = ModuleNode(
        type="module", name="Auth", status="active",
        belongs_to="[[Project - My App]]"
    )
    assert m.name == "Auth"


def test_belongs_to_required():
    with pytest.raises(ValidationError):
        ModuleNode(type="module", name="X", status="draft")


def test_no_complete_status():
    with pytest.raises(ValidationError):
        ModuleNode(type="module", name="X", status="complete",
                   belongs_to="[[Project - Y]]")


def test_actors_optional():
    m = ModuleNode(
        type="module", name="X", status="draft",
        belongs_to="[[Project - Y]]",
        actors=["[[Persona - Developer]]"]
    )
    assert m.actors == ["[[Persona - Developer]]"]


def test_actors_must_be_persona_wikilinks():
    with pytest.raises(ValidationError):
        ModuleNode(
            type="module", name="X", status="draft",
            belongs_to="[[Project - Y]]",
            actors=["[[Module - Bad]]"]
        )


def test_depends_on_optional():
    m = ModuleNode(
        type="module", name="X", status="draft",
        belongs_to="[[Project - Y]]",
        depends_on=["[[Module - Other]]"]
    )
    assert m.depends_on == ["[[Module - Other]]"]


def test_governed_by_optional():
    m = ModuleNode(
        type="module", name="X", status="draft",
        belongs_to="[[Project - Y]]",
        governed_by=["[[Constraint - MIT]]"]
    )
    assert m.governed_by == ["[[Constraint - MIT]]"]


def test_related_to_optional():
    m = ModuleNode(
        type="module", name="X", status="draft",
        belongs_to="[[Project - Y]]",
        related_to=["[[Module - Other]]"]
    )
    assert m.related_to == ["[[Module - Other]]"]


def test_belongs_to_must_be_wikilink():
    with pytest.raises(ValidationError):
        ModuleNode(type="module", name="X", status="draft", belongs_to="not a link")


def test_type_must_be_module():
    with pytest.raises(ValidationError):
        ModuleNode(type="project", name="X", status="draft",
                   belongs_to="[[Project - Y]]")
