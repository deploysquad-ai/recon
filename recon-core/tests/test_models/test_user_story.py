"""Tests for UserStoryNode model."""
import pytest
from pydantic import ValidationError

from deploysquad_recon_core.models.user_story import UserStoryNode


def test_valid_user_story():
    us = UserStoryNode(
        type="user-story", name="Login Flow", status="draft",
        belongs_to="[[Module - Auth]]",
        actors=["[[Persona - Developer]]"],
    )
    assert us.name == "Login Flow"


def test_actors_required():
    with pytest.raises(ValidationError):
        UserStoryNode(
            type="user-story", name="X", status="draft",
            belongs_to="[[Module - Y]]",
        )


def test_actors_min_one():
    with pytest.raises(ValidationError):
        UserStoryNode(
            type="user-story", name="X", status="draft",
            belongs_to="[[Module - Y]]",
            actors=[],
        )


def test_actors_must_be_personas():
    with pytest.raises(ValidationError):
        UserStoryNode(
            type="user-story", name="X", status="draft",
            belongs_to="[[Module - Y]]",
            actors=["[[Module - Bad]]"],
        )


def test_supports_optional():
    us = UserStoryNode(
        type="user-story", name="X", status="draft",
        belongs_to="[[Module - Y]]",
        actors=["[[Persona - Dev]]"],
        supports=["[[Goal - Fast]]"]
    )
    assert us.supports == ["[[Goal - Fast]]"]


def test_target_version_optional():
    us = UserStoryNode(
        type="user-story", name="X", status="draft",
        belongs_to="[[Module - Y]]",
        actors=["[[Persona - Dev]]"],
        target_version="[[Version - MVP]]"
    )
    assert us.target_version == "[[Version - MVP]]"


def test_governed_by_optional():
    us = UserStoryNode(
        type="user-story", name="X", status="draft",
        belongs_to="[[Module - Y]]",
        actors=["[[Persona - Dev]]"],
        governed_by=["[[Constraint - PCI]]"]
    )
    assert us.governed_by == ["[[Constraint - PCI]]"]
