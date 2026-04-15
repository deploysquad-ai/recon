"""Tests for FeatureNode model."""
import pytest
from pydantic import ValidationError

from deploysquad_recon_core.models.feature import FeatureNode


def test_valid_feature():
    f = FeatureNode(
        type="feature", name="JWT Login", status="draft",
        belongs_to="[[Module - Auth]]",
        implements=["[[User Story - Login Flow]]"]
    )
    assert f.name == "JWT Login"


def test_implements_required():
    with pytest.raises(ValidationError):
        FeatureNode(
            type="feature", name="X", status="draft",
            belongs_to="[[Module - Y]]"
        )


def test_implements_min_one():
    with pytest.raises(ValidationError):
        FeatureNode(
            type="feature", name="X", status="draft",
            belongs_to="[[Module - Y]]",
            implements=[]
        )


def test_belongs_to_must_be_module():
    with pytest.raises(ValidationError):
        FeatureNode(
            type="feature", name="X", status="draft",
            belongs_to="[[Project - Y]]",
            implements=["[[User Story - Z]]"],
        )


def test_actors_must_be_personas():
    with pytest.raises(ValidationError):
        FeatureNode(
            type="feature", name="X", status="draft",
            belongs_to="[[Module - Y]]",
            implements=["[[User Story - Z]]"],
            actors=["[[Module - Bad]]"]
        )


def test_actors_accepts_personas():
    f = FeatureNode(
        type="feature", name="X", status="draft",
        belongs_to="[[Module - Y]]",
        implements=["[[User Story - Z]]"],
        actors=["[[Persona - Dev]]"]
    )
    assert f.actors == ["[[Persona - Dev]]"]


def test_supports_optional():
    f = FeatureNode(
        type="feature", name="X", status="draft",
        belongs_to="[[Module - Y]]",
        implements=["[[User Story - Z]]"],
        supports=["[[Goal - Fast]]"]
    )
    assert f.supports == ["[[Goal - Fast]]"]


def test_target_version_optional():
    f = FeatureNode(
        type="feature", name="X", status="draft",
        belongs_to="[[Module - Y]]",
        implements=["[[User Story - Z]]"],
        target_version="[[Version - MVP]]"
    )
    assert f.target_version == "[[Version - MVP]]"


def test_epic_optional():
    f = FeatureNode(
        type="feature", name="X", status="draft",
        belongs_to="[[Module - Y]]",
        implements=["[[User Story - Z]]"],
        epic="[[Epic - Auth]]"
    )
    assert f.epic == "[[Epic - Auth]]"


def test_depends_on_optional():
    f = FeatureNode(
        type="feature", name="X", status="draft",
        belongs_to="[[Module - Y]]",
        implements=["[[User Story - Z]]"],
        depends_on=["[[Feature - Other]]"]
    )
    assert f.depends_on == ["[[Feature - Other]]"]


def test_governed_by_optional():
    f = FeatureNode(
        type="feature", name="X", status="draft",
        belongs_to="[[Module - Y]]",
        implements=["[[User Story - Z]]"],
        governed_by=["[[Constraint - PCI]]"]
    )
    assert f.governed_by == ["[[Constraint - PCI]]"]


def test_all_statuses():
    for s in ["draft", "active", "complete", "archived"]:
        f = FeatureNode(
            type="feature", name="X", status=s,
            belongs_to="[[Module - Y]]",
            implements=["[[User Story - Z]]"]
        )
        assert f.status == s


def test_spec_path_defaults_to_none():
    f = FeatureNode(
        type="feature", name="X", status="draft",
        belongs_to="[[Module - Y]]",
        implements=["[[User Story - Z]]"],
    )
    assert f.spec_path is None


def test_spec_path_accepts_string():
    f = FeatureNode(
        type="feature", name="X", status="draft",
        belongs_to="[[Module - Y]]",
        implements=["[[User Story - Z]]"],
        spec_path="docs/specs/2026-03-28-focus-view-design.md",
    )
    assert f.spec_path == "docs/specs/2026-03-28-focus-view-design.md"
