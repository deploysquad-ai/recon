"""MCP server exposing recon-core tools for Claude Code integration."""
from __future__ import annotations

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

import deploysquad_recon_core

mcp = FastMCP("recon")

# Captured at startup from environment; mutable via configure_vault_tool.
PROJECT_DIR: Path = Path(os.environ.get("VAULT_PATH", "") or ".")


def _get_project_dir() -> Path:
    """Return the current PROJECT_DIR (module-level, updated by configure_vault_tool)."""
    return PROJECT_DIR


def _relative_path(absolute: Path) -> str:
    """Convert absolute path to vault-relative string."""
    try:
        return str(absolute.relative_to(_get_project_dir()))
    except ValueError:
        return str(absolute)


def _serialize_error(e: Exception) -> str:
    """Serialize an exception as JSON error response."""
    return json.dumps({"error": type(e).__name__, "message": str(e)})


@mcp.tool()
def get_vault_status_tool() -> str:
    """Check whether the vault is configured. Returns vault_path and is_configured flag.

    is_configured is True when VAULT_PATH is set to a real existing directory
    (i.e. not the default '.').
    """
    pd = _get_project_dir()
    is_configured = pd != Path(".") and pd.exists()
    return json.dumps({
        "vault_path": str(pd),
        "is_configured": is_configured,
    })


@mcp.tool()
def configure_vault_tool(vault_path: str) -> str:
    """Set the vault path for this session. Every recon-touching skill calls this in its preflight.

    Args:
        vault_path: Absolute path to the Obsidian vault directory (typically the project root).

    Updates the in-memory PROJECT_DIR so all subsequent tool calls use the new path.
    Do NOT persist this to settings.json — every skill's preflight calls configure_vault_tool
    afresh. Persisting would race between concurrent Claude Code sessions on different repos.
    See project-local-vault-spec.md §4 for rationale.
    """
    global PROJECT_DIR
    expanded = Path(os.path.expanduser(vault_path)).resolve()
    if not expanded.is_dir():
        return json.dumps({
            "error": "DirectoryNotFound",
            "message": f"Path does not exist or is not a directory: {expanded}",
        })
    PROJECT_DIR = expanded
    return json.dumps({
        "vault_path": str(PROJECT_DIR),
        "is_configured": True,
    })


_VALID_NODE_TYPES = {
    "project", "goal", "persona", "constraint", "module",
    "decision", "user-story", "epic", "feature", "version",
}


@mcp.tool()
def get_authoring_guide_tool(node_type: str) -> str:
    """Return the detailed authoring guide for a node type.

    Call this before authoring a node of a given type for the first time in a
    session — it returns the full schema, body section guidance, writing tips,
    and fallback question prompts the LLM should follow. Cache the result for
    subsequent nodes of the same type in the same session.

    Args:
        node_type: One of: project, goal, persona, constraint, module,
                   decision, user-story, epic, feature, version.
    """
    if node_type not in _VALID_NODE_TYPES:
        return _serialize_error(ValueError(
            f"Unknown node_type: {node_type!r}. Valid types: {sorted(_VALID_NODE_TYPES)}"
        ))
    try:
        from importlib.resources import files
        guide_path = files("deploysquad_recon_core") / "authoring_guides" / f"{node_type}.md"
        content = guide_path.read_text(encoding="utf-8")
        return json.dumps({"node_type": node_type, "guide": content})
    except Exception as e:
        return _serialize_error(e)


@mcp.tool()
def create_node_tool(
    node_type: str,
    data: dict,
    body_sections: dict[str, str] | None = None,
) -> str:
    """Create a new node in the vault. Validates via Pydantic, writes atomically.

    Args:
        node_type: One of: project, goal, persona, constraint, module, decision, user-story, epic, feature, version
        data: Dict of frontmatter fields (type and schema_version auto-filled)
        body_sections: Optional dict of {"Heading": "content"} for the markdown body (writer prepends ## automatically)
    """
    try:
        result_path = deploysquad_recon_core.create_node(node_type, data, _get_project_dir(), body_sections)
        return json.dumps({"file_path": _relative_path(result_path)})
    except Exception as e:
        return _serialize_error(e)


@mcp.tool()
def get_node_tool(file_path: str) -> str:
    """Read and validate an existing node.

    Args:
        file_path: Vault-relative path (e.g. "features/Feature - Login.md")

    Returns node data with frontmatter, body, body_sections.
    """
    try:
        absolute = _get_project_dir() / file_path
        result = deploysquad_recon_core.get_node(absolute)
        return json.dumps({
            "frontmatter": result["frontmatter"],
            "body": result["body"],
            "body_sections": result["body_sections"],
            "file_path": _relative_path(result["file_path"]),
        })
    except Exception as e:
        return _serialize_error(e)


@mcp.tool()
def list_nodes_tool(
    node_type: str | None = None,
    status: str | None = None,
) -> str:
    """List nodes in the vault, optionally filtered by type and/or status.

    Args:
        node_type: Filter by type (e.g. "feature", "user-story"). None for all.
        status: Filter by status (e.g. "draft", "active"). None for all.
    """
    try:
        results = deploysquad_recon_core.list_nodes(_get_project_dir(), node_type, status)
        serialized = [
            {
                "type": r["type"],
                "name": r["name"],
                "status": r["status"],
                "file_path": _relative_path(r["file_path"]),
            }
            for r in results
        ]
        return json.dumps(serialized)
    except Exception as e:
        return _serialize_error(e)


@mcp.tool()
def update_node_tool(
    file_path: str,
    updates: dict,
    body_sections: dict[str, str] | None = None,
) -> str:
    """Update an existing node's frontmatter and/or body.

    Args:
        file_path: Vault-relative path (e.g. "features/Feature - Login.md")
        updates: Dict of fields to merge into existing frontmatter
        body_sections: If provided, replaces body sections entirely
    """
    try:
        absolute = _get_project_dir() / file_path
        result_path = deploysquad_recon_core.update_node(absolute, updates, body_sections)
        return json.dumps({"file_path": _relative_path(result_path)})
    except Exception as e:
        return _serialize_error(e)


@mcp.tool()
def resolve_links_tool() -> str:
    """Check all wikilinks in the vault. Returns valid and broken links."""
    try:
        result = deploysquad_recon_core.resolve_links(_get_project_dir())
        serialized = {
            "valid": [
                {"source_path": _relative_path(lr.source_path), "wikilink": lr.wikilink,
                 "target_path": _relative_path(lr.target_path) if lr.target_path else None}
                for lr in result["valid"]
            ],
            "broken": [
                {"source_path": _relative_path(lr.source_path), "wikilink": lr.wikilink,
                 "target_path": None}
                for lr in result["broken"]
            ],
        }
        return json.dumps(serialized)
    except Exception as e:
        return _serialize_error(e)


@mcp.tool()
def build_index_tool() -> str:
    """Build the graph index from vault files. Returns the index structure (nodes + edges)."""
    try:
        result = deploysquad_recon_core.build_index(_get_project_dir())
        # Index values contain Path objects in node entries — convert to strings
        serialized = json.loads(json.dumps(result, default=str))
        return json.dumps(serialized)
    except Exception as e:
        return _serialize_error(e)


@mcp.tool()
def generate_context_tool(feature_name: str, output_path: str | None = None) -> str:
    """Generate a CONTEXT.md string for a Feature node by traversing its graph relationships.

    Args:
        feature_name: The name field of the Feature (e.g. "JWT Login"), not the filename.
        output_path: Where to write the file. None = return string only (backward compatible).
                     "auto" = write to features/CONTEXT - {feature_name}.md.
                     Any other string = vault-relative path to write to.
    """
    try:
        result = deploysquad_recon_core.generate_context(feature_name, _get_project_dir())
        response = {"context": result}
        if output_path is not None:
            from deploysquad_recon_core.context import write_context
            rel = write_context(result, output_path, _get_project_dir(), feature_name=feature_name)
            response["output_path"] = str(rel)
        return json.dumps(response)
    except Exception as e:
        return _serialize_error(e)


@mcp.tool()
def embed_nodes_tool() -> str:
    """Embed all nodes in the vault using Gemini text-embedding-004.
    Requires GEMINI_API_KEY environment variable.
    """
    from deploysquad_recon_core.embeddings import embed_nodes
    try:
        result = embed_nodes(_get_project_dir())
        return json.dumps(result)
    except Exception as e:
        return _serialize_error(e)


@mcp.tool()
def find_similar_tool(
    node_path: str,
    top_k: int = 5,
    threshold: float = 0.75,
) -> str:
    """Find semantically similar nodes using cached Gemini embeddings.
    Run embed_nodes_tool first to populate the cache.
    Args:
        node_path: Vault-relative path (e.g. "features/Feature - Login.md")
        top_k: Maximum results to return (default 5)
        threshold: Minimum cosine similarity (default 0.75)
    """
    from deploysquad_recon_core.embeddings import find_similar
    try:
        pd = _get_project_dir()
        abs_node_path = pd / node_path
        results = find_similar(abs_node_path, pd, top_k=top_k, threshold=threshold)
        serialized = [
            {"path": str(abs_path.relative_to(pd)), "score": round(score, 4)}
            for abs_path, score in results
        ]
        return json.dumps({"results": serialized})
    except Exception as e:
        return _serialize_error(e)


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
