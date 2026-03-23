# Context Bundle Generation

## When This File Is Used

On-demand, after the graph is complete and the linking pass has run. Triggered when the user asks for context on a specific Feature.

## What It Does

Calls `generate_context_tool(feature_name)` from recon-core. This traverses the Feature's graph relationships and returns a structured Markdown string — the `CONTEXT.md` that is handed off to spec-kit.

## Traversal (performed by recon-core)

Given a Feature node, `generate_context_tool` follows these edges:

1. `belongs_to` → Module
2. Module's `belongs_to` → Project
3. `implements` → each User Story (and their `supports` → Goals)
4. `supports` → Goals (direct)
5. Union of Feature + Module `governed_by` → Constraints and Decisions (deduplicated)
6. `depends_on` → dependency nodes with their status
7. `related_to` → related Features
8. `target_version` → Version
9. Feature's and User Stories' `supports` → Goals (deduplicated)

## Output

The output is a Markdown file written to:
`{vault}/{project-slug}/features/CONTEXT - {feature-name}.md`

It contains structured sections: Project, Goals, Version, Module, User Stories, Constraints, Decisions, Dependencies, Related Features.

## When to Use

- Before handing off a Feature to spec-kit for detailed specification
- When the user asks "what context does this feature need?"
- To verify the graph is complete — missing sections in the output indicate missing nodes or edges

## How to Call

```
generate_context_tool("Feature Name")
```

The `feature_name` is the name field, not the filename. recon-core locates the file automatically.
