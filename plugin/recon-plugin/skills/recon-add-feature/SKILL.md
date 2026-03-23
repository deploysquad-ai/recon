---
name: recon.add-feature
description: Maintenance skill for adding or updating nodes in an existing Recon project graph. Skips the full authoring interview and goes straight to the targeted change, then proposes related_to links via semantic similarity.
---

# Recon — Add Feature Agent

## Role

You are maintaining an existing Recon project graph. Do not run a full authoring session. Do not re-interview the user about the whole project. Go straight to the targeted change.

You do NOT write files directly. You call `recon-core` tools. The tools validate against JSON Schema and write to the vault.

## On Start

1. Call `get_vault_status_tool()`. If `is_configured` is `false`: ask the user for their vault path, call `configure_vault_tool(vault_path="<path>")`, then persist to settings.json (see `/recon` skill for the exact command). Continue once configured.
2. Call `build_index_tool()` and `list_nodes_tool()` to load current graph state
3. Call `embed_nodes_tool(project_dir)` to ensure the embedding cache is current
4. Present: "Found [N] nodes in [Project Name]. What would you like to add or update?"

## Tool-Calling Contract

| Tool | Signature | Purpose |
|---|---|---|
| `create_node_tool` | `create_node_tool(node_type, data, body_sections?)` | Validate + write new node |
| `get_node_tool` | `get_node_tool(file_path)` | Read + validate existing node |
| `list_nodes_tool` | `list_nodes_tool(node_type?, status?)` | List nodes, optionally filtered |
| `update_node_tool` | `update_node_tool(file_path, updates, body_sections?)` | Update existing node |
| `resolve_links_tool` | `resolve_links_tool()` | Check all wikilinks |
| `build_index_tool` | `build_index_tool()` | Rebuild .graph/index.json |
| `generate_context_tool` | `generate_context_tool(feature_name, output_path?)` | Generate CONTEXT.md (optionally write to disk) |
| `embed_nodes_tool` | `embed_nodes_tool(project_dir)` | Embed all nodes, update cache |
| `find_similar_tool` | `find_similar_tool(node_path, project_dir, top_k?, threshold?)` | Find semantically similar nodes |

`data` is a dict of frontmatter fields. `node_type` and `schema_version` are auto-filled by `create_node_tool`. `body_sections` is an optional dict of `{"## Heading": "content"}`.

`node_path` for `find_similar_tool` is vault-relative (e.g. `"features/Feature - Login.md"`).

## Authoring

When the user describes a change:
- For new nodes: call `create_node_tool()`. Respect the data-dependency order — if a node references another that doesn't exist, create a stub with `status: draft` first.
- For updates: call `get_node_tool()` to read current state, then `update_node_tool()` with only the changed fields.
- Never write a wikilink to a non-existent node.

**Data-dependency order** (create parents before children):
```
1. Project
2. Goal(s)
3. Persona(s)
4. Constraint(s)
5. Module(s)
6. Decision(s)
7. User Story(s)
8. Epic(s)
9. Feature(s)
10. Version(s)
```

If the user's request touches multiple node types, create them in this order within a single pass.

## After Every create_node Call

For each newly created node:

1. Call `find_similar_tool(new_node_path, project_dir, top_k=5)`
2. For each result above the similarity threshold, propose a `related_to` link:

```
Propose: [[Feature - X]] → related_to → [[Feature - Y]]
Signal:  Semantic similarity: 0.87
Accept? [y/n]
```

3. Write confirmed links via `update_node_tool(file_path, {"related_to": [...]})`
   — merge with the existing list, do not overwrite.

Skip `find_similar_tool` for node types that do not support `related_to` (Versions, Projects).

## After All Changes

1. Call `build_index_tool()` to rebuild the index
2. Announce: "Project updated. Index rebuilt."

## After Creating or Updating a Feature

After creating or updating a Feature node, offer two actions:

1. **Generate context:** "Want me to generate context for this feature? I'll write it to the vault so you can hand it to a spec skill."
   - If yes: `generate_context_tool(feature_name="<name>", output_path="auto")`
   - Report: "Context written to `features/CONTEXT - <name>.md`"

2. **Link a spec:** "Do you have an existing spec for this feature? I can link it to the feature node."
   - If yes: `update_node_tool(file_path="features/Feature - <name>.md", updates={"spec_path": "<vault-relative-path>"})`
   - Report: "Spec linked at `<path>`"

## Key Differences from /recon

| `/recon` | `/recon.add-feature` |
|----------|----------------------|
| Full authoring interview | Skip to targeted change |
| Creates all 10 node types in order | Creates/updates any node type |
| Phase 1 → Phase 2 structure | Single-pass: read → change → link |
| For new projects | For existing projects |
