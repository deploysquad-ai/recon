"""Write validated node models to vault as .md files."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import frontmatter

from .paths import node_filepath
from ..errors import DuplicateNodeError
from ..models.base import BaseNode


def write_node(
    node: BaseNode,
    project_dir: Path,
    body_sections: dict[str, str] | None = None,
    overwrite: bool = False,
) -> Path:
    """Write a validated node model to the vault as a .md file.

    Args:
        node: Validated Pydantic model instance
        project_dir: Root directory of the project vault
        body_sections: Optional dict of {heading: content} for the body
        overwrite: If True, overwrites existing file

    Returns:
        Path to the written file

    Raises:
        DuplicateNodeError: File already exists and overwrite=False
    """
    file_path = node_filepath(node.type, node.name, project_dir)

    if file_path.exists() and not overwrite:
        raise DuplicateNodeError(f"Node already exists: {file_path}")

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.parent.chmod(0o755)

    # Build frontmatter dict, excluding None values
    # mode="json" ensures enums serialize to their string values
    fm_dict = node.model_dump(exclude_none=True, mode="json")

    # Build body from sections
    body = _render_body_sections(body_sections) if body_sections else ""

    post = frontmatter.Post(body, **fm_dict)
    content = frontmatter.dumps(post)

    # Atomic write: write to temp file then rename.
    # mkstemp creates files with mode 0600; chmod to 0644 so Obsidian can read them.
    fd, tmp_path = tempfile.mkstemp(dir=file_path.parent, suffix=".md.tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, file_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

    return file_path


def _render_body_sections(sections: dict[str, str]) -> str:
    """Render body sections dict into markdown with ## headings."""
    parts = []
    for heading, content in sections.items():
        parts.append(f"## {heading}\n\n{content}")
    return "\n\n".join(parts)
