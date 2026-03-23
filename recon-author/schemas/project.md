# Schema: Project

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| type | `"project"` | auto-filled | |
| schema_version | `1` | auto-filled | |
| name | string | yes | canonical project name |
| status | `draft` / `active` / `complete` / `archived` | yes | default: `draft` |
| description | string | yes | one-line tagline, max 120 chars |

## Body Sections

- `## Overview` — 2-5 sentence expansion of the tagline. What the project does, who it's for, why it exists. Not a restatement of `description` — the "why we're building this" paragraph.
- `## Scope` — Two sub-lists: **In scope** (what this project covers) and **Out of scope** (what it does not). Bullet format.
- `## Background` — (Optional) 1-3 sentences on origin: what triggered this project, what it replaces. Only include if non-obvious.

## Writing Guidance

- **Overview**: Declarative, present tense, no jargon. "This project enables X by doing Y, for Z audience." Write for a stakeholder seeing this for the first time.
- **Scope**: Use parallel structure. Bullets start with verbs ("Supports...", "Does not include...").
- **Background**: Past tense, factual. Keep it to 2-3 sentences max.

## Question Prompts (fallback — use only if not inferable)

1. "What is this project called?"
2. "Give me a one-line summary (under 120 characters)."
3. "What is explicitly out of scope?"
