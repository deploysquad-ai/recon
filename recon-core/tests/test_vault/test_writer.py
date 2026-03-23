"""Tests for vault writer."""
import re
from pathlib import Path

import frontmatter
import pytest

from deploysquad_recon_core.vault.writer import write_node, _render_body_sections
from deploysquad_recon_core.models.project import ProjectNode
from deploysquad_recon_core.models.feature import FeatureNode
from deploysquad_recon_core.errors import DuplicateNodeError

_DESC = "A productivity app that helps users manage their daily tasks"


def _read_back(path: Path) -> tuple[dict, dict[str, str]]:
    """Read a written file back, returning (frontmatter_dict, body_sections)."""
    post = frontmatter.load(str(path))
    fm = dict(post.metadata)
    # Parse body sections: lines starting with ## are headings
    sections: dict[str, str] = {}
    if post.content.strip():
        parts = re.split(r"^## (.+)$", post.content.strip(), flags=re.MULTILINE)
        # parts[0] is text before first heading (usually empty), then alternating heading/content
        for i in range(1, len(parts), 2):
            heading = parts[i].strip()
            content = parts[i + 1].strip() if i + 1 < len(parts) else ""
            sections[heading] = content
    return fm, sections


class TestWriteNode:
    def test_write_project(self, tmp_path):
        node = ProjectNode(type="project", name="Test App", status="draft", description=_DESC)
        path = write_node(node, tmp_path)
        assert path.exists()
        assert path == tmp_path / "Project - Test App.md"

    def test_write_feature_in_subfolder(self, tmp_path):
        node = FeatureNode(
            type="feature", name="Login", status="draft",
            belongs_to="[[Module - Auth]]",
            implements=["[[User Story - Login Flow]]"],
        )
        path = write_node(node, tmp_path)
        assert path == tmp_path / "features" / "Feature - Login.md"
        assert path.exists()

    def test_round_trip(self, tmp_path):
        """Write then read should preserve data."""
        node = ProjectNode(type="project", name="Test", status="active", description=_DESC)
        path = write_node(node, tmp_path, body_sections={"Description": "Test project"})
        fm, sections = _read_back(path)
        assert fm["name"] == "Test"
        assert fm["status"] == "active"
        assert sections["Description"] == "Test project"

    def test_duplicate_raises(self, tmp_path):
        node = ProjectNode(type="project", name="Test", status="draft", description=_DESC)
        write_node(node, tmp_path)
        with pytest.raises(DuplicateNodeError):
            write_node(node, tmp_path)

    def test_overwrite_allowed(self, tmp_path):
        node = ProjectNode(type="project", name="Test", status="draft", description=_DESC)
        write_node(node, tmp_path)
        node2 = ProjectNode(type="project", name="Test", status="active", description=_DESC + " with updates")
        path = write_node(node2, tmp_path, overwrite=True)
        fm, _ = _read_back(path)
        assert fm["status"] == "active"
        assert fm["description"] == _DESC + " with updates"

    def test_creates_parent_dirs(self, tmp_path):
        node = FeatureNode(
            type="feature", name="X", status="draft",
            belongs_to="[[Module - Y]]",
            implements=["[[User Story - Z]]"],
        )
        path = write_node(node, tmp_path)
        assert path.parent.exists()
        assert path.exists()

    def test_body_sections_rendered(self, tmp_path):
        node = ProjectNode(type="project", name="Test", status="draft", description=_DESC)
        sections = {"Description": "Foo bar", "Scope": "Baz"}
        path = write_node(node, tmp_path, body_sections=sections)
        _, read_sections = _read_back(path)
        assert read_sections["Description"] == "Foo bar"
        assert read_sections["Scope"] == "Baz"

    def test_no_body_sections(self, tmp_path):
        node = ProjectNode(type="project", name="Test", status="draft", description=_DESC)
        path = write_node(node, tmp_path)
        _, sections = _read_back(path)
        assert sections == {}

    def test_write_with_optional_fields(self, tmp_path):
        node = FeatureNode(
            type="feature", name="X", status="draft",
            belongs_to="[[Module - Y]]",
            implements=["[[User Story - Z]]"],
            target_version="[[Version - MVP]]",
            epic="[[Epic - Auth]]",
            actors=["[[Persona - Dev]]"],
            supports=["[[Goal - Fast]]"],
        )
        path = write_node(node, tmp_path)
        fm, _ = _read_back(path)
        assert fm["target_version"] == "[[Version - MVP]]"
        assert fm["epic"] == "[[Epic - Auth]]"
        assert fm["actors"] == ["[[Persona - Dev]]"]

    def test_excludes_none_values(self, tmp_path):
        node = FeatureNode(
            type="feature", name="X", status="draft",
            belongs_to="[[Module - Y]]",
            implements=["[[User Story - Z]]"],
        )
        path = write_node(node, tmp_path)
        fm, _ = _read_back(path)
        assert "target_version" not in fm
        assert "epic" not in fm


class TestRenderBodySections:
    def test_single_section(self):
        result = _render_body_sections({"Desc": "Hello"})
        assert result == "## Desc\n\nHello"

    def test_multiple_sections(self):
        result = _render_body_sections({"A": "1", "B": "2"})
        assert "## A\n\n1" in result
        assert "## B\n\n2" in result
