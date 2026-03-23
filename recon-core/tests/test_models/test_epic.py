"""Tests for EpicNode model."""
import pytest
from pydantic import ValidationError

from deploysquad_recon_core.models.epic import EpicNode


def test_valid_epic():
    e = EpicNode(
        type="epic", name="Authentication", status="active",
        belongs_to="[[Module - Auth]]"
    )
    assert e.name == "Authentication"


def test_belongs_to_required():
    with pytest.raises(ValidationError):
        EpicNode(type="epic", name="X", status="draft")


def test_no_complete_status():
    with pytest.raises(ValidationError):
        EpicNode(type="epic", name="X", status="complete",
                 belongs_to="[[Module - Y]]")


def test_target_version_optional():
    e = EpicNode(
        type="epic", name="X", status="draft",
        belongs_to="[[Module - Y]]",
        target_version="[[Version - MVP]]"
    )
    assert e.target_version == "[[Version - MVP]]"


def test_supports_optional():
    e = EpicNode(
        type="epic", name="X", status="draft",
        belongs_to="[[Module - Y]]",
        supports=["[[Goal - Fast]]"]
    )
    assert e.supports == ["[[Goal - Fast]]"]


def test_belongs_to_must_be_wikilink():
    with pytest.raises(ValidationError):
        EpicNode(type="epic", name="X", status="draft", belongs_to="not a link")


def test_related_to_optional():
    e = EpicNode(
        type="epic", name="X", status="draft",
        belongs_to="[[Module - Y]]",
        related_to=["[[Epic - Other]]"]
    )
    assert e.related_to == ["[[Epic - Other]]"]
