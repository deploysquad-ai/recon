"""Read .md vault files, parse frontmatter + body, validate against models."""
from __future__ import annotations

from pathlib import Path

import frontmatter

from ..errors import NodeNotFoundError, ValidationError
from ..models import get_model_for_type


def read_node(file_path: Path) -> dict:
    """Read a node .md file, parse frontmatter, validate, return structured data.

    Returns dict with keys:
        - frontmatter: raw dict from YAML
        - body: raw markdown string
        - body_sections: dict of {heading: content}
        - model: validated Pydantic model instance
        - file_path: the Path that was read

    Raises:
        NodeNotFoundError: file does not exist
        ValidationError: frontmatter fails model validation
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise NodeNotFoundError(f"Node file not found: {file_path}")

    post = frontmatter.load(str(file_path))
    fm = dict(post.metadata)

    node_type = fm.get("type")
    if not node_type:
        raise ValidationError(f"Missing 'type' field in frontmatter: {file_path}")

    try:
        model_cls = get_model_for_type(node_type)
    except KeyError:
        raise ValidationError(f"Unknown node type '{node_type}' in {file_path}")

    try:
        model = model_cls(**fm)
    except Exception as e:
        raise ValidationError(f"Validation failed for {file_path}: {e}") from e

    body_sections = parse_body_sections(post.content)

    return {
        "frontmatter": fm,
        "body": post.content,
        "body_sections": body_sections,
        "model": model,
        "file_path": file_path,
    }


def parse_body_sections(body: str) -> dict[str, str]:
    """Split body on ## headings into {heading: content} dict.

    Example:
        '## Description\\nFoo bar\\n\\n## Scope\\nBaz'
        -> {'Description': 'Foo bar', 'Scope': 'Baz'}
    """
    sections: dict[str, str] = {}
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in body.split("\n"):
        if line.startswith("## "):
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_heading is not None:
        sections[current_heading] = "\n".join(current_lines).strip()

    return sections
