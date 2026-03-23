"""Tests for vault reader."""
from pathlib import Path

import pytest

from deploysquad_recon_core.vault.reader import read_node, parse_body_sections
from deploysquad_recon_core.errors import NodeNotFoundError, ValidationError
from deploysquad_recon_core.models.project import ProjectNode
from deploysquad_recon_core.models.feature import FeatureNode


FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "sample_vault" / "my-project"


class TestReadNode:
    def test_read_project(self):
        result = read_node(FIXTURE_DIR / "Project - My Project.md")
        assert result["frontmatter"]["name"] == "My Project"
        assert isinstance(result["model"], ProjectNode)
        assert result["model"].status == "active"

    def test_read_feature(self):
        result = read_node(FIXTURE_DIR / "features" / "Feature - JWT Login.md")
        assert isinstance(result["model"], FeatureNode)
        assert result["model"].implements == ["[[User Story - Login]]"]
        assert result["model"].actors == ["[[Persona - Developer]]"]

    def test_body_sections_parsed(self):
        result = read_node(FIXTURE_DIR / "Project - My Project.md")
        assert "Description" in result["body_sections"]
        assert "Scope" in result["body_sections"]
        assert "sample project" in result["body_sections"]["Description"]

    def test_nonexistent_file_raises(self):
        with pytest.raises(NodeNotFoundError):
            read_node(FIXTURE_DIR / "nonexistent.md")

    def test_read_user_story(self):
        result = read_node(FIXTURE_DIR / "user-stories" / "User Story - Login.md")
        assert "Developer can authenticate with email and password" in result["body_sections"]["Acceptance Criteria"]
        assert result["model"].actors == ["[[Persona - Developer]]"]

    def test_read_decision(self):
        result = read_node(FIXTURE_DIR / "decisions" / "Decision - Use JWT.md")
        assert "Decision" in result["body_sections"]
        assert "JWT tokens" in result["body_sections"]["Decision"]

    def test_read_goal(self):
        result = read_node(FIXTURE_DIR / "goals" / "Goal - Fast Delivery.md")
        assert result["model"].belongs_to == "[[Project - My Project]]"
        assert "Description" in result["body_sections"]

    def test_read_persona(self):
        result = read_node(FIXTURE_DIR / "personas" / "Persona - Developer.md")
        assert "Integrate quickly via API" in result["body_sections"]["Goals"]
        assert "Backend developer integrating our API" in result["body_sections"]["Background"]

    def test_read_all_fixture_files(self):
        """Every file in the fixture vault should parse and validate."""
        files = list(FIXTURE_DIR.rglob("*.md"))
        assert len(files) == 10  # All 10 node types
        for f in files:
            result = read_node(f)
            assert result["model"] is not None


class TestParseBodySections:
    def test_simple(self):
        body = "## Description\nFoo bar\n\n## Scope\nBaz"
        sections = parse_body_sections(body)
        assert sections == {"Description": "Foo bar", "Scope": "Baz"}

    def test_empty_body(self):
        assert parse_body_sections("") == {}

    def test_no_headings(self):
        assert parse_body_sections("Just some text") == {}

    def test_multiline_content(self):
        body = "## Description\nLine 1\nLine 2\n\nLine 3"
        sections = parse_body_sections(body)
        assert "Line 1\nLine 2\n\nLine 3" == sections["Description"]
