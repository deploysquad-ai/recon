# Schema: Epic

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

- `## Description` — What this epic delivers as a user-facing outcome. 2-4 sentences. Answer: Who benefits? What can they do after this epic ships that they could not before?
- `## Why Now` — Why this epic is prioritized in this version. 1-3 sentences connecting to a business driver, user need, or strategic constraint.
- `## Success Criteria` — How stakeholders know this epic is done. 2-4 measurable, business-level items. Not a duplicate of user story acceptance criteria — these are rollup criteria.
- `## Out of Scope` — (Optional) What the team agreed is not in this epic. Prevents scope creep.

## Writing Guidance

- **Description**: Write for a product stakeholder, not a developer. "After this epic, [who] can [do what]." Avoid naming specific technologies.
- **Why Now**: Two or three sentences for a quarterly planning audience. "We are building authentication before payments because no payment flow can be trusted without identity."
- **Success Criteria**: Stakeholder-level outcomes. "A logged-out user cannot access any protected endpoint" — not "login works."
- **Out of Scope**: Write as decisions, not omissions. "Password reset is deferred to v1.0" rather than "we didn't include password reset."

## Notes

- Epics group related Features into product-level bodies of work
- Features reference their Epic via the optional `epic` field
- Modules are technical decomposition; Epics are product-level work streams

## Question Prompts (fallback — use only if not inferable)

1. "What body of work does this epic represent?"
2. "Which goals does it advance?"
3. "Why is this being built now?"
