---
belongs_to: '[[Project - obsidian-spec-graph]]'
governed_by: []
name: Two-Phase Authoring
related_to: []
schema_version: 1
status: active
type: decision
---

## Decision

Phase 1 authors all nodes, Phase 2 resolves links. Can't reliably link to nodes that don't exist yet.

## Rationale

Forward-reference problem — full graph visibility produces more accurate linking.