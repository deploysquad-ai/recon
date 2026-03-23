---
actors:
- '[[Persona - Overwhelmed Individual]]'
belongs_to: '[[Module - Focus Engine]]'
depends_on: []
epic: '[[Epic - Focus and priority system]]'
governed_by:
- '[[Constraint - Mobile-first design]]'
implements:
- '[[User Story - Receive focus nudge when switching tasks]]'
name: Focus nudge
related_to:
- '[[Feature - Focus view]]'
schema_version: 1
status: draft
supports:
- '[[Goal - Build daily focus habit]]'
tags:
- project/focus
target_version: '[[Version - MVP]]'
type: feature
---

## Description

An in-app behavioral nudge triggered when the user navigates away from the focus view shortly after starting a task. Displays a brief, encouraging message encouraging them to return to their priority.

## Scope

In scope: context-switch detection, nudge message display, dismiss action, session-level rate limiting. Out of scope: push notifications, nudge scheduling, AI-generated message variants.