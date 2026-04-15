# Schema: Goal

> Goal: each Goal node expresses strategic intent precisely enough that Epics and Features can trace back to it, and Success Criteria are concrete enough to test against.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| type | `"goal"` | auto-filled | |
| schema_version | `1` | auto-filled | |
| name | string | yes | short goal name |
| status | `draft` / `active` / `complete` / `archived` | yes | default: `draft` |
| belongs_to | wikilink | yes | `[[Project - <name>]]` |
| related_to | list[wikilink] | no | other Goals or any node type |

## Body Sections

- `## Description` — **REQUIRED.** 2-4 sentences. One sentence stating the goal plainly, then the strategic rationale: what changes in the world (for users, the business, the system) once this goal is achieved. Do not list features or tasks.

- `## Success Criteria` — **REQUIRED.** Bulleted list, 2-5 items. Each criterion is falsifiable and independently verifiable. Prefer SMART format: specific, measurable, and (where relevant) time-bound. Name the observable, not the feeling.

- `## Non-Goals` — **OPTIONAL but preferred.** 2-4 bullets naming outcomes this goal deliberately does *not* pursue, especially ones a reader might assume. Prevents scope inflation during downstream authoring.

- `## Metrics` — **OPTIONAL.** Quantitative signals that track progress. Name the metric, source, and target. Different from Success Criteria: criteria define "done"; metrics track "how close."

- `## Rationale` — **OPTIONAL.** 2-4 sentences on why this goal is in the project at all — what happens if it is dropped, and why it outranks alternatives competing for the same resources.

## Writing Guidance

- **Description**: Outcome-level, not task-level. "Users can author a complete project graph in under 30 minutes" — not "we ship a CLI."
- **Success Criteria**: Each bullet must pass the falsifiability test — a reviewer can point at the system and say yes or no.
- **Non-Goals**: Write as decisions, not omissions. "This goal is not about improving generation quality — that is tracked separately."
- **Metrics**: Numbers and sources. "p95 time-to-first-node < 5 min, measured from session logs."

## Question Prompts (fallback — use only if not inferable)

1. "What is this goal trying to achieve, and why does it matter?"
2. "How would you know it has been achieved? (success criteria)"
3. "What is this goal explicitly *not* about?"
