"""Tests for GoalNode model."""
import pytest
from pydantic import ValidationError

from deploysquad_recon_core.models.goal import GoalNode


def test_valid_goal():
    g = GoalNode(
        type="goal", name="Fast Delivery", status="active",
        belongs_to="[[Project - My App]]"
    )
    assert g.belongs_to == "[[Project - My App]]"


def test_belongs_to_required():
    with pytest.raises(ValidationError):
        GoalNode(type="goal", name="X", status="draft")


def test_belongs_to_must_be_wikilink():
    with pytest.raises(ValidationError):
        GoalNode(type="goal", name="X", status="draft", belongs_to="not a link")


def test_related_to_optional():
    g = GoalNode(
        type="goal", name="X", status="draft",
        belongs_to="[[Project - Y]]",
        related_to=["[[Goal - Z]]"]
    )
    assert g.related_to == ["[[Goal - Z]]"]


def test_related_to_defaults_empty():
    g = GoalNode(type="goal", name="X", status="draft", belongs_to="[[Project - Y]]")
    assert g.related_to == []


def test_type_must_be_goal():
    with pytest.raises(ValidationError):
        GoalNode(type="project", name="X", status="draft", belongs_to="[[Project - Y]]")


def test_all_statuses():
    for s in ["draft", "active", "complete", "archived"]:
        g = GoalNode(type="goal", name="X", status=s, belongs_to="[[Project - Y]]")
        assert g.status == s
