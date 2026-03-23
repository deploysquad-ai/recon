---
acceptance_criteria:
- Invalid data rejected with clear error message
- Type field enforced via Literal types
- Wikilink format validated via regex pattern
actors:
- '[[Persona - LLM Agent]]'
belongs_to: '[[Module - Graph Core]]'
governed_by: []
name: Validate Node Data
related_to: []
schema_version: 1
status: active
supports:
- '[[Goal - Structured Graph Authoring]]'
target_version: '[[Version - MVP]]'
type: user-story
---

## Story

As an LLM Agent, I want node data validated before writing so that the vault never contains invalid files.