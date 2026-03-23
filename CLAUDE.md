# CLAUDE.md — recon

## What This Project Is

An open-source CLI tool that lets users build a structured project graph in an Obsidian vault through interactive LLM-driven conversation. The LLM (Claude) authors and links graph nodes by calling structured tool functions — it never writes files directly.

## Open Source — Fresh Install Must Work

This project is open source. Every change must work for a user doing a **completely fresh install** on a new machine. Before merging any change that touches the MCP server, plugin, or skills:

1. **PyPI package must be published** — The MCP server runs via `uvx deploysquad-recon-core`. Any changes to `mcp_server.py` or any Python code require a version bump + PyPI publish, or fresh users get the old version.
2. **No restart required for setup** — The `configure_vault_tool()` MCP tool sets the vault path in-memory. Skills must use this for first-time setup instead of requiring a Claude Code restart.
3. **`.mcp.json` must not ship env defaults** — Empty `VAULT_PATH=""` in `.mcp.json` overrides user settings on restart. The plugin `.mcp.json` should only contain `command` and `args`.
4. **Skills must handle unconfigured state inline** — If vault isn't configured, ask for the path and call `configure_vault_tool()` in the same session. Never bounce to a separate command and stop.
5. **Don't re-ask for already-configured values** — Check existing settings before prompting (e.g., don't ask for Gemini API key if already set).

### Release Checklist

```bash
cd recon-core
# 1. Bump version in pyproject.toml
# 2. Run tests
.venv/bin/python -m pytest -v           # Must pass (290+ tests)
# 3. Build
.venv/bin/python -m build
# 4. Publish (PYPI_TOKEN in ~/.zsh/secrets.zsh)
source ~/.zsh/secrets.zsh
.venv/bin/python -m twine upload dist/* -u __token__ -p "$PYPI_TOKEN"
# 5. Sync lockfile
cd .. && uv lock
# 6. Commit version bump + lockfile
```

## Project Structure

```
recon/
  recon-core/          # Python library — the engine (parse, write, validate, index, context)
  recon-author/        # Agent instruction files loaded as LLM context during sessions
    AGENT.md           # Always-loaded orchestration (tool contract, authoring order)
    schemas/           # One prompt file per node type (fallback guidance, not validation)
    linking-pass.md    # Heuristic linking rules
    context-bundle.md  # CONTEXT.md generation reference
  plugin/recon-plugin/ # Installable Claude Code plugin + skill files
  docs/
    architecture/      # Foundational specs (schema design, brainstorm decisions)
    feedback/          # Historical reviews (staff-engineer, product)
    plan.md            # Project roadmap and tasklist
    agent-scaffold-plan.md  # Implementation plan for agent files + dog-food
```

## Architecture (4 layers)

1. **recon-core** (Python): Pydantic v2 models for 10 node types, vault I/O, wikilink resolution, graph index, context bundle generation. This is the validation + write layer.
2. **recon-author** (Markdown): Agent instruction files — source of truth for skill content. Tells the LLM how to converse with users and call recon-core tools.
3. **MCP Server** (`deploysquad_recon_core/mcp_server.py`): Thin wrapper exposing 10 recon-core API functions as MCP tools callable by Claude.
4. **Skill** (`plugin/recon-plugin/skills/recon/SKILL.md`): Claude Code skill invoked as `/recon`. Inlines recon-author content and wires the MCP server.

## Key Design Decisions

- **Markdown is source of truth**: `.md` files with YAML frontmatter in an Obsidian vault. No external database.
- **LLM as conversational UI, not database engine** (Decision 10): The LLM calls `create_node(type, data)` — recon-core validates and writes.
- **LLM infers the graph** (Decision 11): User describes naturally, LLM drafts nodes in bulk, user reviews. NOT a sequential interview.
- **Heuristic linking for MVP** (Decision 9): Uses shared personas, name mentions, module co-membership. Gemini-based semantic linking is also supported optionally (when GEMINI_API_KEY is configured).
- **Two-phase authoring**: Phase 1 authors nodes, Phase 2 resolves links.
- **Context builder is the MVP gate** (Decision 12): If `generate_context("Feature - X")` produces a correct CONTEXT.md, the data model works.

## 10 Node Types (authoring order)

Project → Goals → Personas → Constraints → Modules → Decisions → User Stories → Epics → Features → Versions → version assignment → linking pass

## Working with recon-core

```bash
cd recon-core
.venv/bin/python -m pytest -v    # Run tests (290+ tests, use venv Python not system)
```

**Important:** The `.venv` uses Python 3.12. Do NOT use `uv run pytest` from the repo root — it picks up the system Python which doesn't have the package installed.

Public API: `create_node`, `get_node`, `list_nodes`, `update_node`, `resolve_links`, `build_index`, `generate_context` — all importable from `deploysquad_recon_core`.

See `recon-core/CLAUDE.md` for detailed development guidance.

## Commit Conventions

- `feat:` for new functionality
- `docs:` for documentation changes
- `chore:` for tooling/config
- `fix:` for bug fixes
- Always include `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>` when Claude commits

## Git Workflow

- Use `.worktrees/` for feature branches (already in .gitignore)
- Branch naming: `feature/<phase>-<description>` (e.g. `feature/phase-b-recon-core`)
- Merge to master via fast-forward when clean

## Project Status

- Phase A: Schema fixes — DONE
- Phase B: recon-core library — DONE (290+ tests)
- Phase C: Agent instruction files — DONE
- Phase D: Skill + MCP server — DONE
