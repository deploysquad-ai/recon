"""Tests for ConstraintNode model."""
import pytest
from pydantic import ValidationError

from deploysquad_recon_core.models.constraint import ConstraintNode


def test_valid_constraint():
    c = ConstraintNode(
        type="constraint", name="MIT License", status="active",
        belongs_to="[[Project - My App]]"
    )
    assert c.name == "MIT License"


def test_belongs_to_required():
    with pytest.raises(ValidationError):
        ConstraintNode(type="constraint", name="X", status="draft")


def test_no_complete_status():
    with pytest.raises(ValidationError):
        ConstraintNode(type="constraint", name="X", status="complete",
                       belongs_to="[[Project - Y]]")


def test_related_to_optional():
    c = ConstraintNode(
        type="constraint", name="X", status="draft",
        belongs_to="[[Project - Y]]",
        related_to=["[[Constraint - Z]]"]
    )
    assert c.related_to == ["[[Constraint - Z]]"]


def test_belongs_to_must_be_wikilink():
    with pytest.raises(ValidationError):
        ConstraintNode(type="constraint", name="X", status="draft", belongs_to="not a link")


def test_type_must_be_constraint():
    with pytest.raises(ValidationError):
        ConstraintNode(type="project", name="X", status="draft",
                       belongs_to="[[Project - Y]]")
