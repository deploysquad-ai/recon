# Schema: User Story

> Goal: each User Story captures one user-facing behavior precisely enough that QA can write tests directly from the Acceptance Criteria and implementers know what they must build.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| type | `"user-story"` | auto-filled | |
| schema_version | `1` | auto-filled | |
| name | string | yes | short story name |
| status | `draft` / `active` / `complete` / `archived` | yes | default: `draft` |
| belongs_to | wikilink | yes | `[[Module - <name>]]` |
| actors | list[wikilink] | yes, min 1 | Persona references: `[[Persona - <name>]]` |
| supports | list[wikilink] | no | Goal references: `[[Goal - <name>]]` |
| target_version | wikilink | no | `[[Version - <name>]]` — assigned during version pass, not authoring |
| governed_by | list[wikilink] | no | Constraints and/or Decisions |
| related_to | list[wikilink] | no | other User Stories |

## Body Sections

- `## Story` — **REQUIRED.** The Connextra sentence: "As a [Persona], I want [goal], so that [benefit]." Exactly one sentence. If you need two, you have two stories.

- `## Acceptance Criteria` — **REQUIRED.** Markdown checklist, 3-7 items. Each criterion is one observable outcome and must be falsifiable. Gherkin (Given/When/Then) is preferred when the story will go to QA; plain English is acceptable otherwise. Cover the happy path *and* at least one failure or edge case.

- `## Rationale` — **REQUIRED.** 2-4 sentences. Why this story exists — what problem or moment prompted it. Write for a future reader with no context.

- `## Preconditions` — **OPTIONAL but preferred.** State, permissions, data, or feature flags that must already be true before the story applies. One bullet each.

- `## Interaction Flow` — **OPTIONAL.** Short step-by-step sketch of the user's interaction (4-8 steps) for stories with non-trivial flow. Useful for features with multi-step UIs or back-and-forth protocols.

- `## Edge Cases` — **OPTIONAL but preferred.** 2-4 bullets on known tricky situations: empty states, concurrent actions, partial failure, permission boundaries. Each becomes a test.

- `## Notes` — **OPTIONAL.** Open questions, linked Decisions, or temporary constraints. Omit if empty.

## Writing Guidance

- **Story**: One sentence, one pass.
- **Acceptance Criteria**: Each criterion must be falsifiable. "The user can log in" fails the test; "Given valid credentials, when the user submits the form, the system returns a JWT and a 200 response" passes it.
- **Rationale**: Answer "why did the team write this story?" — not a restatement of the benefit clause.
- **Preconditions**: State the world before the trigger. "User has verified their email."
- **Edge Cases**: Name the situation concretely. "User tries to submit twice within the network round-trip" beats "network issues."

## Notes

- Non-functional requirements belong on Constraint nodes, not User Stories.
- User Stories capture user-facing behavior only.
- Acceptance criteria live in the body, not frontmatter.

## Question Prompts (fallback — use only if not inferable)

1. "Who is this story for?" (maps to actors)
2. "What do they want to do, and why?" (Story + Rationale)
3. "How do you know it is done?" (Acceptance Criteria)
4. "What must be true before the story applies?" (Preconditions)
5. "What edge cases or failure paths matter?"
