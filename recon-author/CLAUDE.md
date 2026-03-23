# CLAUDE.md — recon-author

## What This Is

Agent instruction files loaded as LLM context during interactive graph authoring sessions. These files tell the LLM HOW to converse with users and WHAT tool functions to call.

## How These Files Are Used

The CLI loads these files as system/context prompts for the LLM:
- `AGENT.md` is **always loaded** (orchestration, tool contract, authoring order)
- Schema files from `schemas/` are loaded per-node-type as needed
- `linking-pass.md` is loaded during Phase 2
- `context-bundle.md` is loaded on-demand for CONTEXT.md generation

## Key Principles

1. **LLM calls recon-core tools** — never writes files directly. All writes go through `create_node()` / `update_node()`.
2. **Inference-first** — the LLM extracts graph structure from natural conversation. Schema prompts are fallback, not a script.
3. **No validation rules here** — recon-core's Pydantic models handle validation. Schema files only describe fields and provide conversation hints.

## File Structure

```
recon-author/
  AGENT.md               # Always-loaded: role, tool contract, authoring order, phases
  schemas/
    project.md           # Field table + fallback prompts for Project nodes
    goal.md              # ...for Goal nodes
    persona.md           # ...for Persona nodes (goals: list[str], context: str)
    constraint.md        # ...for Constraint nodes
    version.md           # ...for Version nodes
    module.md            # ...for Module nodes
    decision.md          # ...for Decision nodes
    user-story.md        # ...for User Story nodes
    epic.md              # ...for Epic nodes
    feature.md           # ...for Feature nodes
  linking-pass.md        # Phase 2: heuristic linking rules
  context-bundle.md      # CONTEXT.md generation reference
```

## Editing These Files

When editing schema files, keep them SHORT:
- Field reference table (name, type, required, notes)
- Body section templates
- Fallback question prompts (2-4 per node type)
- One example `create_node()` call

Do NOT add validation rules — those belong in recon-core's Pydantic models.
