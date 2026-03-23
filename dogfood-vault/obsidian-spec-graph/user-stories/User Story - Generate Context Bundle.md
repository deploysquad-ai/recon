---
acceptance_criteria:
- Context includes Project, Goals, Module, User Stories, Constraints, Decisions
- Output starts with context_bundle_version comment
- Missing optional sections omitted gracefully
actors:
- '[[Persona - Product Developer]]'
belongs_to: '[[Module - Context Builder]]'
governed_by: []
name: Generate Context Bundle
related_to: []
schema_version: 1
status: active
supports:
- '[[Goal - Spec-Kit Handoff]]'
target_version: '[[Version - MVP]]'
type: user-story
---

## Story

As a Product Developer, I want to generate a CONTEXT.md for any Feature so that I can hand it off to spec-kit.