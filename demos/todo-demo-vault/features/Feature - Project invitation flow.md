---
actors:
- '[[Persona - Team Lead]]'
- '[[Persona - Team Member]]'
belongs_to: '[[Module - Team Collaboration]]'
depends_on: []
epic: '[[Epic - Team project sharing]]'
governed_by:
- '[[Constraint - Team data isolation]]'
implements:
- '[[User Story - Invite coworker to shared project]]'
name: Project invitation flow
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

Enables a Team Lead to invite coworkers to a shared project via email. Generates a signed invitation link, sends it via the transactional email provider, and handles the accept flow for both existing and new users.

## Scope

In scope: invite by email, invitation email, accept flow, membership list view. Out of scope: role-based permissions, bulk invite, SSO/SAML.