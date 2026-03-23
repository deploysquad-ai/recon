# Linking Pass

## When This File Is Used

After all nodes are authored (Phase 1 complete) and version assignment is done.

## Goal

Traverse the full graph. Propose typed wikilinks for optional edge fields. Write confirmed links via `update_node()`. Rebuild the index.

## Flow

1. Call `embed_nodes_tool()` — one-time, embeds all nodes and caches results
2. For each node, use heuristics to propose `governed_by` and `depends_on` links (see below)
3. For each node, call `find_similar_tool(node_path, top_k=5)` → propose top matches as `related_to` candidates
4. Present each proposal to the user; accept/reject
5. Write confirmed links via `update_node_tool`
6. Call `build_index_tool()` to rebuild the index

## Heuristic Signals (for governed_by and depends_on)

1. **Shared personas:** Two nodes that reference the same Persona via `actors` are candidates for `related_to`.
2. **Name mentions:** A node's body text mentions another node's `name` field verbatim.
3. **Module co-membership:** Two Features in the same Module without `depends_on` between them → candidate for `related_to`.
4. **Constraint reach:** A Constraint governing a Module logically applies to Features in that Module.

## Traversal Order

1. Constraints — propose `governed_by` on Modules, User Stories, Features, Decisions
2. Decisions — propose `governed_by` on Modules, User Stories, Features
3. Modules — propose `depends_on` between Modules
4. User Stories — `related_to` from `find_similar_tool`
5. Epics — `related_to` from `find_similar_tool`
6. Features — `depends_on`, `governed_by` via heuristics; `related_to` from `find_similar_tool`

## Proposal Format

For each proposed link, present to the user:

```
Propose: [[Feature - X]] → related_to → [[Feature - Y]]
Signal:  Semantic similarity: 0.87 (from find_similar_tool)
Accept? [y/n]
```

Batch proposals by node type. Let the user accept/reject each one.

## Writing Links

- Only write links the user confirms
- Call `update_node_tool(file_path, {"related_to": [...]})` — merge with existing list, do not overwrite
- Verify every target node exists before writing. If missing, flag it and skip.

## After Linking

1. Call `build_index_tool()` to rebuild the full index
2. Announce: "Linking pass complete. Index rebuilt."
