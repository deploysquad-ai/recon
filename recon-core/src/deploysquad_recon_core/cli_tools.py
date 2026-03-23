"""CLI subcommands for recon-core.

Each function is one subcommand. All output JSON to stdout.
Exit code 0 = success, 1 = error (error JSON on stdout).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def _ok(data: dict | list) -> None:
    print(json.dumps(data, default=str))


def _err(message: str) -> None:
    print(json.dumps({"error": message}))
    sys.exit(1)


def cmd_list_nodes(args) -> None:
    from deploysquad_recon_core import list_nodes
    try:
        nodes = list_nodes(
            args.project_dir,
            node_type=args.type,
            status=args.status,
        )
        _ok([{
            "type": n["type"],
            "name": n["name"],
            "status": n["status"],
            "file_path": str(n["file_path"]),
        } for n in nodes])
    except Exception as e:
        _err(str(e))


def cmd_get_node(args) -> None:
    from deploysquad_recon_core import get_node
    try:
        result = get_node(args.file)
        _ok({
            "frontmatter": result["frontmatter"],
            "body": result["body"],
            "file_path": str(args.file),
        })
    except Exception as e:
        _err(str(e))


def cmd_create_node(args) -> None:
    from deploysquad_recon_core import create_node
    try:
        data = json.loads(args.data)
        body_sections = json.loads(args.body_sections) if args.body_sections else None
        path = create_node(args.type, data, args.project_dir, body_sections)
        _ok({"file_path": str(path), "status": "created"})
    except Exception as e:
        _err(str(e))


def cmd_update_node(args) -> None:
    from deploysquad_recon_core import update_node
    try:
        updates = json.loads(args.data)
        body_sections = json.loads(args.body_sections) if args.body_sections else None
        path = update_node(args.file, updates, body_sections)
        _ok({"file_path": str(path), "status": "updated"})
    except Exception as e:
        _err(str(e))


def cmd_resolve_links(args) -> None:
    from deploysquad_recon_core import resolve_links
    try:
        result = resolve_links(args.project_dir)
        _ok({
            "valid_count": len(result["valid"]),
            "broken_count": len(result["broken"]),
            "broken": [str(b) for b in result["broken"]],
        })
    except Exception as e:
        _err(str(e))


def cmd_build_index(args) -> None:
    from deploysquad_recon_core import build_index
    from deploysquad_recon_core.index import write_index
    try:
        index = build_index(args.project_dir)
        write_index(index, Path(args.project_dir))
        _ok({"node_count": len(index.get("nodes", {})), "status": "built"})
    except Exception as e:
        _err(str(e))


def cmd_generate_context(args) -> None:
    from deploysquad_recon_core import generate_context
    try:
        content = generate_context(args.feature, args.project_dir)
        _ok({"content": content, "feature": args.feature})
    except Exception as e:
        _err(str(e))


def cmd_embed_nodes(args) -> None:
    from deploysquad_recon_core import embed_nodes
    try:
        result = embed_nodes(args.project_dir, api_key=args.api_key)
        _ok(result if isinstance(result, dict) else {"status": "embedded"})
    except Exception as e:
        _err(str(e))


def cmd_find_similar(args) -> None:
    from deploysquad_recon_core import find_similar
    try:
        results = find_similar(
            Path(args.node),
            args.project_dir,
            top_k=args.top_k,
            threshold=args.threshold,
        )
        _ok([{"path": str(p), "score": score} for p, score in results])
    except Exception as e:
        _err(str(e))


def build_parser():
    import argparse
    parser = argparse.ArgumentParser(
        prog="deploysquad_recon_core",
        description="recon-core CLI — graph authoring tools",
    )
    sub = parser.add_subparsers(dest="command")

    # list_nodes
    p = sub.add_parser("list_nodes", help="List nodes in a project")
    p.add_argument("--project-dir", required=True)
    p.add_argument("--type", default=None)
    p.add_argument("--status", default=None)

    # get_node
    p = sub.add_parser("get_node", help="Read a node file")
    p.add_argument("--file", required=True, type=Path)

    # create_node
    p = sub.add_parser("create_node", help="Create a new node")
    p.add_argument("--type", required=True)
    p.add_argument("--project-dir", required=True)
    p.add_argument("--data", required=True, help="JSON dict of frontmatter fields")
    p.add_argument("--body-sections", default=None, help='JSON dict e.g. \'{"## Description": "..."}\'')

    # update_node
    p = sub.add_parser("update_node", help="Update an existing node")
    p.add_argument("--file", required=True, type=Path)
    p.add_argument("--data", required=True, help="JSON dict of fields to update")
    p.add_argument("--body-sections", default=None)

    # resolve_links
    p = sub.add_parser("resolve_links", help="Check all wikilinks")
    p.add_argument("--project-dir", required=True)

    # build_index
    p = sub.add_parser("build_index", help="Rebuild .graph/index.json")
    p.add_argument("--project-dir", required=True)

    # generate_context
    p = sub.add_parser("generate_context", help="Generate CONTEXT.md for a feature")
    p.add_argument("--feature", required=True, help="Feature name (not filename)")
    p.add_argument("--project-dir", required=True)

    # embed_nodes
    p = sub.add_parser("embed_nodes", help="Embed all nodes for semantic search")
    p.add_argument("--project-dir", required=True)
    p.add_argument("--api-key", default=None)

    # find_similar
    p = sub.add_parser("find_similar", help="Find semantically similar nodes")
    p.add_argument("--node", required=True, help="Vault-relative path to node file")
    p.add_argument("--project-dir", required=True)
    p.add_argument("--top-k", type=int, default=5)
    p.add_argument("--threshold", type=float, default=0.75)

    return parser
