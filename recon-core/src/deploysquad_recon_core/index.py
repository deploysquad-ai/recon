"""Build, read, and write .graph/index.json for fast graph traversal."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .vault.reader import read_node
from .vault.paths import parse_filename
from .links import extract_wikilinks


def build_index(project_dir: Path) -> dict:
    """Scan all .md node files in project_dir and build an index.

    Returns dict with schema:
    {
        "schema_version": 1,
        "built_at": "2026-03-23T...",
        "project": "<project name>",
        "nodes": {
            "relative/path.md": {
                "type": "feature",
                "name": "JWT Login",
                "status": "draft",
                "edges": {"belongs_to": ["[[Module - Auth]]"], ...}
            }
        }
    }
    """
    project_dir = Path(project_dir)
    nodes: dict[str, dict] = {}
    project_name = ""

    for md_file in sorted(project_dir.rglob("*.md")):
        # Skip .graph directory
        if ".graph" in md_file.parts:
            continue

        # Only process files that match node naming convention
        parsed = parse_filename(md_file.name)
        if parsed is None:
            continue

        result = read_node(md_file)
        model = result["model"]
        fm = result["frontmatter"]

        # Track project name
        if model.type == "project":
            project_name = model.name

        # Extract edges from frontmatter (only wikilink fields)
        edges: dict[str, list[str]] = {}
        for key, value in fm.items():
            links = extract_wikilinks(value) if isinstance(value, (str, list, dict)) else []
            if links:
                edges[key] = links

        # Relative path from project_dir
        rel_path = str(md_file.relative_to(project_dir))

        nodes[rel_path] = {
            "type": model.type,
            "name": model.name,
            "status": str(model.status.value) if hasattr(model.status, 'value') else str(model.status),
            "edges": dict(sorted(edges.items())),
        }

    return {
        "schema_version": 1,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "project": project_name,
        "nodes": dict(sorted(nodes.items())),
    }


def write_index(index: dict, project_dir: Path) -> Path:
    """Write index to .graph/index.json."""
    graph_dir = Path(project_dir) / ".graph"
    graph_dir.mkdir(parents=True, exist_ok=True)
    index_path = graph_dir / "index.json"
    index_path.write_text(json.dumps(index, indent=2, sort_keys=False) + "\n")
    return index_path


def read_index(project_dir: Path) -> dict:
    """Read .graph/index.json and return parsed dict."""
    index_path = Path(project_dir) / ".graph" / "index.json"
    return json.loads(index_path.read_text())
