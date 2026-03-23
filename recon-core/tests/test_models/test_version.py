"""Tests for VersionNode model."""
import pytest
from pydantic import ValidationError

from deploysquad_recon_core.models.version import VersionNode


def test_valid_version():
    v = VersionNode(
        type="version", name="MVP", status="draft",
        belongs_to="[[Project - My App]]", sequence=1
    )
    assert v.sequence == 1
    assert v.target_date is None


def test_sequence_required():
    with pytest.raises(ValidationError):
        VersionNode(type="version", name="X", status="draft", belongs_to="[[Project - Y]]")


def test_sequence_must_be_positive():
    with pytest.raises(ValidationError):
        VersionNode(type="version", name="X", status="draft", belongs_to="[[Project - Y]]", sequence=0)


def test_target_date_optional():
    v = VersionNode(
        type="version", name="X", status="draft",
        belongs_to="[[Project - Y]]", sequence=1, target_date="2026-06-01"
    )
    assert v.target_date == "2026-06-01"


def test_type_must_be_version():
    with pytest.raises(ValidationError):
        VersionNode(type="project", name="X", status="draft", belongs_to="[[Project - Y]]", sequence=1)


def test_all_statuses():
    for s in ["draft", "active", "complete", "archived"]:
        v = VersionNode(type="version", name="X", status=s, belongs_to="[[Project - Y]]", sequence=1)
        assert v.status == s
