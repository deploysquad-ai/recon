---
name: recon.setup
description: Configure recon by connecting it to your Obsidian vault. Run this once after installing the plugin, or to change vault path / API keys.
---

## recon Setup

You are helping the user configure recon by setting their Obsidian vault path and optional Gemini API key.

### Steps

**Step 0 — Check for uv**

Run:

```bash
command -v uvx
```

If the command returns nothing (exit code non-zero or empty output): tell the user exactly this:

> "recon requires `uv` to run its MCP server, but it doesn't appear to be installed.
>
> Install it with:
> ```
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```
> Then restart your terminal and run `/recon.setup` again."

Then **stop**. Do not proceed to the vault path step.

---

**Step 1 — Check current configuration**

Call `get_vault_status_tool()` to see if a vault is already configured. Also check existing settings:

```bash
python3 -c "
import json, pathlib
p = pathlib.Path.home() / '.claude/settings.json'
if p.exists():
    d = json.loads(p.read_text())
    env = d.get('mcpServers', {}).get('recon', {}).get('env', {})
    print(json.dumps(env))
else:
    print('{}')
"
```

Note which values are already set (VAULT_PATH, GEMINI_API_KEY). Only ask about values that are missing or that the user wants to change.

**Step 2 — Ask for the vault path**

If the vault is already configured, say:

> "recon is currently pointing to `<current-path>`. Want to change it, or keep this?"

If not configured, say:

> "What's the full path to your Obsidian vault? (e.g. /Users/yourname/Documents/my-vault)"

Wait for their answer. If they want to keep the existing path, skip to Step 4.

**Step 3 — Validate and apply the vault path**

Call `configure_vault_tool(vault_path="<their-path>")`.

- If it returns `is_configured: true`: continue to Step 4.
- If it returns an error: tell the user the path doesn't exist and ask again.

**Step 4 — Ask for Gemini API key (only if not already set)**

Check if `GEMINI_API_KEY` was found in Step 1. If it's already set, **skip this step entirely** — do not ask again.

If not set, say:

> "Do you have a Gemini API key? It's optional — recon uses it for semantic linking (finding related nodes automatically). Enter it now, or press Enter to skip."

Wait for their answer. If they skip or say no, leave `GEMINI_API_KEY` unset.

**Step 5 — Persist to settings.json**

Run this command (substitute actual values — omit the `GEMINI_API_KEY` line if not provided or already set):

```bash
python3 -c "
import json, pathlib
p = pathlib.Path.home() / '.claude/settings.json'
d = json.loads(p.read_text()) if p.exists() else {}
srv = d.setdefault('mcpServers', {}).setdefault('recon', {})
srv.setdefault('command', 'uvx')
srv.setdefault('args', ['deploysquad-recon-core'])
env = srv.setdefault('env', {})
env['VAULT_PATH'] = '<expanded-path>'
env['GEMINI_API_KEY'] = '<gemini-key>'  # omit if not provided or already set
p.write_text(json.dumps(d, indent=2))
print('done')
"
```

**Step 6 — Confirm**

After the command succeeds, say:

> "Done! recon is now pointing to `<expanded-path>`. Run `/recon` to start building your project graph."

Note: no restart is needed — `configure_vault_tool` already applied the path for this session.
