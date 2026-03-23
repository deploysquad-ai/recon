# recon Setup Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `/recon.setup` skill and a setup guard to `/recon` so plugin-installed users are guided through vault configuration before authoring.

**Architecture:** Add `get_vault_status_tool` to the MCP server for detection; prepend a guard block to the `/recon` skill that calls it; create a new `/recon.setup` skill that patches `~/.claude/settings.json` via `python3`; bundle a `.mcp.json` in the plugin so `/plugin install` wires the MCP server automatically.

**Tech Stack:** Python (FastMCP, Pydantic), Markdown skill files, JSON

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `recon-core/src/deploysquad_recon_core/mcp_server.py` | Modify | Add `get_vault_status_tool` |
| `recon-core/tests/test_mcp_server.py` | Modify | Tests for `get_vault_status_tool` |
| `plugin/recon-plugin/.mcp.json` | Create | Register MCP server on plugin install |
| `plugin/recon-plugin/skills/recon/SKILL.md` | Modify | Prepend setup guard block |
| `skill/recon.md` | Modify | Mirror: same setup guard (kept in sync) |
| `plugin/recon-plugin/skills/recon-setup/SKILL.md` | Create | `/recon.setup` skill |
| `skill/recon.setup.md` | Create | Mirror of recon-setup SKILL.md |

Tasks 1–4 are fully independent and can be parallelized.

---

## Task 1: Add `get_vault_status_tool` to MCP server

**Files:**
- Modify: `recon-core/src/deploysquad_recon_core/mcp_server.py`
- Modify: `recon-core/tests/test_mcp_server.py`

- [ ] **Step 1: Write failing tests**

Add to `recon-core/tests/test_mcp_server.py`:

```python
from deploysquad_recon_core.mcp_server import get_vault_status_tool


def test_get_vault_status_not_configured():
    """get_vault_status returns is_configured=False when VAULT_PATH is default '.'."""
    with patch("deploysquad_recon_core.mcp_server.PROJECT_DIR", Path(".")):
        result = json.loads(get_vault_status_tool())
    assert result["is_configured"] is False
    assert result["vault_path"] == "."


def test_get_vault_status_configured(tmp_path):
    """get_vault_status returns is_configured=True when VAULT_PATH is a real directory."""
    with patch("deploysquad_recon_core.mcp_server.PROJECT_DIR", tmp_path):
        result = json.loads(get_vault_status_tool())
    assert result["is_configured"] is True
    assert result["vault_path"] == str(tmp_path)


def test_get_vault_status_nonexistent_path():
    """get_vault_status returns is_configured=False when path doesn't exist."""
    with patch("deploysquad_recon_core.mcp_server.PROJECT_DIR", Path("/nonexistent/vault")):
        result = json.loads(get_vault_status_tool())
    assert result["is_configured"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd recon-core
pytest tests/test_mcp_server.py::test_get_vault_status_not_configured tests/test_mcp_server.py::test_get_vault_status_configured tests/test_mcp_server.py::test_get_vault_status_nonexistent_path -v
```

Expected: FAIL with `ImportError` or `AttributeError` (function not defined yet)

- [ ] **Step 3: Implement `get_vault_status_tool`**

Add after the `_serialize_error` function in `recon-core/src/deploysquad_recon_core/mcp_server.py`:

```python
@mcp.tool()
def get_vault_status_tool() -> str:
    """Check whether the vault is configured. Returns vault_path and is_configured flag.

    is_configured is True when VAULT_PATH is set to a real existing directory
    (i.e. not the default '.').
    """
    is_configured = PROJECT_DIR != Path(".") and PROJECT_DIR.exists()
    return json.dumps({
        "vault_path": str(PROJECT_DIR),
        "is_configured": is_configured,
    })
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd recon-core
pytest tests/test_mcp_server.py::test_get_vault_status_not_configured tests/test_mcp_server.py::test_get_vault_status_configured tests/test_mcp_server.py::test_get_vault_status_nonexistent_path -v
```

Expected: 3 PASSED

- [ ] **Step 5: Run full test suite to check for regressions**

```bash
cd recon-core
pytest -v
```

Expected: All tests pass (281+ tests)

- [ ] **Step 6: Commit**

```bash
git add recon-core/src/deploysquad_recon_core/mcp_server.py recon-core/tests/test_mcp_server.py
git commit -m "feat: add get_vault_status_tool to MCP server

Returns {vault_path, is_configured} for setup detection in /recon skill.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: Add `.mcp.json` to the plugin bundle

**Files:**
- Create: `plugin/recon-plugin/.mcp.json`

- [ ] **Step 1: Create the file**

Create `plugin/recon-plugin/.mcp.json`:

```json
{
  "mcpServers": {
    "recon": {
      "command": "uvx",
      "args": ["deploysquad-recon-core"],
      "env": {
        "VAULT_PATH": ""
      }
    }
  }
}
```

- [ ] **Step 2: Verify it parses as valid JSON**

```bash
python3 -c "import json; json.load(open('plugin/recon-plugin/.mcp.json')); print('valid')"
```

Expected: `valid`

- [ ] **Step 3: Commit**

```bash
git add plugin/recon-plugin/.mcp.json
git commit -m "feat: add .mcp.json to plugin bundle for plugin install support

Enables /plugin install recon@deploysquad to auto-register the MCP server.
VAULT_PATH is empty by default — configured via /recon.setup.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: Add setup guard to `/recon` skill

**Files:**
- Modify: `plugin/recon-plugin/skills/recon/SKILL.md`
- Modify: `skill/recon.md`

These two files are identical — apply the same change to both.

- [ ] **Step 1: Prepend setup guard block to `plugin/recon-plugin/skills/recon/SKILL.md`**

Insert after the frontmatter block (after the closing `---`) and before `# Graph Author Agent`:

```markdown
## Setup Check

**Run this before anything else.**

Call `get_vault_status_tool()`.

- If `is_configured` is `false`: tell the user exactly this:

  > "recon isn't set up yet — I don't know which Obsidian vault to write to.
  > Run `/recon.setup` to connect your vault. It takes about 30 seconds."

  Then **stop**. Do not ask any questions. Do not proceed into the authoring session.

- If `is_configured` is `true`: proceed normally with the authoring session below.

---

```

The file should now start with the frontmatter, then `## Setup Check`, then `---`, then `# Graph Author Agent`.

- [ ] **Step 2: Apply the identical change to `skill/recon.md`**

Insert the same block (same position — after frontmatter `---`, before `# Graph Author Agent`).

- [ ] **Step 3: Verify both files have the guard**

```bash
grep -n "Setup Check" plugin/recon-plugin/skills/recon/SKILL.md skill/recon.md
```

Expected: one match per file

- [ ] **Step 4: Verify the files are still identical**

```bash
diff plugin/recon-plugin/skills/recon/SKILL.md skill/recon.md
```

Expected: no output (files are identical)

- [ ] **Step 5: Commit**

```bash
git add plugin/recon-plugin/skills/recon/SKILL.md skill/recon.md
git commit -m "feat: add setup guard to /recon skill

Calls get_vault_status_tool() first. If vault not configured,
informs user and redirects to /recon.setup.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 4: Create `/recon.setup` skill

**Files:**
- Create: `plugin/recon-plugin/skills/recon-setup/SKILL.md`
- Create: `skill/recon.setup.md`

These two files should be identical.

- [ ] **Step 1: Create `plugin/recon-plugin/skills/recon-setup/SKILL.md`**

```markdown
---
name: recon.setup
description: Configure recon by connecting it to your Obsidian vault. Run this once after installing the plugin.
---

## recon Setup

You are helping the user configure recon by setting their Obsidian vault path.

### Steps

**Step 1 — Ask for the vault path**

Say exactly:

> "What's the full path to your Obsidian vault? (e.g. /Users/yourname/Documents/my-vault)"

Wait for their answer.

**Step 2 — Expand and validate the path**

If the path starts with `~`, expand it using:

```bash
echo <path>
```

Then verify the directory exists:

```bash
test -d <expanded-path> && echo "exists" || echo "not found"
```

If the output is `not found`: tell the user the path doesn't exist and ask them to check it. Do not proceed until the path resolves to a real directory.

**Step 3 — Write VAULT_PATH to settings.json**

Run this command (substitute `<expanded-path>` with the actual path):

```bash
python3 -c "
import json, pathlib
p = pathlib.Path.home() / '.claude/settings.json'
d = json.loads(p.read_text()) if p.exists() else {}
d.setdefault('mcpServers', {}).setdefault('recon', {}).setdefault('env', {})['VAULT_PATH'] = '<expanded-path>'
p.write_text(json.dumps(d, indent=2))
print('done')
"
```

**Step 4 — Confirm and instruct restart**

After the command succeeds, say exactly:

> "Done! recon is now pointing to `<expanded-path>`.
>
> **Restart Claude Code** to apply the change, then run `/recon` to start building your project graph."
```

- [ ] **Step 2: Create `skill/recon.setup.md` as an identical copy**

```bash
cp plugin/recon-plugin/skills/recon-setup/SKILL.md skill/recon.setup.md
```

- [ ] **Step 3: Verify both files are identical**

```bash
diff plugin/recon-plugin/skills/recon-setup/SKILL.md skill/recon.setup.md
```

Expected: no output

- [ ] **Step 4: Commit**

```bash
git add plugin/recon-plugin/skills/recon-setup/SKILL.md skill/recon.setup.md
git commit -m "feat: add /recon.setup skill for vault path configuration

Asks for vault path, validates it exists, patches ~/.claude/settings.json
via python3. User approves the Bash command via Claude Code's permission prompt.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Final: Verify everything is wired

- [ ] **Step 1: Confirm all four commits are present**

```bash
git log --oneline -6
```

Expected: 4 new commits on top of existing history

- [ ] **Step 2: Confirm plugin structure**

```bash
find plugin/recon-plugin -not -path "*/__pycache__/*" | sort
```

Expected output includes:
```
plugin/recon-plugin/.claude-plugin/plugin.json
plugin/recon-plugin/.mcp.json
plugin/recon-plugin/skills/recon/SKILL.md
plugin/recon-plugin/skills/recon-add-feature/SKILL.md
plugin/recon-plugin/skills/recon-setup/SKILL.md
```

- [ ] **Step 3: Confirm skill/ directory**

```bash
ls skill/
```

Expected: `recon.md`, `recon.add-feature.md`, `recon.setup.md`, `CLAUDE.md`, `openclaw/`

- [ ] **Step 4: Final commit (if any cleanup needed)**

```bash
git add -p  # stage any stragglers
git commit -m "chore: wire recon setup flow end-to-end

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```
