# 🛰️ recon — Obsidian × AI Knowledge Base

> Your project's brain — built by AI, lived in Obsidian.

[![PyPI version](https://badge.fury.io/py/deploysquad-recon-core.svg)](https://pypi.org/project/deploysquad-recon-core/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/deploysquad-ai/recon/blob/main/LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-MCP_Server-blue)](https://claude.ai/code)
[![Obsidian](https://img.shields.io/badge/Obsidian-Compatible-7C3AED)](https://obsidian.md)

recon is a Claude Code MCP server that turns a natural conversation into a structured project knowledge graph — stored as Markdown in your Obsidian vault.

You describe your project. Claude infers goals, personas, modules, decisions, and features — then writes them as linked nodes. No forms. No templates.

The graph then feeds focused context back to any AI session via `generate_context()` — so Claude always knows what you're building, every session.

---

## Install

```
/plugin marketplace add deploysquad-ai/recon
/plugin install recon@deploysquad-ai/recon
```

Then `cd` into your project and run `/recon` — the graph is written to the project root.

---

## The loop

```
💬 /recon       →   🧠 graph         →   ⚡ CONTEXT.md    →   🏗️ build
describe             10 node types        per feature           with context
project                                                              ↓
                ←─────────────── 🔄 /recon.add-feature ───────────┘
                                  keep graph current
```

---

## Node types

Project → Goals → Personas → Constraints → Modules → Decisions → User Stories → Epics → Features → Versions

All stored as `[[wikilinked]]` Markdown in your Obsidian vault.

---

## Python API

```python
from deploysquad_recon_core import (
    create_node, get_node, list_nodes, update_node,
    resolve_links, build_index, generate_context,
)

# Author a node
path = create_node("feature", {
    "name": "Task Board",
    "description": "Kanban board for task management",
    "implements": ["[[User Story - Create Task]]"],
    "actors": ["[[Persona - Manager]]"],
    "belongs_to": "[[Module - Dashboard]]",
    "status": "active",
}, project_dir)

# Generate CONTEXT.md for any AI session
context = generate_context("Task Board", project_dir)

# Write CONTEXT.md directly to the vault
from deploysquad_recon_core.context import write_context
path = write_context(context, "auto", project_dir, feature_name="Task Board")
# → features/CONTEXT - Task Board.md

# Link a spec back to the feature
update_node("features/Feature - Task Board.md", {
    "spec_path": "docs/specs/task-board-design.md"
})
```

---

## Semantic linking (optional)

recon can embed nodes and find semantically similar ones using the Gemini API.

**Claude Code plugin users:** add `export GEMINI_API_KEY=your-key` to your shell rc (`~/.zshrc` or `~/.bashrc`) and restart Claude Code. The MCP server inherits the env from your shell. The `/recon` preflight prints a tip with this exact instruction when the key is missing. Free key: <https://aistudio.google.com/apikey>

**Python library users:**

```bash
pip install "deploysquad-recon-core[embed]"
```

Set `GEMINI_API_KEY` in your environment, then:

```python
from deploysquad_recon_core import embed_nodes, find_similar

embed_nodes(project_dir)
similar = find_similar(node_path, project_dir)
```

---

## Links

- [GitHub](https://github.com/deploysquad-ai/recon)
- [Documentation](https://github.com/deploysquad-ai/recon/tree/main/docs)
