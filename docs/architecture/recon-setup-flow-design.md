# recon Setup Flow Design

**Date:** 2026-03-27
**Status:** Approved

## Problem

The current install experience requires two manual steps:
1. `uvx deploysquad-recon-core install` — prompts for vault path, writes MCP config, copies skills
2. Restart Claude Code and run `/recon`

The goal is to reduce installation to a single `/plugin install recon@deploysquad` command, with vault path configuration handled inline via a `/recon.setup` skill. If a user runs `/recon` without completing setup, they are informed and redirected.

## Scope

- Add `.mcp.json` to the plugin bundle (wires MCP server on install)
- Add `get_vault_status_tool` to `mcp_server.py` (lightweight config check)
- Prepend a setup guard to the `/recon` skill
- Create a new `/recon.setup` skill (full vault path configuration flow)
- Mirror skill files to `skill/` (legacy path used by `uvx install`)

Out of scope: changes to `uvx deploysquad-recon-core install` behavior, embeddings, or authoring logic.

## Components

| Component | Change |
|---|---|
| `plugin/recon-plugin/.mcp.json` | New — registers MCP server on `/plugin install` |
| `recon-core/src/deploysquad_recon_core/mcp_server.py` | Add `get_vault_status_tool` |
| `plugin/recon-plugin/skills/recon/SKILL.md` | Prepend setup guard block |
| `plugin/recon-plugin/skills/recon-setup/SKILL.md` | New skill |
| `skill/recon.md` | Mirror: prepend setup guard |
| `skill/recon.setup.md` | New — mirror of plugin skill |

## Flows

### Install (new path)
```
/plugin install recon@deploysquad
  → .mcp.json registers MCP server with VAULT_PATH: ""
  → skills/ registers /recon and /recon.setup
  → user restarts Claude Code
```

### First-time /recon (not configured)
```
/recon
  → skill calls get_vault_status_tool()
  → {is_configured: false}
  → skill: "recon isn't set up yet. Run /recon.setup to connect
    your Obsidian vault — it takes 30 seconds."
  → stops, does not enter authoring session
```

### /recon.setup
```
/recon.setup
  → asks: "What's the path to your Obsidian vault?"
  → user provides path
  → Claude verifies path exists (bash: test -d <path>)
  → Claude runs python3 patch to write VAULT_PATH into
    ~/.claude/settings.json under mcpServers.recon.env
  → user approves the Bash command in Claude Code's permission prompt
  → skill confirms: "Done. Restart Claude Code, then run /recon."
```

### Subsequent /recon (configured)
```
/recon
  → get_vault_status_tool() → {is_configured: true}
  → proceeds normally into authoring session
```

## Technical Details

### .mcp.json
```json
{
  "mcpServers": {
    "recon": {
      "command": "uvx",
      "args": ["deploysquad-recon-core"],
      "env": { "VAULT_PATH": "" }
    }
  }
}
```

### get_vault_status_tool
Added to `mcp_server.py`. Reads module-level `PROJECT_DIR`.

- `is_configured = PROJECT_DIR != Path(".") and PROJECT_DIR.exists()`
- Returns `{"vault_path": str(PROJECT_DIR), "is_configured": bool}`
- No side effects. Used only for detection.

### /recon skill guard
Prepended as the first section in the skill, before the Role section:

```
## Setup Check (run first)
Before anything else, call get_vault_status_tool().
If is_configured is false: inform the user that recon needs
setup, point them to /recon.setup, and stop. Do not proceed
into the authoring session.
```

### /recon.setup skill behavior
Claude is instructed to:
1. Ask the user for their Obsidian vault path
2. Expand `~` to absolute path if needed
3. Verify the directory exists: `test -d <path>`
4. Run the settings patch:
```python
python3 -c "
import json, pathlib
p = pathlib.Path.home() / '.claude/settings.json'
d = json.loads(p.read_text())
d.setdefault('mcpServers', {}).setdefault('recon', {}).setdefault('env', {})['VAULT_PATH'] = '<path>'
p.write_text(json.dumps(d, indent=2))
"
```
5. Confirm success and tell user to restart Claude Code

### Permissions
No pre-approval needed. Claude Code's default permission prompt covers the one Bash command. The user sees and approves the settings.json write inline. `python3` is used (not `jq`) since Python is universally available.

## Error Handling

- If vault path doesn't exist: `/recon.setup` re-prompts before writing anything
- If `settings.json` doesn't exist: `python3` patch creates the mcpServers key from scratch via `setdefault`
- If MCP server isn't running (plugin not installed): `get_vault_status_tool` won't be available — this is expected pre-install, not a case we need to handle in-skill
