---
actors:
- '[[Persona - Overwhelmed Individual]]'
- '[[Persona - Team Member]]'
belongs_to: '[[Module - Task & Project Management]]'
depends_on: []
epic: '[[Epic - Core task experience]]'
governed_by:
- '[[Constraint - Mobile-first design]]'
implements:
- '[[User Story - Complete a task]]'
name: Task completion
related_to:
- '[[Feature - Task creation form]]'
- '[[Feature - Focus view]]'
schema_version: 1
status: draft
supports:
- '[[Goal - Reduce task overwhelm]]'
- '[[Goal - Build daily focus habit]]'
tags:
- project/focus
target_version: '[[Version - MVP]]'
type: feature
---

## Description

A single-tap interaction to mark a task as complete. Triggers an animated completion state, removes the task from the active list, and logs it to the completion history.

## Scope

In scope: mark complete, undo within 5 seconds, completion history. Out of scope: recurring tasks, partial completion states.