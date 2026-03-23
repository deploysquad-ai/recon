"""Tests for MCP server tool functions."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch
from deploysquad_recon_core.mcp_server import create_node_tool, get_node_tool, list_nodes_tool, update_node_tool
from deploysquad_recon_core.mcp_server import resolve_links_tool, build_index_tool, generate_context_tool
from deploysquad_recon_core.mcp_server import get_vault_status_tool, configure_vault_tool, embed_nodes_tool, find_similar_tool


_DESC = "A productivity app that helps users manage their daily tasks"


@pytest.fixture
def vault_dir(tmp_path):
    """Create a minimal vault directory."""
    return tmp_path


@pytest.fixture
def mock_vault_path(vault_dir):
    """Patch VAULT_PATH env var."""
    with patch("deploysquad_recon_core.mcp_server.PROJECT_DIR", vault_dir):
        yield vault_dir


def test_create_node_returns_relative_path(mock_vault_path):
    """create_node tool should return vault-relative file path."""
    result = create_node_tool(
        node_type="project",
        data={"name": "Test Project", "status": "draft", "description": _DESC},
    )
    parsed = json.loads(result)
    assert parsed["file_path"] == "Project - Test Project.md"
    assert (mock_vault_path / "Project - Test Project.md").exists()


def test_create_node_with_body_sections(mock_vault_path):
    """create_node tool should pass body_sections through."""
    result = create_node_tool(
        node_type="project",
        data={"name": "Test Project", "status": "draft", "description": _DESC},
        body_sections={"Description": "Full description here"},
    )
    parsed = json.loads(result)
    assert parsed["file_path"] == "Project - Test Project.md"
    content = (mock_vault_path / "Project - Test Project.md").read_text()
    assert "Full description here" in content


def test_create_node_validation_error(mock_vault_path):
    """create_node tool should return error for invalid data."""
    result = create_node_tool(
        node_type="project",
        data={"name": "Test"},  # missing required fields
    )
    parsed = json.loads(result)
    assert "error" in parsed


def test_get_node_returns_frontmatter_and_body(mock_vault_path):
    """get_node should return frontmatter, body_sections, and file_path."""
    # Create a node first
    create_node_tool(
        node_type="project",
        data={"name": "Test Project", "status": "draft", "description": _DESC},
        body_sections={"Description": "Full desc"},
    )
    result = get_node_tool(file_path="Project - Test Project.md")
    parsed = json.loads(result)
    assert parsed["frontmatter"]["name"] == "Test Project"
    assert parsed["body_sections"]["Description"] == "Full desc"
    assert parsed["file_path"] == "Project - Test Project.md"


def test_get_node_not_found(mock_vault_path):
    """get_node should return error for missing file."""
    result = get_node_tool(file_path="Project - Nonexistent.md")
    parsed = json.loads(result)
    assert "error" in parsed


def test_get_node_with_subfolder_path(mock_vault_path):
    """get_node should work with nodes in subfolders (non-project nodes)."""
    # Create project first (required for belongs_to)
    create_node_tool(
        node_type="project",
        data={"name": "P1", "status": "draft", "description": _DESC},
    )
    create_node_tool(
        node_type="goal",
        data={"name": "G1", "status": "draft", "belongs_to": "[[Project - P1]]"},
    )
    result = get_node_tool(file_path="goals/Goal - G1.md")
    parsed = json.loads(result)
    assert parsed["frontmatter"]["name"] == "G1"
    assert parsed["file_path"] == "goals/Goal - G1.md"


def test_list_nodes_returns_all(mock_vault_path):
    """list_nodes should return all nodes when no filter."""
    create_node_tool(
        node_type="project",
        data={"name": "P1", "status": "draft", "description": _DESC},
    )
    result = list_nodes_tool()
    parsed = json.loads(result)
    assert len(parsed) == 1
    assert parsed[0]["name"] == "P1"
    assert parsed[0]["file_path"] == "Project - P1.md"


def test_list_nodes_filtered_by_type(mock_vault_path):
    """list_nodes should filter by node_type."""
    create_node_tool(
        node_type="project",
        data={"name": "P1", "status": "draft", "description": _DESC},
    )
    # Create a goal that belongs to the project
    create_node_tool(
        node_type="goal",
        data={
            "name": "G1",
            "status": "draft",
            "belongs_to": "[[Project - P1]]",
        },
    )
    result = list_nodes_tool(node_type="goal")
    parsed = json.loads(result)
    assert len(parsed) == 1
    assert parsed[0]["type"] == "goal"


def test_update_node_changes_fields(mock_vault_path):
    """update_node should merge updates into existing frontmatter."""
    create_node_tool(
        node_type="project",
        data={"name": "P1", "status": "draft", "description": _DESC},
    )
    result = update_node_tool(
        file_path="Project - P1.md",
        updates={"status": "active"},
    )
    parsed = json.loads(result)
    assert parsed["file_path"] == "Project - P1.md"
    # Verify the update persisted
    get_result = json.loads(get_node_tool(file_path="Project - P1.md"))
    assert get_result["frontmatter"]["status"] == "active"


def test_update_node_replaces_body_sections(mock_vault_path):
    """update_node with body_sections should replace body."""
    create_node_tool(
        node_type="project",
        data={"name": "P1", "status": "draft", "description": _DESC},
        body_sections={"Description": "Old"},
    )
    result = update_node_tool(
        file_path="Project - P1.md",
        updates={},
        body_sections={"Description": "New description"},
    )
    parsed = json.loads(result)
    assert "error" not in parsed
    content = (mock_vault_path / "Project - P1.md").read_text()
    assert "New description" in content


def test_update_node_validation_error(mock_vault_path):
    """update_node should return error for invalid updates."""
    create_node_tool(
        node_type="project",
        data={"name": "P1", "status": "draft", "description": _DESC},
    )
    result = update_node_tool(
        file_path="Project - P1.md",
        updates={"status": "invalid_status"},
    )
    parsed = json.loads(result)
    assert "error" in parsed


def _create_minimal_graph(mock_vault_path):
    """Helper: create a minimal graph with Project, Module, User Story, Feature."""
    create_node_tool(
        node_type="project",
        data={"name": "P1", "status": "draft", "description": _DESC},
    )
    create_node_tool(
        node_type="persona",
        data={"name": "Dev", "status": "draft", "belongs_to": "[[Project - P1]]"},
    )
    create_node_tool(
        node_type="module",
        data={"name": "Core", "status": "draft", "belongs_to": "[[Project - P1]]",
              "actors": ["[[Persona - Dev]]"]},
    )
    create_node_tool(
        node_type="user-story",
        data={"name": "Do stuff", "status": "draft", "belongs_to": "[[Module - Core]]",
              "actors": ["[[Persona - Dev]]"]},
        body_sections={"Acceptance Criteria": "- It works"},
    )
    create_node_tool(
        node_type="feature",
        data={"name": "Thing", "status": "draft", "belongs_to": "[[Module - Core]]",
              "implements": ["[[User Story - Do stuff]]"],
              "actors": ["[[Persona - Dev]]"]},
    )


def test_resolve_links_all_valid(mock_vault_path):
    """resolve_links should find no broken links in a valid graph."""
    _create_minimal_graph(mock_vault_path)
    result = resolve_links_tool()
    parsed = json.loads(result)
    assert len(parsed["broken"]) == 0
    assert len(parsed["valid"]) > 0


def test_build_index_returns_nodes_and_edges(mock_vault_path):
    """build_index should return structured index data with nodes containing edge info."""
    _create_minimal_graph(mock_vault_path)
    result = build_index_tool()
    parsed = json.loads(result)
    assert "nodes" in parsed
    # edges are embedded per-node in the index structure
    assert any("edges" in node for node in parsed["nodes"].values())


def test_generate_context_returns_markdown(mock_vault_path):
    """generate_context should return CONTEXT.md string for a feature."""
    _create_minimal_graph(mock_vault_path)
    result = generate_context_tool(feature_name="Thing")
    parsed = json.loads(result)
    assert "context" in parsed
    assert "Project" in parsed["context"]  # Should contain project info


def test_get_vault_status_not_configured():
    """get_vault_status returns is_configured=False when VAULT_PATH is default '.'."""
    with patch("deploysquad_recon_core.mcp_server.PROJECT_DIR", Path(".")):
        result = json.loads(get_vault_status_tool())
    assert result["is_configured"] is False
    assert result["vault_path"] == "."


def test_get_vault_status_configured(tmp_path):
    """get_vault_status returns is_configured=True when VAULT_PATH is a real directory."""
    with patch("deploysquad_recon_core.mcp_server.PROJECT_DIR", tmp_path):
        result = json.loads(get_vault_status_tool())
    assert result["is_configured"] is True
    assert result["vault_path"] == str(tmp_path)


def test_get_vault_status_nonexistent_path():
    """get_vault_status returns is_configured=False when path doesn't exist."""
    with patch("deploysquad_recon_core.mcp_server.PROJECT_DIR", Path("/nonexistent/vault")):
        result = json.loads(get_vault_status_tool())
    assert result["is_configured"] is False


def test_configure_vault_tool_sets_project_dir(tmp_path):
    """configure_vault_tool should update PROJECT_DIR in-memory."""
    with patch("deploysquad_recon_core.mcp_server.PROJECT_DIR", Path(".")):
        result = json.loads(configure_vault_tool(vault_path=str(tmp_path)))
    assert result["is_configured"] is True
    assert result["vault_path"] == str(tmp_path)


def test_configure_vault_tool_rejects_nonexistent():
    """configure_vault_tool should return error for nonexistent path."""
    result = json.loads(configure_vault_tool(vault_path="/nonexistent/vault/path"))
    assert result["error"] == "DirectoryNotFound"


def test_configure_vault_tool_expands_tilde(tmp_path):
    """configure_vault_tool should expand ~ in paths."""
    with patch("os.path.expanduser", return_value=str(tmp_path)):
        result = json.loads(configure_vault_tool(vault_path="~/my-vault"))
    assert result["is_configured"] is True
    assert result["vault_path"] == str(tmp_path)


def test_configure_vault_enables_subsequent_tools(tmp_path):
    """After configure_vault_tool, other tools should use the new path."""
    import deploysquad_recon_core.mcp_server as mod
    old_dir = mod.PROJECT_DIR
    try:
        configure_vault_tool(vault_path=str(tmp_path))
        # Now create_node_tool should write to tmp_path
        result = json.loads(create_node_tool(
            node_type="project",
            data={"name": "Test", "status": "draft", "description": _DESC},
        ))
        assert "error" not in result
        assert (tmp_path / "Project - Test.md").exists()
    finally:
        mod.PROJECT_DIR = old_dir


def test_embed_nodes_tool_uses_project_dir(mock_vault_path):
    """embed_nodes_tool should use PROJECT_DIR, not a caller-supplied path."""
    with patch("deploysquad_recon_core.embeddings.embed_nodes") as mock_embed:
        mock_embed.return_value = {"embedded": 3}
        result = json.loads(embed_nodes_tool())
    mock_embed.assert_called_once_with(mock_vault_path)
    assert result == {"embedded": 3}


def test_find_similar_tool_uses_project_dir(mock_vault_path):
    """find_similar_tool should use PROJECT_DIR, not a caller-supplied path."""
    node_path = "features/Feature - Login.md"
    fake_results = [(mock_vault_path / "features/Feature - Other.md", 0.92)]
    with patch("deploysquad_recon_core.embeddings.find_similar") as mock_find:
        mock_find.return_value = fake_results
        result = json.loads(find_similar_tool(node_path=node_path, top_k=3, threshold=0.8))
    mock_find.assert_called_once_with(
        mock_vault_path / node_path,
        mock_vault_path,
        top_k=3,
        threshold=0.8,
    )
    assert result["results"] == [{"path": "features/Feature - Other.md", "score": 0.92}]


def test_generate_context_with_output_path(mock_vault_path):
    """generate_context_tool with output_path writes file and returns path."""
    _create_minimal_graph(mock_vault_path)
    result = json.loads(generate_context_tool(feature_name="Thing", output_path="features/CONTEXT - Thing.md"))
    assert "context" in result
    assert result["output_path"] == "features/CONTEXT - Thing.md"
    written = mock_vault_path / "features" / "CONTEXT - Thing.md"
    assert written.exists()
    assert written.read_text() == result["context"]


def test_generate_context_with_auto_output_path(mock_vault_path):
    """generate_context_tool with output_path='auto' uses feature name for path."""
    _create_minimal_graph(mock_vault_path)
    result = json.loads(generate_context_tool(feature_name="Thing", output_path="auto"))
    assert result["output_path"] == "features/CONTEXT - Thing.md"
    written = mock_vault_path / "features" / "CONTEXT - Thing.md"
    assert written.exists()


def test_generate_context_without_output_path_returns_string_only(mock_vault_path):
    """generate_context_tool without output_path returns context only (backward compat)."""
    _create_minimal_graph(mock_vault_path)
    result = json.loads(generate_context_tool(feature_name="Thing"))
    assert "context" in result
    assert "output_path" not in result
