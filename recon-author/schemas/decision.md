# Schema: Decision

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| type | `"decision"` | auto-filled | |
| schema_version | `1` | auto-filled | |
| name | string | yes | short ADR-style title |
| status | `draft` / `active` / `archived` | yes | default: `active`. NO `complete` status. |
| belongs_to | wikilink | yes | `[[Project - <name>]]` OR `[[Module - <name>]]` — exactly one |
| governed_by | list[wikilink] | no | Constraints ONLY. A Decision cannot be governed_by another Decision. |
| related_to | list[wikilink] | no | Features, other Decisions |

## Body Sections

- `## Context` — What situation or problem made this decision necessary. 2-4 sentences. Background, not justification.
- `## Decision` — The actual choice, stated plainly in 1-3 sentences. Should be readable standalone.
- `## Rationale` — Why this option over the alternatives. 3-6 sentences as connected prose.
- `## Alternatives Considered` — Options evaluated and not chosen. Short bullet or sub-header per option, with one sentence on why it was rejected.
- `## Consequences` — What this decision commits the team to. Tradeoffs, things accepted, follow-on decisions needed. 3-5 bullets. Use "Good:" and "Bad:" prefixes where helpful.

## Writing Guidance

- **Context**: Past tense, neutral observer. "At the time of this decision, the team was evaluating..."
- **Decision**: Declarative. "We will use PostgreSQL as the primary database."
- **Rationale**: Connected prose, not bullet points. This appears verbatim in CONTEXT.md.
- **Alternatives Considered**: Each alternative gets one specific rejection reason. Avoid vague "not a good fit."
- **Consequences**: Be honest about tradeoffs. This is what future engineers read when they question the decision.

## Question Prompts (fallback — use only if not inferable)

1. "What is this decision about?"
2. "Is it project-wide or specific to a module?"
3. "What alternatives were considered?"
4. "What was decided, and why?"
5. "What are the consequences or tradeoffs?"
