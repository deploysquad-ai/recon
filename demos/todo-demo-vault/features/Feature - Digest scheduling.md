---
actors:
- '[[Persona - Overwhelmed Individual]]'
belongs_to: '[[Module - Daily Digest]]'
depends_on: []
epic: '[[Epic - Morning digest email]]'
governed_by:
- '[[Constraint - Email deliverability]]'
implements:
- '[[User Story - Set digest delivery time]]'
name: Digest scheduling
related_to:
- '[[Feature - Digest email composer]]'
schema_version: 1
status: draft
supports:
- '[[Goal - Deliver reliable daily digest]]'
tags:
- project/focus
target_version: '[[Version - v1.0]]'
type: feature
---

## Description

Allows users to configure when their daily digest is delivered. Stores per-user schedule preferences, manages timezone-aware delivery scheduling, and queues digest jobs via a background task system.

## Scope

In scope: time picker UI, timezone detection and override, scheduler persistence. Out of scope: day-of-week configuration, multiple digests per day, digest pause.