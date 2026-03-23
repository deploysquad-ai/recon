---
actors:
- '[[Persona - Team Lead]]'
- '[[Persona - Team Member]]'
belongs_to: '[[Module - Team Collaboration]]'
depends_on:
- '[[Feature - Project invitation flow]]'
epic: '[[Epic - Team project sharing]]'
governed_by:
- '[[Constraint - Team data isolation]]'
implements:
- '[[User Story - Invite coworker to shared project]]'
name: Team task visibility
related_to: []
schema_version: 1
status: draft
supports:
- '[[Goal - Enable team collaboration]]'
tags:
- project/focus
target_version: '[[Version - v2.0]]'
type: feature
---

## Description

Shows team members the task list of a shared project with attribution for who owns each task. Team Leads see a summary view across all members. Enforces team data isolation so only project members see the data.

## Scope

In scope: shared project task list, task owner display, Team Lead summary view. Out of scope: commenting, @mentions, task reassignment, activity feed.