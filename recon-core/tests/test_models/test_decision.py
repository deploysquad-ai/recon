"""Tests for DecisionNode model."""
import pytest
from pydantic import ValidationError

from deploysquad_recon_core.models.decision import DecisionNode


def test_valid_decision():
    d = DecisionNode(
        type="decision", name="Use JWT", status="active",
        belongs_to="[[Project - My App]]"
    )
    assert d.name == "Use JWT"


def test_belongs_to_required():
    with pytest.raises(ValidationError):
        DecisionNode(type="decision", name="X", status="draft")


def test_no_complete_status():
    with pytest.raises(ValidationError):
        DecisionNode(type="decision", name="X", status="complete",
                     belongs_to="[[Project - Y]]")


def test_governed_by_must_be_constraints():
    with pytest.raises(ValidationError):
        DecisionNode(
            type="decision", name="X", status="draft",
            belongs_to="[[Project - Y]]",
            governed_by=["[[Module - Bad]]"]
        )


def test_governed_by_accepts_constraints():
    d = DecisionNode(
        type="decision", name="X", status="draft",
        belongs_to="[[Project - Y]]",
        governed_by=["[[Constraint - PCI]]"]
    )
    assert d.governed_by == ["[[Constraint - PCI]]"]


def test_related_to_optional():
    d = DecisionNode(
        type="decision", name="X", status="draft",
        belongs_to="[[Project - Y]]",
        related_to=["[[Decision - Other]]"]
    )
    assert d.related_to == ["[[Decision - Other]]"]


def test_belongs_to_must_be_wikilink():
    with pytest.raises(ValidationError):
        DecisionNode(type="decision", name="X", status="draft", belongs_to="not a link")


def test_type_must_be_decision():
    with pytest.raises(ValidationError):
        DecisionNode(type="project", name="X", status="draft",
                     belongs_to="[[Project - Y]]")
