---
actors:
- '[[Persona - Product Developer]]'
belongs_to: '[[Module - Context Builder]]'
depends_on: []
epic: '[[Epic - Handoff Pipeline]]'
governed_by:
- '[[Constraint - Markdown Source of Truth]]'
implements:
- '[[User Story - Generate Context Bundle]]'
name: Generate CONTEXT.md
related_to: []
schema_version: 1
status: active
supports:
- '[[Goal - Spec-Kit Handoff]]'
target_version: '[[Version - MVP]]'
type: feature
---

## Description

generate_context(feature_name) traverses Feature -> Module -> Project, collecting User Stories, Constraints, Decisions, Goals.

## Scope

Graph traversal, section rendering, graceful handling of missing optional data.