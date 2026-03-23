# Schema: Feature

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| type | `"feature"` | auto-filled | |
| schema_version | `1` | auto-filled | |
| name | string | yes | feature name |
| status | `draft` / `active` / `complete` / `archived` | yes | default: `draft` |
| belongs_to | wikilink | yes | `[[Module - <name>]]` |
| implements | list[wikilink] | yes, min 1 | User Story references: `[[User Story - <name>]]` |
| actors | list[wikilink] | no | Persona references: `[[Persona - <name>]]` |
| supports | list[wikilink] | no | Goal references: `[[Goal - <name>]]` |
| target_version | wikilink | no | `[[Version - <name>]]` — assigned during version pass |
| epic | wikilink | no | `[[Epic - <name>]]` — product-level grouping |
| depends_on | list[wikilink] | no | Features or Modules |
| governed_by | list[wikilink] | no | Constraints and/or Decisions |
| related_to | list[wikilink] | no | other Features |

## Body Sections

- `## Description` — What this feature does, stated as user-facing behavior. 1-3 sentences. "This feature allows [actor] to [action] so that [outcome]."
- `## Scope` — Two sub-lists: **In scope** and **Out of scope**. Even one "out of scope" item saves developer confusion. Use the out-of-scope list for tempting extensions deliberately deferred.
- `## Approach` — (Optional) Rough solution sketch. Not a technical design — just enough to signal constraints on how it should be built. Brief and flagged as preliminary.
- `## Open Questions` — (Optional) Unresolved decisions or unknowns. Each item should be a question, not a statement.

## Writing Guidance

- **Description**: Write for a developer at 9am, no prior context. No implementation details. Active voice about user behavior.
- **Scope**: Be blunt. "Out of scope: password reset." If unsure, it goes in Open Questions.
- **Approach**: A constraint, not a prescription. "Should use the existing session store" not "implement using Redis with 24h TTL."
- **Open Questions**: Literal questions. "Should the session expire after inactivity or absolute time?"

## Notes

- The Feature body is managed by spec-kit after handoff. Keep it brief during graph authoring.
- Acceptance criteria live on the User Story nodes this Feature implements.
- If no User Story exists yet, create a stub User Story with `status: draft` first.

## Question Prompts (fallback — use only if not inferable)

1. "What does this feature do?"
2. "Which user story does it implement?"
3. "What is explicitly out of scope?"
