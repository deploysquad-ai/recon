---
type: decision
schema_version: 1
name: Use JWT
status: active
belongs_to: "[[Module - Auth]]"
governed_by:
  - "[[Constraint - MIT License]]"
---

## Decision

Use JWT tokens for stateless authentication.

## Rationale

JWTs are stateless, widely supported, and work well for API authentication.

## Alternatives Considered

- Session-based auth: requires server-side state
- API keys: less flexible, no expiration
