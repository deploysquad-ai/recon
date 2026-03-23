"""recon-core: Engine for reading, writing, and validating Obsidian vault project graphs.

Public API:
    create_node(node_type, data, project_dir, body_sections=None) -> Path
    get_node(file_path) -> dict
    list_nodes(project_dir, node_type=None, status=None) -> list[dict]
    update_node(file_path, updates, body_sections=None) -> Path
    resolve_links(project_dir) -> dict
    build_index(project_dir) -> dict
    generate_context(feature_name, project_dir) -> str
    embed_nodes(project_dir, api_key=None) -> dict
    find_similar(node_path, project_dir, top_k=5, threshold=0.75) -> list[tuple[Path, float]]
"""
from __future__ import annotations

from pathlib import Path

from .errors import ValidationError, NodeNotFoundError, BrokenLinkError, DuplicateNodeError
from .models import NODE_TYPE_MAP, get_model_for_type
from .vault.reader import read_node
from .vault.writer import write_node
from .vault.paths import node_filepath, parse_filename, type_to_subfolder, find_project_name, project_tag
from .links import resolve_all_links
from .index import build_index as _build_index, write_index, read_index
from .context import generate_context as _generate_context
from .embeddings import embed_nodes, find_similar


def create_node(
    node_type: str,
    data: dict,
    project_dir: str | Path,
    body_sections: dict[str, str] | None = None,
) -> Path:
    """Create and write a new node to the vault.

    Args:
        node_type: One of the 10 node types (e.g. "feature", "user-story")
        data: Dict of frontmatter fields (type and schema_version auto-filled)
        project_dir: Root directory of the project vault
        body_sections: Optional dict of {heading: content} for the body

    Returns:
        Path to the created file

    Raises:
        ValidationError: Data fails schema validation
        DuplicateNodeError: Node already exists
        KeyError: Unknown node type
    """
    project_dir = Path(project_dir)
    model_cls = get_model_for_type(node_type)

    # Auto-fill type and schema_version
    full_data = {"type": node_type, "schema_version": 1, **data}

    # Auto-add project tag
    if node_type == "project":
        proj_name = data.get("name", "")
    else:
        proj_name = find_project_name(project_dir)

    if proj_name:
        tag = project_tag(proj_name)
        existing_tags = full_data.get("tags", [])
        if tag not in existing_tags:
            full_data["tags"] = existing_tags + [tag]

    try:
        model = model_cls(**full_data)
    except Exception as e:
        raise ValidationError(f"Validation failed for {node_type}: {e}") from e

    return write_node(model, project_dir, body_sections=body_sections)


def get_node(file_path: str | Path) -> dict:
    """Read and validate a node file.

    Returns dict with keys: frontmatter, body, body_sections, model, file_path
    """
    return read_node(Path(file_path))


def list_nodes(
    project_dir: str | Path,
    node_type: str | None = None,
    status: str | None = None,
) -> list[dict]:
    """List nodes in the project, optionally filtered by type and/or status.

    Returns list of dicts, each with: type, name, status, file_path
    """
    project_dir = Path(project_dir)
    results = []

    for md_file in sorted(project_dir.rglob("*.md")):
        if ".graph" in md_file.parts:
            continue
        parsed = parse_filename(md_file.name)
        if parsed is None:
            continue

        file_type, name = parsed

        if node_type and file_type != node_type:
            continue

        try:
            node_data = read_node(md_file)
        except Exception:
            continue
        node_status = node_data["model"].status
        if hasattr(node_status, "value"):
            node_status = node_status.value

        if status and node_status != status:
            continue

        results.append({
            "type": file_type,
            "name": name,
            "status": node_status,
            "file_path": md_file,
        })

    return results


def update_node(
    file_path: str | Path,
    updates: dict,
    body_sections: dict[str, str] | None = None,
) -> Path:
    """Update an existing node's frontmatter fields.

    Reads the current node, merges updates, validates, and rewrites.

    Args:
        file_path: Path to the existing node file
        updates: Dict of fields to update (merged with existing frontmatter)
        body_sections: If provided, replaces the body sections entirely

    Returns:
        Path to the updated file
    """
    file_path = Path(file_path)
    current = read_node(file_path)

    # Merge updates into existing frontmatter
    merged = {**current["frontmatter"], **updates}

    # Ensure project tag is preserved/added
    proj_name = find_project_name(
        file_path.parent.parent if type_to_subfolder(merged["type"]) else file_path.parent
    )
    if not proj_name and merged["type"] == "project":
        proj_name = merged.get("name", "")
    if proj_name:
        tag = project_tag(proj_name)
        existing_tags = merged.get("tags", [])
        if tag not in existing_tags:
            merged["tags"] = existing_tags + [tag]

    model_cls = get_model_for_type(merged["type"])
    try:
        model = model_cls(**merged)
    except Exception as e:
        raise ValidationError(f"Validation failed: {e}") from e

    # Use existing body sections if not replacing
    if body_sections is None:
        body_sections = current["body_sections"]

    # Derive project_dir from file_path based on node type.
    # Project nodes live at project_dir/Project - Name.md (subfolder is empty),
    # other nodes live at project_dir/subfolder/Type - Name.md.
    subfolder = type_to_subfolder(merged["type"])
    if subfolder:
        project_dir = file_path.parent.parent
    else:
        project_dir = file_path.parent

    return write_node(model, project_dir, body_sections=body_sections, overwrite=True)


def resolve_links(project_dir: str | Path) -> dict:
    """Check all wikilinks in the vault.

    Returns:
        {"valid": [LinkResult, ...], "broken": [LinkResult, ...]}
    """
    return resolve_all_links(Path(project_dir))


def build_index(project_dir: str | Path) -> dict:
    """Build the graph index from vault files.

    Returns the index dict. Does NOT write it to disk -- call write_index() for that.
    """
    return _build_index(Path(project_dir))


def generate_context(feature_name: str, project_dir: str | Path) -> str:
    """Generate a CONTEXT.md string for a Feature node."""
    return _generate_context(feature_name, Path(project_dir))
