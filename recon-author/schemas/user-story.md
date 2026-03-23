# Schema: User Story

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

- `## Story` — The Connextra sentence: "As a [Persona], I want [goal], so that [benefit]." Exactly one sentence.
- `## Acceptance Criteria` — Testable conditions for "done." Markdown checklist, 2-5 items. Each item is one observable outcome. Plain English is acceptable; Gherkin (Given/When/Then) is preferred when the story will go to QA.
- `## Rationale` — Why this story exists. 2-4 sentences. Not a restatement of the benefit clause — add context about what problem prompted this story.
- `## Notes` — (Optional) Edge cases, known constraints, or open questions. Delete if empty.

## Writing Guidance

- **Story**: One sentence, one pass. If you need more than one sentence, you have two stories.
- **Acceptance Criteria**: Each criterion must be falsifiable. "The user can log in" is not a criterion. "Given valid credentials, when the user submits the login form, the system returns a JWT token and a 200 response" is. Cap at 5; more means the story should be split.
- **Rationale**: Write for a future reader with no context. Answer: "Why did the team write this story?"
- **Notes**: Short, direct, flagged with the open question or constraint.

## Notes

- Non-functional requirements should be modeled as Constraint nodes, not User Stories
- User Stories capture user-facing behavior only
- Acceptance criteria are in the body, not frontmatter

## Question Prompts (fallback — use only if not inferable)

1. "Who is this story for?" (maps to actors)
2. "What do they want to do?"
3. "How do you know it is done?" (maps to Acceptance Criteria body section)
