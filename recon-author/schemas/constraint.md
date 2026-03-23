# Schema: Constraint

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| type | `"constraint"` | auto-filled | |
| schema_version | `1` | auto-filled | |
| name | string | yes | short, descriptive constraint name |
| status | `draft` / `active` / `archived` | yes | default: `active`. NO `complete` status. |
| belongs_to | wikilink | yes | `[[Project - <name>]]` |
| related_to | list[wikilink] | no | other Constraints |

## Body Sections

- `## Description` — A precise statement of what is required or prohibited, written as a rule: "All X must Y" or "No X may Z." Include one sentence on why this constraint exists (regulatory, technical, business). 2-4 sentences.
- `## Scope` — What systems, modules, features, or decisions this constraint applies to. Bullet list (3-6 items). Include "does not apply to" if the boundary is non-obvious.
- `## Implications` — What a developer or designer must do (or not do) as a result. Actionable consequences: what choices it forecloses, what patterns it requires. 2-5 bullets.

## Writing Guidance

- **Description**: Open with the constraint rule in the imperative or declarative. "All user data must be encrypted at rest and in transit." Then one sentence of origin.
- **Scope**: List specific modules, systems, or feature categories — not vague terms like "everything."
- **Implications**: Developer-facing. "This means we cannot use X, we must implement Y."

## Question Prompts (fallback — use only if not inferable)

1. "What does this constraint require or prohibit?"
2. "What does it apply to?"
3. "What are the practical implications for developers?"
