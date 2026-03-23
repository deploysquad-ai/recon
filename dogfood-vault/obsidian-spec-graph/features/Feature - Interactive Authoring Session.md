---
actors:
- '[[Persona - Product Developer]]'
- '[[Persona - LLM Agent]]'
belongs_to: '[[Module - Agent CLI]]'
depends_on:
- '[[Feature - Create Node via Tool Call]]'
epic: '[[Epic - Graph Authoring System]]'
governed_by: []
implements:
- '[[User Story - Author Project Graph]]'
name: Interactive Authoring Session
related_to: []
schema_version: 1
status: active
supports:
- '[[Goal - Structured Graph Authoring]]'
target_version: '[[Version - MVP]]'
type: feature
---

## Description

CLI loads AGENT.md + schema files, wires graph-core as tools, runs conversation loop.

## Scope

Phase 1 (authoring) + Phase 2 (version assignment + heuristic linking).