"""Vault path utilities: slug generation, folder mapping, filename conventions."""
from __future__ import annotations

import re
from pathlib import Path

# Maps node type strings to vault subfolder names
_TYPE_TO_SUBFOLDER: dict[str, str] = {
    "project": "",
    "goal": "goals",
    "version": "versions",
    "persona": "personas",
    "constraint": "constraints",
    "module": "modules",
    "decision": "decisions",
    "user-story": "user-stories",
    "epic": "epics",
    "feature": "features",
}

# Maps node type strings to display names used in filenames
_TYPE_TO_DISPLAY: dict[str, str] = {
    "project": "Project",
    "goal": "Goal",
    "version": "Version",
    "persona": "Persona",
    "constraint": "Constraint",
    "module": "Module",
    "decision": "Decision",
    "user-story": "User Story",
    "epic": "Epic",
    "feature": "Feature",
}

# Reverse lookup: display name -> type string
_DISPLAY_TO_TYPE: dict[str, str] = {v: k for k, v in _TYPE_TO_DISPLAY.items()}


def type_to_subfolder(node_type: str) -> str:
    """Get the vault subfolder for a node type. Returns '' for project (lives at root)."""
    return _TYPE_TO_SUBFOLDER[node_type]


def get_type_display_name(node_type: str) -> str:
    """Return the display name for a node type (e.g. 'user-story' -> 'User Story')."""
    return _TYPE_TO_DISPLAY.get(node_type, node_type.title())


def node_filename(node_type: str, name: str) -> str:
    """Generate filename: 'Type - Name.md'."""
    display = _TYPE_TO_DISPLAY[node_type]
    return f"{display} - {name}.md"


def node_filepath(node_type: str, name: str, project_dir: Path) -> Path:
    """Full path to a node file within a project directory."""
    subfolder = _TYPE_TO_SUBFOLDER[node_type]
    filename = node_filename(node_type, name)
    if subfolder:
        return project_dir / subfolder / filename
    return project_dir / filename


def parse_filename(filename: str) -> tuple[str, str] | None:
    """Parse 'Type - Name.md' -> (type_string, name), or None if not a node file."""
    if not filename.endswith(".md"):
        return None
    stem = filename[:-3]  # Remove .md
    if " - " not in stem:
        return None
    display, name = stem.split(" - ", 1)
    node_type = _DISPLAY_TO_TYPE.get(display)
    if node_type is None:
        return None
    return (node_type, name)


def name_to_wikilink(node_type: str, name: str) -> str:
    """Generate a wikilink string: '[[Type - Name]]'."""
    display = _TYPE_TO_DISPLAY[node_type]
    return f"[[{display} - {name}]]"


def project_slug(name: str) -> str:
    """Generate a URL-safe slug from a project name."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", " ", slug)
    slug = re.sub(r"[\s-]+", "-", slug)
    return slug.strip("-")


def find_project_name(project_dir: Path) -> str | None:
    """Find the project name by looking for Project - *.md in the root."""
    for f in project_dir.glob("Project - *.md"):
        parsed = parse_filename(f.name)
        if parsed and parsed[0] == "project":
            return parsed[1]
    return None


def project_tag(project_name: str) -> str:
    """Convert project name to an Obsidian tag: project/{slug}."""
    return f"project/{project_slug(project_name)}"
