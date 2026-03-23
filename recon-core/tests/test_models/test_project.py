"""Tests for ProjectNode model."""
import pytest
from pydantic import ValidationError

from deploysquad_recon_core.models.project import ProjectNode

VALID_DESC = "A productivity app that helps users manage tasks and focus"


def test_valid_project():
    p = ProjectNode(
        type="project", name="My App", status="draft",
        description=VALID_DESC,
    )
    assert p.name == "My App"
    assert p.schema_version == 1
    assert p.type == "project"


def test_description_required():
    with pytest.raises(ValidationError):
        ProjectNode(type="project", name="X", status="draft")


def test_description_no_max_length():
    """No upper limit — long descriptions are fine."""
    p = ProjectNode(
        type="project", name="X", status="draft",
        description="x" * 1000,
    )
    assert len(p.description) == 1000


def test_description_min_length():
    with pytest.raises(ValidationError):
        ProjectNode(type="project", name="X", status="draft", description="")


def test_description_too_short():
    with pytest.raises(ValidationError):
        ProjectNode(type="project", name="X", status="draft", description="Too short")


def test_description_exactly_at_minimum():
    p = ProjectNode(
        type="project", name="X", status="draft",
        description="x" * 50,
    )
    assert len(p.description) == 50


def test_type_must_be_project():
    with pytest.raises(ValidationError):
        ProjectNode(type="feature", name="X", status="draft", description=VALID_DESC)


def test_all_statuses():
    for s in ["draft", "active", "complete", "archived"]:
        p = ProjectNode(type="project", name="X", status=s, description=VALID_DESC)
        assert p.status == s
