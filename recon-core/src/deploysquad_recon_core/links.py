"""Wikilink parsing, resolution, and broken-link detection."""
from __future__ import annotations

import re
from pathlib import Path
from dataclasses import dataclass

from .vault.paths import parse_filename, node_filepath

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def parse_wikilink(link: str) -> tuple[str, str] | None:
    """Parse '[[Type - Name]]' -> (type_string, name), or None if invalid.

    Uses parse_filename internally since the inner text follows the same
    'Type - Name' convention as filenames (without .md).
    """
    match = WIKILINK_RE.fullmatch(link)
    if not match:
        return None
    inner = match.group(1)
    # parse_filename expects .md extension
    return parse_filename(inner + ".md")


def extract_wikilinks(data: dict | list | str) -> list[str]:
    """Extract all wikilink strings from a nested dict/list/str structure.

    Recursively walks the data and collects any string matching [[...]].
    """
    links: list[str] = []
    if isinstance(data, str):
        return [f"[[{m}]]" for m in WIKILINK_RE.findall(data)]
    elif isinstance(data, list):
        for item in data:
            links.extend(extract_wikilinks(item))
    elif isinstance(data, dict):
        for value in data.values():
            links.extend(extract_wikilinks(value))
    return links


def resolve_link(wikilink: str, project_dir: Path) -> Path | None:
    """Check if a wikilink target exists in the vault.

    Returns the file path if it exists, None otherwise.
    """
    parsed = parse_wikilink(wikilink)
    if parsed is None:
        return None
    node_type, name = parsed
    path = node_filepath(node_type, name, project_dir)
    return path if path.exists() else None


@dataclass
class LinkResult:
    """Result of resolving a single wikilink."""
    source_path: Path
    wikilink: str
    target_path: Path | None  # None if broken


def resolve_all_links(project_dir: Path) -> dict[str, list[LinkResult]]:
    """Scan all .md files in project_dir, resolve every wikilink.

    Returns:
        {"valid": [...], "broken": [...]} where each entry is a LinkResult
    """
    import frontmatter

    valid: list[LinkResult] = []
    broken: list[LinkResult] = []

    for md_file in sorted(project_dir.rglob("*.md")):
        # Skip .graph directory
        if ".graph" in md_file.parts:
            continue

        post = frontmatter.load(str(md_file))
        fm = dict(post.metadata)

        # Extract wikilinks from frontmatter only (body links are informational, not structural)
        wikilinks = extract_wikilinks(fm)

        for link in wikilinks:
            target = resolve_link(link, project_dir)
            result = LinkResult(source_path=md_file, wikilink=link, target_path=target)
            if target is not None:
                valid.append(result)
            else:
                broken.append(result)

    return {"valid": valid, "broken": broken}
