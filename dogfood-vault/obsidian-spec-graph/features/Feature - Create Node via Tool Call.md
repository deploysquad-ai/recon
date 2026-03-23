---
actors:
- '[[Persona - LLM Agent]]'
belongs_to: '[[Module - Graph Core]]'
depends_on: []
epic: '[[Epic - Graph Authoring System]]'
governed_by:
- '[[Constraint - Markdown Source of Truth]]'
implements:
- '[[User Story - Validate Node Data]]'
name: Create Node via Tool Call
related_to: []
schema_version: 1
status: active
supports:
- '[[Goal - Structured Graph Authoring]]'
target_version: '[[Version - MVP]]'
type: feature
---

## Description

create_node(type, data) validates against Pydantic models and writes an atomic .md file.

## Scope

All 10 node types, frontmatter validation, atomic file writes.