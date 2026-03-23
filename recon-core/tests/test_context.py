"""Tests for context builder — the MVP gate."""
from pathlib import Path

import pytest

from deploysquad_recon_core.context import generate_context, write_context
from deploysquad_recon_core.errors import NodeNotFoundError


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "sample_vault" / "my-project"


class TestGenerateContext:
    def test_generates_for_fixture_feature(self):
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        assert isinstance(ctx, str)
        assert len(ctx) > 100

    def test_starts_with_version_comment(self):
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        assert ctx.startswith("<!-- context_bundle_version: 1 -->")

    def test_has_title(self):
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        assert "# Context Bundle: JWT Login" in ctx

    def test_project_section(self):
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        assert "## Project" in ctx
        assert "My Project" in ctx
        assert "A sample project for testing" in ctx

    def test_goals_section(self):
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        assert "## Goals" in ctx
        assert "Fast Delivery" in ctx
        assert "Deliver features quickly" in ctx

    def test_version_section(self):
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        assert "## Version" in ctx
        assert "MVP" in ctx
        assert "sequence: 1" in ctx
        assert "2026-06-01" in ctx

    def test_module_section(self):
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        assert "## Module" in ctx
        assert "Auth" in ctx

    def test_user_stories_section(self):
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        assert "## User Stories" in ctx
        assert "Login" in ctx
        assert "Acceptance Criteria" in ctx
        assert "Developer can authenticate with email and password" in ctx

    def test_user_story_body_included(self):
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        assert "log in with my credentials" in ctx

    def test_constraints_section(self):
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        assert "## Constraints" in ctx
        assert "MIT License" in ctx
        assert "All code must be MIT licensed" in ctx

    def test_decisions_section(self):
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        assert "## Decisions" in ctx
        assert "Use JWT" in ctx
        assert "JWT tokens for stateless authentication" in ctx

    def test_nonexistent_feature_raises(self):
        with pytest.raises(NodeNotFoundError):
            generate_context("Nonexistent", FIXTURE_DIR)

    def test_no_dependencies_section_when_empty(self):
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        # The fixture feature has depends_on: [], so no Dependencies section
        assert "## Dependencies" not in ctx

    def test_no_related_section_when_empty(self):
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        # The fixture feature has related_to: [], so no Related section
        assert "## Related" not in ctx

    def test_goals_deduplicated(self):
        """Goal - Fast Delivery is referenced by both Feature and User Story.
        It should appear only once in the output."""
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        assert ctx.count("### Fast Delivery") == 1


class TestGenerateContextGovernedByDecision:
    """Exercise the governed_by → decision branch (context.py lines 85-93).

    The existing fixture feature only has a Constraint in governed_by.  This
    class builds a minimal temporary vault where the Feature's governed_by
    list contains a Decision wikilink, ensuring that branch is reached.
    """

    @pytest.fixture()
    def vault(self, tmp_path):
        """Create a minimal vault with a Feature governed_by a Decision."""
        project_dir = tmp_path / "test-project"

        # Project node (lives at root)
        (project_dir).mkdir(parents=True)
        (project_dir / "Project - Temp Project.md").write_text(
            "---\n"
            "type: project\n"
            "schema_version: 1\n"
            "name: Temp Project\n"
            "status: draft\n"
            "description: A minimal project for testing the governed_by decision branch.\n"
            "---\n"
        )

        # Module
        modules_dir = project_dir / "modules"
        modules_dir.mkdir()
        (modules_dir / "Module - Core.md").write_text(
            "---\n"
            "type: module\n"
            "schema_version: 1\n"
            "name: Core\n"
            "status: active\n"
            "belongs_to: \"[[Project - Temp Project]]\"\n"
            "actors: []\n"
            "governed_by: []\n"
            "---\n"
            "\n"
            "## Description\n"
            "\n"
            "Core module.\n"
        )

        # Decision (the node we expect to appear in generated context)
        decisions_dir = project_dir / "decisions"
        decisions_dir.mkdir()
        (decisions_dir / "Decision - Token Strategy.md").write_text(
            "---\n"
            "type: decision\n"
            "schema_version: 1\n"
            "name: Token Strategy\n"
            "status: active\n"
            "belongs_to: \"[[Module - Core]]\"\n"
            "governed_by: []\n"
            "---\n"
            "\n"
            "## Decision\n"
            "\n"
            "Use short-lived tokens for all API calls.\n"
            "\n"
            "## Rationale\n"
            "\n"
            "Reduces exposure window if a token is compromised.\n"
        )

        # User Story (Feature.implements requires min 1)
        us_dir = project_dir / "user-stories"
        us_dir.mkdir()
        (us_dir / "User Story - Create Account.md").write_text(
            "---\n"
            "type: user-story\n"
            "schema_version: 1\n"
            "name: Create Account\n"
            "status: draft\n"
            "belongs_to: \"[[Module - Core]]\"\n"
            "actors:\n"
            "  - \"[[Persona - Admin]]\"\n"
            "supports: []\n"
            "acceptance_criteria: []\n"
            "---\n"
            "\n"
            "## Story\n"
            "\n"
            "As an admin I want to create accounts.\n"
        )

        # Persona (referenced by User Story actors)
        personas_dir = project_dir / "personas"
        personas_dir.mkdir()
        (personas_dir / "Persona - Admin.md").write_text(
            "---\n"
            "type: persona\n"
            "schema_version: 1\n"
            "name: Admin\n"
            "status: active\n"
            "belongs_to: \"[[Project - Temp Project]]\"\n"
            "---\n"
        )

        # Feature — governed_by references the Decision directly
        features_dir = project_dir / "features"
        features_dir.mkdir()
        (features_dir / "Feature - Account Setup.md").write_text(
            "---\n"
            "type: feature\n"
            "schema_version: 1\n"
            "name: Account Setup\n"
            "status: draft\n"
            "belongs_to: \"[[Module - Core]]\"\n"
            "implements:\n"
            "  - \"[[User Story - Create Account]]\"\n"
            "governed_by:\n"
            "  - \"[[Decision - Token Strategy]]\"\n"
            "depends_on: []\n"
            "related_to: []\n"
            "---\n"
            "\n"
            "## Description\n"
            "\n"
            "Account setup feature governed by the Token Strategy decision.\n"
        )

        return project_dir

    def test_decision_appears_in_context_via_governed_by(self, vault):
        """governed_by → decision branch: Decision reached via Feature.governed_by."""
        ctx = generate_context("Account Setup", vault)
        assert "## Decisions" in ctx
        assert "Token Strategy" in ctx

    def test_decision_body_included(self, vault):
        """Decision body text is rendered in the Decisions section."""
        ctx = generate_context("Account Setup", vault)
        assert "Use short-lived tokens for all API calls." in ctx


class TestWriteContext:
    def test_write_to_explicit_path(self):
        """write_context writes to a given vault-relative path."""
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        out_path = write_context(ctx, "features/CONTEXT - JWT Login.md", FIXTURE_DIR)
        assert out_path == Path("features/CONTEXT - JWT Login.md")
        full = FIXTURE_DIR / out_path
        assert full.exists()
        assert full.read_text() == ctx
        # Clean up
        full.unlink()

    def test_write_auto_path(self):
        """write_context with output_path='auto' writes to features/CONTEXT - {name}.md."""
        ctx = generate_context("JWT Login", FIXTURE_DIR)
        out_path = write_context(ctx, "auto", FIXTURE_DIR, feature_name="JWT Login")
        assert out_path == Path("features/CONTEXT - JWT Login.md")
        full = FIXTURE_DIR / out_path
        assert full.exists()
        assert full.read_text() == ctx
        # Clean up
        full.unlink()

    def test_write_auto_creates_parent_dir(self, tmp_path):
        """write_context with 'auto' creates the features/ dir if missing."""
        ctx = "# Test context"
        out_path = write_context(ctx, "auto", tmp_path, feature_name="New Thing")
        assert out_path == Path("features/CONTEXT - New Thing.md")
        full = tmp_path / out_path
        assert full.exists()
        assert full.read_text() == ctx
