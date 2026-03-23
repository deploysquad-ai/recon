---
type: user-story
schema_version: 1
name: Login
status: draft
belongs_to: "[[Module - Auth]]"
actors:
  - "[[Persona - Developer]]"
supports:
  - "[[Goal - Fast Delivery]]"
target_version: "[[Version - MVP]]"
---

## Story

As a Developer, I want to log in with my credentials, so that I can access protected API endpoints.

## Acceptance Criteria

- Developer can authenticate with email and password
- Returns a valid JWT token
- Invalid credentials return 401
