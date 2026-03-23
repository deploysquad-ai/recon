---
type: feature
schema_version: 1
name: JWT Login
status: draft
belongs_to: "[[Module - Auth]]"
implements:
  - "[[User Story - Login]]"
actors:
  - "[[Persona - Developer]]"
supports:
  - "[[Goal - Fast Delivery]]"
target_version: "[[Version - MVP]]"
epic: "[[Epic - Authentication]]"
governed_by:
  - "[[Constraint - MIT License]]"
depends_on: []
related_to: []
---

## Description

JWT-based login endpoint for developer authentication.

## Scope

- POST /auth/login endpoint
- JWT token generation
- Credential validation
