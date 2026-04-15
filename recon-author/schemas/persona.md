# Schema: Persona

> Goal: each Persona grounds features and user stories in a specific person — detailed enough that designers, PMs, and implementers can simulate their behavior and reactions.

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

- `## Description` — **REQUIRED.** 2-4 sentences. Role, relationship to the product, what they do day-to-day, and the values or constraints that shape their behavior. One specific person, not a class.

- `## Background` — **REQUIRED for external / user-facing personas; OPTIONAL for internal stakeholders.** Technical proficiency, relevant experience, tools they already use, how they currently solve the problem. 3-5 sentences with specifics (named tools, seniority, domain vocabulary).

- `## Goals` — **REQUIRED for external personas; OPTIONAL for internal.** Bulleted list (3-5 items) followed by 1-2 sentences on the most important goal. Distinguish outcome goals ("ship the report by Friday") from experience goals ("feel confident, not confused").

- `## Pain Points` — **REQUIRED for external personas; OPTIONAL for internal.** 3-5 bullets. Each specific and behavioral, traceable to a moment in their workflow. "Copies numbers between two tools every Monday" — not "finds it inefficient."

- `## Decision Authority` — **OPTIONAL.** What this persona can decide unilaterally, what needs approval, who blocks them. Useful for personas that drive procurement, compliance, or cross-team coordination.

- `## Scenarios` — **OPTIONAL but preferred.** One or two short narratives (4-6 sentences each) of this persona in a representative situation. Start from a trigger; end with success or frustration. These feed directly into User Story authoring.

- `## Success Looks Like` — **OPTIONAL.** 2-3 bullets describing observable behaviors after the project ships — not sentiments.

## Writing Guidance

- **Description**: Third person, present tense. Concrete. "Sarah is a mid-level analyst on the pricing team..."
- **Background**: Specifics beat adjectives. "Uses Excel and Tableau, has never written SQL" beats "tech-savvy."
- **Goals**: Outcome-oriented, not task-oriented.
- **Pain Points**: Each must be traceable to a moment. If you can't say when it happens, it's not a pain point yet.
- **Scenarios**: Trigger → steps → outcome. These become seeds for User Stories.

## Notes

- Personas are project-scoped, not module-scoped.
- Referenced by Features, Modules, and User Stories via the `actors` field.
- Shared personas across nodes are a strong signal for link suggestions in Phase 2.

## Question Prompts (fallback — use only if not inferable)

1. "Who is this persona, and what is their role?"
2. "What tools and skills do they bring to this work?"
3. "What are they trying to achieve?"
4. "What frustrates them about the current state?"
5. "What would success feel like for them?"
