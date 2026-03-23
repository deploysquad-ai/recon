"""Tests for CLI subcommands (OpenClaw shell interface)."""
import json
import subprocess
import sys
from pathlib import Path
import pytest


PYTHON = sys.executable
VAULT = Path(__file__).parent / "fixtures" / "sample_vault" / "my-project"


def run(args: list[str]) -> dict:
    """Run a CLI subcommand and return parsed JSON output."""
    result = subprocess.run(
        [PYTHON, "-m", "deploysquad_recon_core"] + args,
        capture_output=True, text=True,
        cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 0, f"Command failed:\n{result.stderr}"
    return json.loads(result.stdout)


def test_list_nodes_returns_list():
    out = run(["list_nodes", "--project-dir", str(VAULT)])
    assert isinstance(out, list)
    assert len(out) > 0
    assert "type" in out[0]
    assert "name" in out[0]


def test_list_nodes_filtered_by_type():
    out = run(["list_nodes", "--project-dir", str(VAULT), "--type", "feature"])
    assert all(n["type"] == "feature" for n in out)


def test_get_node_returns_frontmatter(tmp_path):
    # Use an existing fixture file
    node_file = VAULT / "features" / "Feature - JWT Login.md"
    out = run(["get_node", "--file", str(node_file)])
    assert "frontmatter" in out
    assert out["frontmatter"]["type"] == "feature"


def test_build_index_returns_summary(tmp_path):
    out = run(["build_index", "--project-dir", str(VAULT)])
    assert out["status"] == "built"
    assert out["node_count"] > 0


def test_generate_context_returns_markdown():
    out = run(["generate_context", "--feature", "JWT Login", "--project-dir", str(VAULT)])
    assert "content" in out
    assert "JWT" in out["content"]


def test_create_node_roundtrip(tmp_path):
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    # Create project first
    run(["create_node", "--type", "project", "--project-dir", str(project_dir),
         "--data", json.dumps({"name": "Test Project", "description": "A productivity app that helps users manage their daily tasks", "status": "active"})])
    # Then create a goal
    out = run(["create_node", "--type", "goal", "--project-dir", str(project_dir),
               "--data", json.dumps({
                   "name": "Ship Fast",
                   "belongs_to": "[[Project - Test Project]]",
                   "status": "active"
               })])
    assert "file_path" in out
    assert Path(out["file_path"]).exists()


def test_unknown_subcommand_exits_nonzero():
    result = subprocess.run(
        [PYTHON, "-m", "deploysquad_recon_core", "nonexistent_command"],
        capture_output=True, text=True,
        cwd=Path(__file__).parent.parent
    )
    assert result.returncode != 0
