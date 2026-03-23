---
belongs_to: '[[Module - Agent CLI]]'
governed_by: []
name: LLM as Conversational UI
related_to: []
schema_version: 1
status: active
type: decision
---

## Decision

The LLM calls create_node(type, data) — it never writes files directly. graph-core validates.

## Rationale

Deterministic validation beats probabilistic LLM compliance with prose rules.