# Schema: Goal

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

- `## Description` — What this goal aims to achieve and the strategic intent behind it. 2-4 sentences. Not a restatement of the name — explain why this goal matters to the project.
- `## Success Criteria` — Measurable conditions for "achieved." Bulleted list, 2-5 items. Each bullet should be independently verifiable. SMART format preferred: specific, measurable, time-bound where possible.

## Writing Guidance

- **Description**: One sentence stating the goal plainly, then one or two explaining the strategic rationale. Do not list features or tasks — those belong on Features and Epics.
- **Success Criteria**: Each bullet must be falsifiable. "Users can complete X without Y" rather than "Users are happy with Z."

## Question Prompts (fallback — use only if not inferable)

1. "What is this goal trying to achieve?"
2. "How would you know it has been achieved?"
