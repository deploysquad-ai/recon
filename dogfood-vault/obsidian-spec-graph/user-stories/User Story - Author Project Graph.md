---
acceptance_criteria:
- User can describe project in natural language
- LLM infers and drafts nodes in bulk
- User reviews and confirms before write
- All 10 node types can be authored
actors:
- '[[Persona - Product Developer]]'
belongs_to: '[[Module - Agent CLI]]'
governed_by: []
name: Author Project Graph
related_to: []
schema_version: 1
status: active
supports:
- '[[Goal - Structured Graph Authoring]]'
target_version: '[[Version - MVP]]'
type: user-story
---

## Story

As a Product Developer, I want to describe my project in natural language so that the LLM builds a structured graph for me.