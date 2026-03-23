"""Integration tests for the public API."""
from pathlib import Path

import pytest

from deploysquad_recon_core import (
    create_node,
    get_node,
    list_nodes,
    update_node,
    resolve_links,
    build_index,
    generate_context,
)
from deploysquad_recon_core.errors import ValidationError, DuplicateNodeError, NodeNotFoundError


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "sample_vault" / "my-project"

_DESC = "A productivity app that helps users manage their daily tasks"


class TestCreateNode:
    def test_create_project(self, tmp_path):
        path = create_node("project", {"name": "Test", "status": "draft", "description": _DESC}, tmp_path)
        assert path.exists()
        assert path.name == "Project - Test.md"

    def test_create_feature(self, tmp_path):
        path = create_node("feature", {
            "name": "Login", "status": "draft",
            "belongs_to": "[[Module - Auth]]",
            "implements": ["[[User Story - Login Flow]]"],
        }, tmp_path)
        assert path.exists()
        assert "features" in str(path)

    def test_create_with_body_sections(self, tmp_path):
        path = create_node(
            "project",
            {"name": "Test", "status": "draft", "description": _DESC},
            tmp_path,
            body_sections={"Description": "Full description here"},
        )
        node = get_node(path)
        assert node["body_sections"]["Description"] == "Full description here"

    def test_create_invalid_raises(self, tmp_path):
        with pytest.raises(ValidationError):
            create_node("project", {"name": "", "status": "draft"}, tmp_path)

    def test_create_duplicate_raises(self, tmp_path):
        create_node("project", {"name": "Test", "status": "draft", "description": _DESC}, tmp_path)
        with pytest.raises(DuplicateNodeError):
            create_node("project", {"name": "Test", "status": "draft", "description": _DESC}, tmp_path)

    def test_auto_fills_type_and_schema_version(self, tmp_path):
        path = create_node("project", {"name": "Test", "status": "draft", "description": _DESC}, tmp_path)
        node = get_node(path)
        assert node["frontmatter"]["type"] == "project"
        assert node["frontmatter"]["schema_version"] == 1


class TestGetNode:
    def test_get_fixture_project(self):
        node = get_node(FIXTURE_DIR / "Project - My Project.md")
        assert node["frontmatter"]["name"] == "My Project"

    def test_get_nonexistent_raises(self):
        with pytest.raises(NodeNotFoundError):
            get_node(Path("/nonexistent/path.md"))


class TestListNodes:
    def test_list_all(self):
        nodes = list_nodes(FIXTURE_DIR)
        assert len(nodes) == 10

    def test_filter_by_type(self):
        features = list_nodes(FIXTURE_DIR, node_type="feature")
        assert len(features) == 1
        assert features[0]["type"] == "feature"

    def test_filter_by_status(self):
        active = list_nodes(FIXTURE_DIR, status="active")
        assert all(n["status"] == "active" for n in active)
        assert len(active) > 0

    def test_filter_by_type_and_status(self):
        drafts = list_nodes(FIXTURE_DIR, node_type="feature", status="draft")
        assert len(drafts) == 1


class TestUpdateNode:
    def test_update_status(self, tmp_path):
        path = create_node("project", {"name": "Test", "status": "draft", "description": _DESC}, tmp_path)
        updated = update_node(path, {"status": "active"})
        node = get_node(updated)
        assert node["frontmatter"]["status"] == "active"

    def test_update_preserves_body(self, tmp_path):
        path = create_node(
            "project",
            {"name": "Test", "status": "draft", "description": _DESC},
            tmp_path,
            body_sections={"Description": "Keep me"},
        )
        updated = update_node(path, {"status": "active"})
        node = get_node(updated)
        assert node["body_sections"]["Description"] == "Keep me"

    def test_update_invalid_raises(self, tmp_path):
        path = create_node("project", {"name": "Test", "status": "draft", "description": _DESC}, tmp_path)
        with pytest.raises(ValidationError):
            update_node(path, {"status": "invalid"})


class TestAutoTagging:
    def test_create_node_auto_tags_project(self, tmp_path):
        path = create_node("project", {"name": "Ideate", "status": "draft", "description": _DESC}, tmp_path)
        node = get_node(path)
        assert "project/ideate" in node["frontmatter"]["tags"]

    def test_create_node_auto_tags_child(self, tmp_path):
        create_node("project", {"name": "Ideate", "status": "draft", "description": _DESC}, tmp_path)
        path = create_node("module", {
            "name": "Auth", "status": "draft",
            "belongs_to": "[[Project - Ideate]]",
        }, tmp_path)
        node = get_node(path)
        assert "project/ideate" in node["frontmatter"]["tags"]

    def test_create_node_multiword_project_tag(self, tmp_path):
        create_node("project", {"name": "My Cool App", "status": "draft", "description": _DESC}, tmp_path)
        path = create_node("goal", {
            "name": "Ship It", "status": "draft",
            "belongs_to": "[[Project - My Cool App]]",
        }, tmp_path)
        node = get_node(path)
        assert "project/my-cool-app" in node["frontmatter"]["tags"]

    def test_create_node_preserves_custom_tags(self, tmp_path):
        path = create_node(
            "project",
            {"name": "Ideate", "status": "draft", "description": _DESC, "tags": ["custom/tag"]},
            tmp_path,
        )
        node = get_node(path)
        tags = node["frontmatter"]["tags"]
        assert "project/ideate" in tags
        assert "custom/tag" in tags

    def test_create_node_no_duplicate_tags(self, tmp_path):
        path = create_node(
            "project",
            {"name": "Ideate", "status": "draft", "description": _DESC, "tags": ["project/ideate"]},
            tmp_path,
        )
        node = get_node(path)
        assert node["frontmatter"]["tags"].count("project/ideate") == 1

    def test_update_node_preserves_tags(self, tmp_path):
        path = create_node("project", {"name": "Ideate", "status": "draft", "description": _DESC}, tmp_path)
        updated = update_node(path, {"status": "active"})
        node = get_node(updated)
        assert "project/ideate" in node["frontmatter"]["tags"]

    def test_update_node_adds_tag_if_missing(self, tmp_path):
        """Nodes without tags (e.g. older files) get the tag added on update."""
        path = create_node("project", {"name": "Ideate", "status": "draft", "description": _DESC}, tmp_path)
        # Manually strip tags from frontmatter to simulate an old file
        node = get_node(path)
        update_node(path, {"tags": []})
        updated = update_node(path, {"status": "active"})
        node = get_node(updated)
        assert "project/ideate" in node["frontmatter"]["tags"]

    def test_child_node_no_project_file_no_tag(self, tmp_path):
        """When no Project - *.md exists, child nodes get no auto tag."""
        path = create_node("module", {
            "name": "Auth", "status": "draft",
            "belongs_to": "[[Project - Missing]]",
        }, tmp_path)
        node = get_node(path)
        # No project file present, tags should be empty (no project tag added)
        assert not any(t.startswith("project/") for t in node["frontmatter"].get("tags", []))


class TestResolveLinks:
    def test_fixture_vault_all_valid(self):
        result = resolve_links(FIXTURE_DIR)
        assert len(result["broken"]) == 0
        assert len(result["valid"]) > 0

    def test_broken_link_detected(self, tmp_path):
        create_node("feature", {
            "name": "Bad", "status": "draft",
            "belongs_to": "[[Module - Missing]]",
            "implements": ["[[User Story - Missing]]"],
        }, tmp_path)
        result = resolve_links(tmp_path)
        assert len(result["broken"]) >= 2


class TestBuildIndex:
    def test_fixture_vault(self):
        index = build_index(FIXTURE_DIR)
        assert len(index["nodes"]) == 10
        assert index["project"] == "My Project"


class TestGenerateContext:
    def test_end_to_end(self):
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        assert "# Context Bundle: JWT Login" in ctx
        assert "## Project" in ctx
        assert "## User Stories" in ctx

    def test_nonexistent_raises(self):
        with pytest.raises(NodeNotFoundError):
            generate_context("Nonexistent", FIXTURE_DIR)

    def test_create_and_generate(self, tmp_path):
        """Create a minimal graph from scratch and generate context."""
        create_node("project", {"name": "P", "status": "active", "description": _DESC}, tmp_path)
        create_node("module", {
            "name": "M", "status": "active",
            "belongs_to": "[[Project - P]]",
        }, tmp_path)
        create_node("persona", {
            "name": "User", "status": "active",
            "belongs_to": "[[Project - P]]",
        }, tmp_path)
        create_node("user-story", {
            "name": "Do Thing", "status": "draft",
            "belongs_to": "[[Module - M]]",
            "actors": ["[[Persona - User]]"],
        }, tmp_path, body_sections={"Story": "As a User, I want to do a thing.", "Acceptance Criteria": "- Thing is done"})
        create_node("feature", {
            "name": "Thing Feature", "status": "draft",
            "belongs_to": "[[Module - M]]",
            "implements": ["[[User Story - Do Thing]]"],
        }, tmp_path)

        ctx = generate_context("Thing Feature", tmp_path)
        assert "# Context Bundle: Thing Feature" in ctx
        assert "## Project" in ctx
        assert "productivity app" in ctx
        assert "## User Stories" in ctx
        assert "Thing is done" in ctx
        assert "As a User" in ctx
