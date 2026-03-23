# Schema: Persona

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| type | `"persona"` | auto-filled | |
| schema_version | `1` | auto-filled | |
| name | string | yes | who or what this persona is |
| status | `draft` / `active` / `archived` | yes | default: `active`. NO `complete` status. |
| belongs_to | wikilink | yes | `[[Project - <name>]]` |
| related_to | list[wikilink] | no | other Personas (e.g. Admin is a type of User) |

## Body Sections

- `## Description` — Who this persona is in 2-3 sentences. Their role, their relationship to the product, what they do day-to-day. Do not put goals here.
- `## Background` — Technical proficiency, relevant experience, tools they already use, how they currently solve the problem. 3-5 sentences.
- `## Goals` — What this persona is trying to achieve. Bulleted list (3-5 items) followed by 1-2 sentences elaborating the most important goal. Distinguish outcome goals ("complete the report without errors") from experience goals ("feel confident, not confused").
- `## Pain Points` — Current frustrations. 3-5 bullet points. Each should be specific and behavioral, traceable to a moment in their workflow.
- `## Scenarios` — (Optional) One brief paragraph (4-6 sentences) describing this persona in a representative situation using the product.

## Writing Guidance

- **Description**: Third person, present tense. "Sarah is a mid-level analyst..." Concrete, specific, one person.
- **Background**: Skills-and-context inventory. Avoid generic ("tech-savvy") — be specific ("uses Excel and Tableau but has never written SQL").
- **Goals**: Outcome-oriented ("ship the report by Friday") not task-oriented ("click the export button").
- **Pain Points**: "Has to copy numbers manually between two tools every Monday" is useful. "Finds the process inefficient" is not.
- **Scenarios**: Short narrative starting from a trigger. End with success or current frustration.

## Notes

- Personas are project-scoped, not module-scoped
- Referenced by Features, Modules, and User Stories via the `actors` field
- Shared personas between nodes is a strong signal for proposing links during the linking pass

## Question Prompts (fallback — use only if not inferable)

1. "Who is this persona?"
2. "What are they trying to achieve?"
3. "What frustrates them about the current way they do this?"
