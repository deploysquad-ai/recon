"""Entry point for `uvx deploysquad-recon-core [subcommand]`.

No args → start MCP server (Claude Code)
*        → CLI subcommand
"""
import sys


def main() -> None:
    if len(sys.argv) < 2:
        # No subcommand — start MCP server
        from .mcp_server import main as mcp_main
        mcp_main()
        return

    command = sys.argv[1]

    # All subcommands go through cli_tools
    from .cli_tools import build_parser
    handlers = {
        "list_nodes":       "cmd_list_nodes",
        "get_node":         "cmd_get_node",
        "create_node":      "cmd_create_node",
        "update_node":      "cmd_update_node",
        "resolve_links":    "cmd_resolve_links",
        "build_index":      "cmd_build_index",
        "generate_context": "cmd_generate_context",
        "embed_nodes":      "cmd_embed_nodes",
        "find_similar":     "cmd_find_similar",
    }

    if command not in handlers:
        print(f"Unknown command: {command}", file=sys.stderr)
        print(f"Available: {', '.join(handlers)}", file=sys.stderr)
        sys.exit(1)

    from . import cli_tools
    parser = build_parser()
    args = parser.parse_args()
    getattr(cli_tools, handlers[command])(args)


if __name__ == "__main__":
    main()
