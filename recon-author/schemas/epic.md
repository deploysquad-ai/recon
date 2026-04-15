# Schema: Epic

> Goal: each Epic frames a product-level body of work. Detailed enough that a planning stakeholder can see what ships, why now, what success looks like, and what's deliberately excluded.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| type | `"epic"` | auto-filled | |
| schema_version | `1` | auto-filled | |
| name | string | yes | product-level work stream name |
| status | `draft` / `active` / `archived` | yes | default: `draft`. NO `complete` status. |
| belongs_to | wikilink | yes | `[[Module - <name>]]` |
| target_version | wikilink | no | `[[Version - <name>]]` — assigned during version pass |
| supports | list[wikilink] | no | Goal references: `[[Goal - <name>]]` |
| related_to | list[wikilink] | no | other Epics |

## Body Sections

- `## Description` — **REQUIRED.** 2-5 sentences. What this epic delivers as a user-facing outcome. Answer: who benefits, and what can they do after this ships that they could not before? Write for a product stakeholder, not a developer.

- `## Why Now` — **REQUIRED.** 2-4 sentences connecting this epic to a business driver, user need, dependency, or strategic window. Answers: why this epic *this* version and not later.

- `## Success Criteria` — **REQUIRED.** 2-5 bullets of stakeholder-level, measurable outcomes. Rollup criteria — not a duplicate of per-User-Story acceptance criteria. Each bullet names an observable at the product level.

- `## Scope` — **REQUIRED.** Two sub-lists: **In scope** (the Features and outcomes covered) and **Out of scope** (deliberately deferred — ideally with a pointer to the version or epic that will own it).

- `## Dependencies` — **OPTIONAL but preferred.** Epics, Features, Modules, or external teams this epic depends on. One line each explaining the dependency and what becomes blocked without it.

- `## Risks` — **OPTIONAL.** 2-4 bullets on what could cause this epic to slip, shrink, or fail. Name the risk and the mitigation or trigger. Honest risks beat optimistic timelines.

- `## Stakeholders` — **OPTIONAL.** Sponsor, approvers, primary users (link to Personas). Useful when the epic spans teams.

## Writing Guidance

- **Description**: Product framing. "After this epic, [who] can [do what]." Avoid specific technologies.
- **Why Now**: Planning-audience voice. "We are building authentication before payments because no payment flow can be trusted without identity."
- **Success Criteria**: Observable at the product level. "A logged-out user cannot access any protected endpoint" — not "login works."
- **Out of scope**: Decisions, not omissions. "Password reset is deferred to v1.0."
- **Risks**: Name the mechanism of failure, not the feeling. "Vendor X's rate limit blocks peak hour usage" beats "might be slow."

## Notes

- Epics group related Features into product-level bodies of work.
- Features reference their Epic via the optional `epic` field.
- Modules are technical decomposition; Epics are product-level work streams.

## Question Prompts (fallback — use only if not inferable)

1. "What body of work does this epic represent, and who benefits?"
2. "Why is this being built now?"
3. "Which goals does it advance?"
4. "What does success look like at the stakeholder level?"
5. "What is explicitly out of scope?"
6. "What are the biggest risks to shipping this?"
