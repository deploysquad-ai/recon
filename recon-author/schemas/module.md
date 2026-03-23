# Schema: Module

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| type | `"module"` | auto-filled | |
| schema_version | `1` | auto-filled | |
| name | string | yes | functional subsystem name |
| status | `draft` / `active` / `archived` | yes | default: `draft` |
| belongs_to | wikilink | yes | `[[Project - <name>]]` |
| actors | list[wikilink] | no | Persona references: `[[Persona - <name>]]` |
| depends_on | list[wikilink] | no | other Modules |
| governed_by | list[wikilink] | no | Constraints and/or Decisions |
| related_to | list[wikilink] | no | other Modules |

## Body Sections

- `## Description` — What this module is responsible for. 2-4 sentences. Focus on the verb: what does it do, what does it produce, what does it accept.
- `## Responsibilities` — Bulleted list of what this module owns. Each bullet is a discrete responsibility. This is the "yes, this belongs here" checklist. 3-8 bullets.
- `## Boundaries` — What this module explicitly does not own. Prevents scope creep. Include pointer to the correct module where helpful. 2-5 bullets.

## Writing Guidance

- **Description**: Read like an elevator pitch. "The Auth module handles..."
- **Responsibilities**: Start with verbs in present tense. "Validates user credentials," "Issues and refreshes JWT tokens."
- **Boundaries**: Negations with redirects. "Does not handle authorization (role checking) — that belongs to the Permissions module."

## Notes

- Modules are flat — a Module belongs to a Project only, never to another Module
- Modules are technical decomposition; Epics are product-level work streams

## Question Prompts (fallback — use only if not inferable)

1. "What is this module responsible for?"
2. "Which personas interact with it?"
3. "What does it explicitly NOT own?"
