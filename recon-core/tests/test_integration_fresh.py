"""Integration tests simulating a fresh install experience.

Run via: .venv/bin/python -m pytest tests/test_integration_fresh.py -v
Or from PyPI (true fresh install):
    uv run --with deploysquad-recon-core python -m pytest tests/test_integration_fresh.py -v

Tests cover the full user journey:
  1. Vault not configured on startup
  2. Configure vault (valid, invalid, tilde expansion)
  3. Full 10-node authoring flow with wikilinks
  4. Graph operations (links, index, context)
  5. Reconfigure vault mid-session
  6. CLI subcommand parity
"""
from __future__ import annotations

import json
import os
import subprocess
import shutil
import sys
import textwrap
from pathlib import Path

import pytest

import deploysquad_recon_core.mcp_server as mcp_mod
from deploysquad_recon_core.mcp_server import (
    configure_vault_tool,
    create_node_tool,
    get_node_tool,
    get_vault_status_tool,
    list_nodes_tool,
    update_node_tool,
    resolve_links_tool,
    build_index_tool,
    generate_context_tool,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DESC = "A productivity app that helps users manage their daily tasks"


def _json(result: str) -> dict | list:
    return json.loads(result)


def _assert_ok(result: str) -> dict | list:
    parsed = _json(result)
    if isinstance(parsed, dict):
        assert "error" not in parsed, f"Unexpected error: {parsed}"
    return parsed


def _assert_error(result: str) -> dict:
    parsed = _json(result)
    assert "error" in parsed, f"Expected error but got: {parsed}"
    return parsed


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def vault_a(tmp_path):
    """First empty vault directory."""
    d = tmp_path / "vault_a"
    d.mkdir()
    return d


@pytest.fixture
def vault_b(tmp_path):
    """Second empty vault directory for reconfiguration tests."""
    d = tmp_path / "vault_b"
    d.mkdir()
    return d


@pytest.fixture(autouse=True)
def _reset_project_dir():
    """Reset PROJECT_DIR to default before and after each test."""
    original = mcp_mod.PROJECT_DIR
    mcp_mod.PROJECT_DIR = Path(".")
    yield
    mcp_mod.PROJECT_DIR = original


# ===========================================================================
# 1. Fresh install baseline
# ===========================================================================

class TestFreshInstallBaseline:
    """Vault is not configured on first start."""

    def test_vault_not_configured_by_default(self):
        result = _json(get_vault_status_tool())
        assert result["is_configured"] is False
        assert result["vault_path"] == "."

    def test_tools_still_return_errors_not_crashes(self):
        """MCP tools should return JSON errors, not crash, when vault is unconfigured."""
        result = _json(list_nodes_tool())
        # Listing an unconfigured vault (cwd) shouldn't crash
        assert isinstance(result, list)


# ===========================================================================
# 2. Vault configuration
# ===========================================================================

class TestVaultConfiguration:
    """configure_vault_tool handles all edge cases."""

    def test_configure_valid_path(self, vault_a):
        result = _assert_ok(configure_vault_tool(vault_path=str(vault_a)))
        assert result["is_configured"] is True
        assert result["vault_path"] == str(vault_a)

    def test_configure_invalid_path(self):
        result = _assert_error(configure_vault_tool(vault_path="/nonexistent/vault/xyz"))
        assert result["error"] == "DirectoryNotFound"

    def test_configure_expands_tilde(self, vault_a, monkeypatch):
        monkeypatch.setattr("os.path.expanduser", lambda p: str(vault_a))
        result = _assert_ok(configure_vault_tool(vault_path="~/my-vault"))
        assert result["is_configured"] is True

    def test_status_reflects_configuration(self, vault_a):
        # Before
        assert _json(get_vault_status_tool())["is_configured"] is False
        # Configure
        configure_vault_tool(vault_path=str(vault_a))
        # After
        assert _json(get_vault_status_tool())["is_configured"] is True
        assert _json(get_vault_status_tool())["vault_path"] == str(vault_a)

    def test_configure_twice_updates_path(self, vault_a, vault_b):
        configure_vault_tool(vault_path=str(vault_a))
        assert _json(get_vault_status_tool())["vault_path"] == str(vault_a)
        configure_vault_tool(vault_path=str(vault_b))
        assert _json(get_vault_status_tool())["vault_path"] == str(vault_b)


# ===========================================================================
# 3. Full authoring flow — all 10 node types
# ===========================================================================

class TestFullAuthoringFlow:
    """Create all 10 node types in correct order with valid wikilinks."""

    @pytest.fixture(autouse=True)
    def setup_vault(self, vault_a):
        configure_vault_tool(vault_path=str(vault_a))
        self.vault = vault_a

    def _create(self, node_type, data, body_sections=None):
        result = _assert_ok(create_node_tool(
            node_type=node_type, data=data, body_sections=body_sections,
        ))
        assert "file_path" in result
        return result

    def test_create_all_10_node_types(self):
        """Author a complete graph: Project → ... → Version."""
        # 1. Project
        self._create("project", {
            "name": "FreshApp", "status": "draft",
            "description": _DESC,
        })

        # 2. Goal
        self._create("goal", {
            "name": "Ship MVP", "status": "active",
            "belongs_to": "[[Project - FreshApp]]",
        })

        # 3. Persona
        self._create("persona", {
            "name": "Developer", "status": "active",
            "belongs_to": "[[Project - FreshApp]]",
        }, body_sections={"Goals": "Build stuff", "Context": "Senior dev"})

        # 4. Constraint
        self._create("constraint", {
            "name": "Must be open source", "status": "active",
            "belongs_to": "[[Project - FreshApp]]",
        })

        # 5. Module
        self._create("module", {
            "name": "Core Engine", "status": "draft",
            "belongs_to": "[[Project - FreshApp]]",
            "actors": ["[[Persona - Developer]]"],
        })

        # 6. Decision
        self._create("decision", {
            "name": "Use Python for backend", "status": "active",
            "belongs_to": "[[Module - Core Engine]]",
            "governed_by": ["[[Constraint - Must be open source]]"],
        })

        # 7. User Story
        self._create("user-story", {
            "name": "Create a project", "status": "draft",
            "belongs_to": "[[Module - Core Engine]]",
            "actors": ["[[Persona - Developer]]"],
        }, body_sections={"Acceptance Criteria": "- Project file exists\n- Valid frontmatter"})

        # 8. Epic
        self._create("epic", {
            "name": "Project setup", "status": "draft",
            "belongs_to": "[[Module - Core Engine]]",
        })

        # 9. Feature
        self._create("feature", {
            "name": "Project creation wizard", "status": "draft",
            "belongs_to": "[[Module - Core Engine]]",
            "implements": ["[[User Story - Create a project]]"],
            "actors": ["[[Persona - Developer]]"],
        })

        # 10. Version
        self._create("version", {
            "name": "v0.1", "status": "draft",
            "belongs_to": "[[Project - FreshApp]]",
            "sequence": 1,
            "features": ["[[Feature - Project creation wizard]]"],
        })

        # Verify all 10 nodes exist
        nodes = _json(list_nodes_tool())
        assert len(nodes) == 10
        types_created = {n["type"] for n in nodes}
        assert types_created == {
            "project", "goal", "persona", "constraint", "module",
            "decision", "user-story", "epic", "feature", "version",
        }

    def test_list_nodes_filters_by_type(self):
        self._create("project", {
            "name": "FilterTest", "status": "draft", "description": _DESC,
        })
        self._create("goal", {
            "name": "G1", "status": "draft",
            "belongs_to": "[[Project - FilterTest]]",
        })
        result = _json(list_nodes_tool(node_type="goal"))
        assert all(n["type"] == "goal" for n in result)

    def test_get_node_reads_back_correctly(self):
        self._create("project", {
            "name": "ReadBack", "status": "draft", "description": _DESC,
        }, body_sections={"Description": "Full description here"})

        result = _assert_ok(get_node_tool(file_path="Project - ReadBack.md"))
        assert result["frontmatter"]["name"] == "ReadBack"
        assert result["body_sections"]["Description"] == "Full description here"

    def test_update_node_persists_changes(self):
        self._create("project", {
            "name": "UpdateMe", "status": "draft", "description": _DESC,
        })
        _assert_ok(update_node_tool(
            file_path="Project - UpdateMe.md",
            updates={"status": "active"},
        ))
        result = _assert_ok(get_node_tool(file_path="Project - UpdateMe.md"))
        assert result["frontmatter"]["status"] == "active"

    def test_update_node_replaces_body_sections(self):
        self._create("project", {
            "name": "BodyUpdate", "status": "draft", "description": _DESC,
        }, body_sections={"Description": "Old"})
        _assert_ok(update_node_tool(
            file_path="Project - BodyUpdate.md",
            updates={},
            body_sections={"Description": "New content"},
        ))
        result = _assert_ok(get_node_tool(file_path="Project - BodyUpdate.md"))
        assert result["body_sections"]["Description"] == "New content"

    def test_create_duplicate_returns_error(self):
        self._create("project", {
            "name": "NoDup", "status": "draft", "description": _DESC,
        })
        result = _assert_error(create_node_tool(
            node_type="project",
            data={"name": "NoDup", "status": "draft", "description": _DESC},
        ))
        assert "Duplicate" in result["error"] or "exists" in result.get("message", "").lower()

    def test_create_with_invalid_data_returns_error(self):
        result = _assert_error(create_node_tool(
            node_type="project",
            data={"name": "Bad"},  # missing required fields
        ))
        assert "Validation" in result["error"]


# ===========================================================================
# 4. Graph operations
# ===========================================================================

class TestGraphOperations:
    """Link resolution, index building, and context generation."""

    @pytest.fixture(autouse=True)
    def setup_graph(self, vault_a):
        """Create a minimal connected graph for graph operation tests."""
        configure_vault_tool(vault_path=str(vault_a))
        self.vault = vault_a

        create_node_tool(node_type="project", data={
            "name": "GraphTest", "status": "draft", "description": _DESC,
        })
        create_node_tool(node_type="persona", data={
            "name": "Tester", "status": "active",
            "belongs_to": "[[Project - GraphTest]]",
        }, body_sections={"Goals": "Test things", "Context": "QA"})
        create_node_tool(node_type="module", data={
            "name": "Testing", "status": "draft",
            "belongs_to": "[[Project - GraphTest]]",
            "actors": ["[[Persona - Tester]]"],
        })
        create_node_tool(node_type="user-story", data={
            "name": "Run tests", "status": "draft",
            "belongs_to": "[[Module - Testing]]",
            "actors": ["[[Persona - Tester]]"],
        }, body_sections={"Acceptance Criteria": "- Tests pass"})
        create_node_tool(node_type="feature", data={
            "name": "Test runner", "status": "draft",
            "belongs_to": "[[Module - Testing]]",
            "implements": ["[[User Story - Run tests]]"],
            "actors": ["[[Persona - Tester]]"],
        })

    def test_resolve_links_no_broken(self):
        result = _assert_ok(resolve_links_tool())
        assert len(result["broken"]) == 0
        assert len(result["valid"]) > 0

    def test_build_index_returns_structure(self):
        result = _assert_ok(build_index_tool())
        assert "nodes" in result
        assert len(result["nodes"]) == 5
        # Verify edges exist on at least one node
        has_edges = any(
            "edges" in node and len(node["edges"]) > 0
            for node in result["nodes"].values()
        )
        assert has_edges, "Index should contain edges for connected nodes"

    def test_generate_context_produces_markdown(self):
        result = _assert_ok(generate_context_tool(feature_name="Test runner"))
        context = result["context"]
        assert "GraphTest" in context  # Project name appears
        assert "Test runner" in context  # Feature name appears
        assert "Run tests" in context  # User story appears
        assert len(context) > 100  # Non-trivial content


# ===========================================================================
# 5. Reconfigure vault mid-session
# ===========================================================================

class TestReconfigureMidSession:
    """Switching vaults mid-session isolates data correctly."""

    def test_nodes_isolated_between_vaults(self, vault_a, vault_b):
        # Create node in vault A
        configure_vault_tool(vault_path=str(vault_a))
        _assert_ok(create_node_tool(
            node_type="project",
            data={"name": "VaultA Project", "status": "draft", "description": _DESC},
        ))
        nodes_a = _json(list_nodes_tool())
        assert len(nodes_a) == 1

        # Switch to vault B
        configure_vault_tool(vault_path=str(vault_b))
        nodes_b = _json(list_nodes_tool())
        assert len(nodes_b) == 0  # Vault B is empty

        # Create node in vault B
        _assert_ok(create_node_tool(
            node_type="project",
            data={"name": "VaultB Project", "status": "draft", "description": _DESC},
        ))
        nodes_b = _json(list_nodes_tool())
        assert len(nodes_b) == 1
        assert nodes_b[0]["name"] == "VaultB Project"

        # Switch back to vault A — original node still there
        configure_vault_tool(vault_path=str(vault_a))
        nodes_a = _json(list_nodes_tool())
        assert len(nodes_a) == 1
        assert nodes_a[0]["name"] == "VaultA Project"

    def test_get_node_after_reconfig(self, vault_a, vault_b):
        """get_node uses the newly configured vault, not the old one."""
        configure_vault_tool(vault_path=str(vault_a))
        _assert_ok(create_node_tool(
            node_type="project",
            data={"name": "OnlyInA", "status": "draft", "description": _DESC},
        ))

        # Switch to B — node from A should not be accessible
        configure_vault_tool(vault_path=str(vault_b))
        result = _assert_error(get_node_tool(file_path="Project - OnlyInA.md"))
        assert "NotFound" in result["error"] or "not found" in result.get("message", "").lower() or "No such file" in result.get("message", "")


# ===========================================================================
# 6. CLI subcommand parity
# ===========================================================================

class TestCLIParity:
    """CLI subcommands produce same results as MCP tools."""

    @pytest.fixture(autouse=True)
    def setup_vault(self, vault_a):
        configure_vault_tool(vault_path=str(vault_a))
        self.vault = vault_a
        create_node_tool(node_type="project", data={
            "name": "CLITest", "status": "draft", "description": _DESC,
        })

    def _run_cli(self, *args):
        """Run a CLI subcommand via the package entry point."""
        result = subprocess.run(
            [sys.executable, "-m", "deploysquad_recon_core", *args],
            capture_output=True, text=True,
        )
        return result

    def test_list_nodes_cli(self):
        result = self._run_cli("list_nodes", "--project-dir", str(self.vault))
        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert len(parsed) == 1
        assert parsed[0]["name"] == "CLITest"

    def test_get_node_cli(self):
        node_path = self.vault / "Project - CLITest.md"
        result = self._run_cli("get_node", "--file", str(node_path))
        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert parsed["frontmatter"]["name"] == "CLITest"

    def test_build_index_cli(self):
        result = self._run_cli("build_index", "--project-dir", str(self.vault))
        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert parsed["node_count"] == 1

    def test_resolve_links_cli(self):
        result = self._run_cli("resolve_links", "--project-dir", str(self.vault))
        assert result.returncode == 0
        parsed = json.loads(result.stdout)
        assert "broken_count" in parsed

    def test_unknown_subcommand_fails(self):
        result = self._run_cli("not_a_command")
        assert result.returncode != 0
