# Integration Guide — recon + AI Dev Workflows

recon's graph is most powerful when it feeds context into your AI sessions. This guide shows how.

---

## The problem

Every new AI session starts blank. You re-explain your project, re-describe the architecture, re-list the constraints. The AI makes reasonable-sounding but wrong assumptions about things you've already decided.

recon solves this by maintaining a persistent, structured knowledge graph of your project. Before any AI task, you generate a focused context bundle — and the AI starts informed.

---

## How `generate_context()` works

`generate_context("Feature - X")` traverses the graph from a Feature node and collects:

- The Feature itself (description, status, linked epics)
- Related User Stories (what users need)
- Related Personas (who is affected)
- Related Modules (what code is involved)
- Related Decisions (architecture choices that apply)
- Project Goals (the why)
- Constraints (hard limits)

It outputs a `CONTEXT.md` file — a structured brief for the AI. One file, everything relevant, nothing extraneous.

---

## Integration patterns

### Before starting a feature

```
"generate context for Task Board"
```

This writes `features/CONTEXT - Task Board.md` directly to your vault. In your next session, tell the AI to read that file:

```
/brainstorming
"I have project context at features/CONTEXT - Task Board.md"
```

Claude now knows:
- What the feature needs to do
- Who it's for
- What modules it touches
- What decisions have already been made
- What constraints apply

No copy-pasting. The context file lives in your vault, visible in Obsidian's graph view alongside the feature node.

### After writing a spec

Once a spec skill produces a technical spec, link it back to the feature:

```
"link the spec to Task Board"
→ update_node_tool("features/Feature - Task Board.md", {"spec_path": "docs/specs/task-board-design.md"})
```

Now you can query the graph:
- "Which features have specs?" — `list_nodes(type="feature")` + check `spec_path`
- "What's the spec for Task Board?" — `get_node("features/Feature - Task Board.md")` → `spec_path`

### Before writing an implementation plan

Run `generate_context()` for the feature you're planning. The plan will reference the right modules, respect existing decisions, and avoid architecture that contradicts your constraints.

### Before brainstorming

Context primes the brainstorm. "Given this project's goals, personas, and constraints, brainstorm approaches for Feature X" is a much stronger prompt than "brainstorm approaches for Feature X."

### New session or new team member

```bash
# See all features
list_nodes_tool("feature")

# Generate context for any one of them — writes to vault
generate_context_tool("Authentication", output_path="auto")
```

Instant orientation. No walkthrough needed.

---

## Keeping the graph current

### Use `/recon.add-feature` for incremental updates

When you add a new feature or change an existing one:

1. Run `/recon.add-feature` in Claude Code
2. Describe the change — recon infers what nodes to create or update
3. Semantic linking suggests connections to existing nodes
4. Confirm the links — the graph stays coherent

### When to re-run `/recon` from scratch

Run a fresh `/recon` session when:
- The project pivots significantly
- You're onboarding someone and want a clean, reviewed graph
- More than half the nodes need updating

### The full cycle

```
/recon                              author the graph
  ↓
"generate context for Feature X"    write CONTEXT.md to vault
  ↓
/brainstorming                      read context, produce spec
  ↓
"link the spec to Feature X"        connect spec → feature node
  ↓
/feature-dev or /writing-plans      build the feature with full context
  ↓
/recon.add-feature                  update graph with what you learned
  ↓
next feature...
```

---

## MCP tool reference

All 10 tools are exposed via the recon MCP server and callable from Claude Code:

| Tool | Signature | Purpose |
|------|-----------|---------|
| `create_node_tool` | `(node_type, data, body_sections?)` | Validate + write new node |
| `get_node_tool` | `(file_path)` | Read + validate existing node |
| `list_nodes_tool` | `(node_type?, status?)` | List nodes, optionally filtered |
| `update_node_tool` | `(file_path, updates, body_sections?)` | Update existing node (including `spec_path`) |
| `resolve_links_tool` | `()` | Check all wikilinks for broken references |
| `build_index_tool` | `()` | Rebuild `.graph/index.json` |
| `generate_context_tool` | `(feature_name, output_path?)` | Generate CONTEXT.md — optionally write to vault |
| `get_vault_status_tool` | `()` | Check if vault is configured |
| `configure_vault_tool` | `(vault_path)` | Set vault path in-memory |
| `embed_nodes_tool` | `()` | Embed all nodes for semantic search |
| `find_similar_tool` | `(node_path, project_dir, top_k?, threshold?)` | Find semantically similar nodes |

### `output_path` for context generation

| `output_path` value | Behavior |
|---|---|
| omitted / `None` | Returns context string only (backward compatible) |
| `"auto"` | Writes to `features/CONTEXT - {feature-name}.md` and returns the path |
| any string path | Writes to that vault-relative path and returns the path |
