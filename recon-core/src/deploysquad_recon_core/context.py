"""Generate CONTEXT.md by traversing the graph from a Feature node."""
from __future__ import annotations

from pathlib import Path

from .vault.reader import read_node
from .vault.paths import node_filepath, parse_filename, get_type_display_name
from .links import parse_wikilink
from .errors import NodeNotFoundError


def generate_context(feature_name: str, project_dir: Path) -> str:
    """Generate a CONTEXT.md string for a Feature node.

    Traversal:
    1. Find Feature file by name
    2. Feature -> belongs_to -> Module -> belongs_to -> Project
    3. Feature -> target_version -> Version
    4. Feature -> implements -> User Stories (with Acceptance Criteria + Story body sections)
    5. Feature + Module governed_by -> Constraints (deduplicated)
    6. Feature + Module governed_by -> Decisions (deduplicated, from Module's belongs_to context)
    7. Feature + User Stories supports -> Goals (deduplicated)
    8. Feature -> depends_on -> Dependencies
    9. Feature -> related_to -> Related features

    Args:
        feature_name: The name of the Feature (e.g. "JWT Login")
        project_dir: Root directory of the project vault

    Returns:
        Formatted CONTEXT.md string

    Raises:
        NodeNotFoundError: Feature not found
    """
    project_dir = Path(project_dir)

    # 1. Read the Feature
    feature_path = node_filepath("feature", feature_name, project_dir)
    if not feature_path.exists():
        raise NodeNotFoundError(f"Feature not found: {feature_name}")
    feature = read_node(feature_path)
    feature_model = feature["model"]

    # 2. Traverse to Module and Project
    module = _follow_link(feature_model.belongs_to, project_dir)
    module_model = module["model"] if module else None

    project = None
    if module_model and hasattr(module_model, "belongs_to"):
        project = _follow_link(module_model.belongs_to, project_dir)

    # 3. Version
    version = None
    if feature_model.target_version:
        version = _follow_link(feature_model.target_version, project_dir)

    # 4. User Stories
    user_stories = []
    for us_link in feature_model.implements:
        us = _follow_link(us_link, project_dir)
        if us:
            user_stories.append(us)

    # 5. Constraints (from Feature + Module governed_by, deduplicated)
    constraint_links = set()
    for link in feature_model.governed_by:
        parsed = parse_wikilink(link)
        if parsed and parsed[0] == "constraint":
            constraint_links.add(link)
    if module_model and hasattr(module_model, "governed_by"):
        for link in module_model.governed_by:
            parsed = parse_wikilink(link)
            if parsed and parsed[0] == "constraint":
                constraint_links.add(link)

    constraints = []
    for link in sorted(constraint_links):
        c = _follow_link(link, project_dir)
        if c:
            constraints.append(c)

    # 6. Decisions (from Feature + Module context)
    decision_links = set()
    for link in feature_model.governed_by:
        parsed = parse_wikilink(link)
        if parsed and parsed[0] == "decision":
            decision_links.add(link)
    if module_model and hasattr(module_model, "governed_by"):
        for link in module_model.governed_by:
            parsed = parse_wikilink(link)
            if parsed and parsed[0] == "decision":
                decision_links.add(link)
    # Also scan for decisions that belong_to this module
    _scan_decisions_for_module(module_model, project_dir, decision_links)

    decisions = []
    for link in sorted(decision_links):
        d = _follow_link(link, project_dir)
        if d:
            decisions.append(d)

    # 7. Goals (from Feature supports + User Story supports, deduplicated)
    goal_links = set()
    for link in feature_model.supports:
        goal_links.add(link)
    for us in user_stories:
        if hasattr(us["model"], "supports"):
            for link in us["model"].supports:
                goal_links.add(link)

    goals = []
    for link in sorted(goal_links):
        g = _follow_link(link, project_dir)
        if g:
            goals.append(g)

    # 8. Dependencies
    dependencies = []
    for link in feature_model.depends_on:
        dep = _follow_link(link, project_dir)
        if dep:
            dependencies.append(dep)

    # 9. Related features
    related = []
    for link in feature_model.related_to:
        rel = _follow_link(link, project_dir)
        if rel:
            related.append(rel)

    # Render
    return _render_context(
        feature=feature,
        project=project,
        module=module,
        version=version,
        goals=goals,
        user_stories=user_stories,
        constraints=constraints,
        decisions=decisions,
        dependencies=dependencies,
        related=related,
    )


def _follow_link(wikilink: str, project_dir: Path) -> dict | None:
    """Follow a wikilink and read the target node. Returns None if not found."""
    parsed = parse_wikilink(wikilink)
    if not parsed:
        return None
    node_type, name = parsed
    path = node_filepath(node_type, name, project_dir)
    if not path.exists():
        return None
    return read_node(path)


def _scan_decisions_for_module(module_model, project_dir: Path, decision_links: set) -> None:
    """Find Decision nodes whose belongs_to references this module."""
    if not module_model:
        return
    decisions_dir = project_dir / "decisions"
    if not decisions_dir.exists():
        return
    module_link = f"[[Module - {module_model.name}]]"
    for md_file in decisions_dir.glob("*.md"):
        parsed = parse_filename(md_file.name)
        if not parsed or parsed[0] != "decision":
            continue
        try:
            result = read_node(md_file)
        except Exception:
            continue
        if result["model"].belongs_to == module_link:
            decision_links.add(f"[[Decision - {result['model'].name}]]")


def _render_context(
    feature: dict,
    project: dict | None,
    module: dict | None,
    version: dict | None,
    goals: list[dict],
    user_stories: list[dict],
    constraints: list[dict],
    decisions: list[dict],
    dependencies: list[dict],
    related: list[dict],
) -> str:
    """Render the CONTEXT.md output."""
    lines: list[str] = []

    # Header comment
    lines.append("<!-- context_bundle_version: 1 -->")
    lines.append("")

    # Title
    lines.append(f"# Context Bundle: {feature['model'].name}")
    lines.append("")

    # Project section
    if project:
        lines.append("## Project")
        lines.append("")
        lines.append(f"**{project['model'].name}** — {project['model'].description}")
        lines.append("")

    # Goals section
    if goals:
        lines.append("## Goals")
        lines.append("")
        for g in goals:
            lines.append(f"### {g['model'].name}")
            lines.append("")
            desc = g["body_sections"].get("Description", "")
            if desc:
                lines.append(desc)
                lines.append("")
            criteria = g["body_sections"].get("Success Criteria", "")
            if criteria:
                lines.append("**Success Criteria:**")
                lines.append("")
                lines.append(criteria)
                lines.append("")

    # Version section
    if version:
        lines.append("## Version")
        lines.append("")
        v = version["model"]
        line = f"**{v.name}** (sequence: {v.sequence})"
        if v.target_date:
            line += f" — target: {v.target_date}"
        lines.append(line)
        lines.append("")

    # Module section
    if module:
        lines.append("## Module")
        lines.append("")
        lines.append(f"**{module['model'].name}**")
        lines.append("")
        desc = module["body_sections"].get("Description", "")
        if desc:
            lines.append(desc)
            lines.append("")
        if hasattr(module["model"], "governed_by") and module["model"].governed_by:
            gov = ", ".join(module["model"].governed_by)
            lines.append(f"Governed by: {gov}")
            lines.append("")

    # User Stories section
    if user_stories:
        lines.append("## User Stories")
        lines.append("")
        for us in user_stories:
            lines.append(f"### {us['model'].name}")
            lines.append("")
            story = us["body_sections"].get("Story", "")
            if story:
                lines.append(story)
                lines.append("")
            ac_section = us["body_sections"].get("Acceptance Criteria", "")
            if ac_section:
                lines.append("**Acceptance Criteria:**")
                lines.append("")
                lines.append(ac_section)
                lines.append("")

    # Constraints section
    if constraints:
        lines.append("## Constraints")
        lines.append("")
        for c in constraints:
            lines.append(f"### {c['model'].name}")
            lines.append("")
            desc = c["body_sections"].get("Description", "")
            if desc:
                lines.append(desc)
                lines.append("")
            scope = c["body_sections"].get("Scope", "")
            if scope:
                lines.append(f"**Scope:** {scope}")
                lines.append("")

    # Decisions section
    if decisions:
        lines.append("## Decisions")
        lines.append("")
        for d in decisions:
            lines.append(f"### {d['model'].name}")
            lines.append("")
            decision_text = d["body_sections"].get("Decision", "")
            if decision_text:
                lines.append(decision_text)
                lines.append("")
            rationale = d["body_sections"].get("Rationale", "")
            if rationale:
                lines.append(f"**Rationale:** {rationale}")
                lines.append("")

    # Dependencies section
    if dependencies:
        lines.append("## Dependencies")
        lines.append("")
        for dep in dependencies:
            status = dep["model"].status
            if hasattr(status, "value"):
                status = status.value
            lines.append(f"- **{dep['model'].name}** (status: {status})")
        lines.append("")

    # Related section
    if related:
        lines.append("## Related")
        lines.append("")
        for rel in related:
            lines.append(f"- [[{get_type_display_name(rel['model'].type)} - {rel['model'].name}]]")
        lines.append("")

    return "\n".join(lines)


def write_context(
    context: str,
    output_path: str,
    project_dir: Path,
    feature_name: str | None = None,
) -> Path:
    """Write a context string to disk.

    Args:
        context: The rendered CONTEXT.md string
        output_path: Vault-relative path, or "auto" to use features/CONTEXT - {name}.md
        project_dir: Root directory of the project vault
        feature_name: Required when output_path is "auto"

    Returns:
        Vault-relative Path where the file was written
    """
    if output_path == "auto":
        if not feature_name:
            raise ValueError("feature_name is required when output_path is 'auto'")
        rel = Path("features") / f"CONTEXT - {feature_name}.md"
    else:
        rel = Path(output_path)

    full = project_dir / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(context)
    return rel
