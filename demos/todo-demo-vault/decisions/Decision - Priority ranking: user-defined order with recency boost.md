---
belongs_to: '[[Module - Focus Engine]]'
governed_by: []
name: 'Priority ranking: user-defined order with recency boost'
related_to: []
schema_version: 1
status: active
tags:
- project/focus
type: decision
---

## Context

The Focus Engine needs a way to determine which task is the user's top priority. Fully automated ranking risks surfacing the wrong task; fully manual ranking requires too much user effort.

## Decision

Default ranking is user-defined drag-and-drop order within a project. A recency boost surfaces tasks that haven't been touched in 3+ days. Users can pin a task to always surface it as #1.

## Rationale

Respects user intent (they know their priorities) while providing a light nudge for neglected tasks. Avoids complex ML models that require training data an early product doesn't have.

## Alternatives Considered

- Fully automated ML ranking: Requires behavioral data, black-box feels out of control
- Due-date based: Only works if users diligently set due dates — most don't
- Eisenhower matrix: Too much cognitive overhead for overwhelmed users