# Schema: Decision

> Goal: each Decision is an ADR-style record future engineers can read standalone and reconstruct the reasoning, including what was rejected and why.

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

- `## Context` — **REQUIRED.** 2-4 sentences. What situation or problem forced this decision. Neutral background, not justification. Include the forces in tension (performance vs. simplicity, speed vs. correctness, etc.).

- `## Decision` — **REQUIRED.** The actual choice in 1-3 sentences. Must be readable standalone — a reader who jumps here should understand the commitment without reading Context.

- `## Rationale` — **REQUIRED.** 3-6 sentences of connected prose on why this option over the alternatives. This appears verbatim in CONTEXT.md. Cite the governing Constraints by wikilink where they were decisive. (Note: `governed_by` accepts Constraints only — recon-core rejects Decision→Decision governance. If another Decision influenced this one, link it via `related_to` instead and name it in the Rationale.)

- `## Alternatives Considered` — **REQUIRED.** Each option gets a sub-bullet or sub-header with a one-sentence rejection reason. Avoid vague "not a good fit" — name the specific property that failed. Include "do nothing" when it was a serious option.

- `## Consequences` — **REQUIRED.** 3-6 bullets on what this decision commits the team to: tradeoffs accepted, follow-on work triggered, capabilities foreclosed. Use **Good:** and **Bad:** prefixes where helpful. Be honest about the Bad — this is what engineers read when they question the decision.

- `## Follow-ups` — **OPTIONAL.** Downstream Decisions, Features, or Constraints this one implies or requires. Cross-link where the node already exists.

- `## Revisit Triggers` — **OPTIONAL.** Conditions under which this decision should be reopened (scale thresholds, new vendor availability, regulatory change). One bullet per trigger.

## Writing Guidance

- **Context**: Past tense, neutral observer. "At the time of this decision, the team was evaluating..."
- **Decision**: Declarative present or future. "We will use PostgreSQL as the primary database."
- **Rationale**: Connected prose, not bullet points. Prose signals thought; bullets signal avoidance.
- **Alternatives Considered**: Specific rejection reason per alternative. "Rejected DynamoDB: no native support for the relational joins the reporting module requires."
- **Consequences**: Balanced — engineers do not trust a decision without acknowledged downsides.

## Question Prompts (fallback — use only if not inferable)

1. "What is this decision about, and what forced it?"
2. "Is it project-wide or specific to a module?"
3. "What alternatives were considered, and why was each rejected?"
4. "What was decided, and why that option?"
5. "What are the consequences — good and bad?"
6. "Under what conditions should we reopen this decision?"
