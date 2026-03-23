# Context Injection + Artifact Tracking

**Date:** 2026-03-28
**Status:** Approved

## Problem

Recon builds a structured project graph (goals, personas, constraints, decisions, user stories, features) but the output — CONTEXT.md — currently goes nowhere automatically. Spec-driven development skills (`/brainstorming`, `/writing-plans`, `/feature-dev`) start every session from zero, re-discovering project context that recon already captured.

Additionally, once a technical spec is produced by those skills, there's no way to link it back to the Feature node in the graph. You can't ask "which features have specs?" or "what's the spec for Focus View?"

## Design Principles

- **Recon is the PM layer.** It knows the what, why, who, and constraints. It does not do technical design.
- **Spec-driven skills handle the how.** Brainstorming, writing-plans, feature-dev produce technical specs and implementation plans. Recon does not replace or orchestrate them.
- **No coupling to skill internals.** Recon writes files and exposes data. It never invokes brainstorming or writing-plans directly. Users pick their own tools.
- **The graph stays connected.** Like a PR referencing a Jira ticket, artifacts produced during development link back to the Feature node.

## Changes

### 1. `spec_path` field on FeatureNode

Add an optional field to the Feature model:

```python
spec_path: str | None = None
```

This is a vault-relative path to the technical spec file (e.g., `docs/superpowers/specs/2026-03-28-focus-view-design.md`). Set via `update_node_tool` after a spec is produced by any skill.

Enables queries like:
- "Which features have specs?" — `list_nodes(type="feature")` + check `spec_path`
- "What's the spec for Focus View?" — `get_node("features/Feature - Focus View.md")` → `spec_path`

### 2. `generate_context_tool` gains an `output_path` parameter

Current behavior: returns CONTEXT.md as a string. New behavior:

| `output_path` value | Behavior |
|---|---|
| omitted / `None` | Returns string (backward compatible) |
| `"auto"` | Writes to `{vault}/features/CONTEXT - {feature-name}.md` and returns the path |
| any string path | Writes to that vault-relative path and returns the path |

The auto path puts the context file next to the Feature file in Obsidian, making it visible in the graph view.

The MCP tool writes the file and returns:
```json
{"context": "...", "output_path": "features/CONTEXT - Focus View.md"}
```

### 3. Skill guidance updates

After the authoring session completes (linking pass done, index rebuilt), the `/recon` skill presents next steps:

> "Your graph is ready. To start building a feature:
> 1. Ask me to generate context for any feature (e.g. 'generate context for Focus View')
> 2. Start a new session and run `/brainstorming` — tell it to read the context file
> 3. After the spec is written, come back and I'll link it to the feature node"

The `/recon.add-feature` skill, after creating or updating a Feature, offers to generate its context and link an existing spec.

### 4. No new skill

There is no `/recon.dev` or orchestration skill. Recon writes context to disk. The user invokes whatever spec/implementation skill they prefer. The spec gets linked back to the Feature node via `update_node_tool`.

## What does NOT change

- `generate_context()` traversal logic — untouched
- CONTEXT.md format — untouched
- Brainstorming / writing-plans / feature-dev / executing-plans skills — untouched
- No coupling to superpowers or any other plugin internals
- CLI subcommands — unchanged (generate_context already exists)

## User workflow

```
/recon                                    # Author the full graph
"generate context for Focus View"         # Writes CONTEXT - Focus View.md

--- new session ---

/brainstorming                            # User says "I have project context at
                                          #   features/CONTEXT - Focus View.md"
                                          # Skill reads it, skips discovery,
                                          #   jumps to technical design
                                          # Produces spec at docs/superpowers/specs/...

--- back to recon session ---

"link the spec to Focus View"             # update_node_tool sets spec_path
```

## Implementation scope

| Component | Change | Size |
|---|---|---|
| `models/feature.py` | Add `spec_path: str \| None = None` | 1 line |
| `mcp_server.py` | Add `output_path` param to `generate_context_tool` | ~15 lines |
| `context.py` | Add `write_context()` helper | ~10 lines |
| `skills/recon/SKILL.md` | Add "next steps" guidance after authoring | ~10 lines |
| `skills/recon-add-feature/SKILL.md` | Offer context generation + spec linking | ~5 lines |
| Tests | Feature model test, context write test, MCP tool test | ~40 lines |
