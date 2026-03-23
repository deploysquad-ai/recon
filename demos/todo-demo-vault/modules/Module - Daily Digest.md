---
actors:
- '[[Persona - Overwhelmed Individual]]'
- '[[Persona - Team Member]]'
belongs_to: '[[Project - Focus]]'
depends_on:
- '[[Module - Focus Engine]]'
governed_by:
- '[[Constraint - Email deliverability]]'
name: Daily Digest
related_to: []
schema_version: 1
status: draft
tags:
- project/focus
type: module
---

## Description

Generates and delivers a personalized morning email to each user containing their top 3 priorities for the day. Runs on a per-user schedule, queries the Focus Engine for current rankings, and sends via a transactional email provider.