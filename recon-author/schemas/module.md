# Schema: Module

> Goal: each Module defines a bounded technical subsystem. Detailed enough that Features belonging to it inherit clear ownership, interfaces, and neighbors.

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

- `## Description` — **REQUIRED.** 2-4 sentences. What this module does, what it produces, what it accepts. Elevator pitch — a stakeholder seeing it for the first time should know its role in the system.

- `## Responsibilities` — **REQUIRED.** 3-8 bullets of what this module owns. Each bullet is a discrete responsibility starting with a present-tense verb. The "yes, this belongs here" checklist.

- `## Boundaries` — **REQUIRED.** 2-5 bullets on what this module explicitly does *not* own, with a redirect to the owning module where possible. Prevents scope creep and cross-module leakage.

- `## Interfaces` — **OPTIONAL but preferred.** The contracts this module exposes to the rest of the system: public APIs, tool names, events emitted, queues published to, database tables owned. Keep the listing concrete — signatures or field shapes beat prose.

- `## Data & State` — **OPTIONAL.** Persistent state this module owns (tables, files, checkpoints) and in-flight state it holds (caches, sessions). Ownership matters more than schema detail at the module level.

- `## Dependencies` — **OPTIONAL.** One line per `depends_on` and `governed_by` link explaining *why* the dependency exists. Gives reviewers reasons, not just edges.

- `## Operational Notes` — **OPTIONAL.** Deployment shape, scaling characteristics, failure modes, observability hooks. Include when the module has non-trivial runtime behavior.

## Writing Guidance

- **Description**: Elevator pitch. "The Pipeline Engine module builds, runs, and checkpoints StateGraphs..."
- **Responsibilities**: Present-tense verbs. Each bullet is falsifiable at review — "owns X" or "does not."
- **Boundaries**: Negation with a redirect. "Does not speak MCP — the MCP Server module adapts it."
- **Interfaces**: Name the concrete surface. If it changes, this is the first section to update.
- **Dependencies**: Explain the *why*. Edges without rationale rot fastest.

## Notes

- Modules are flat — a Module belongs to a Project only, never to another Module.
- Modules are technical decomposition; Epics are product-level work streams.

## Question Prompts (fallback — use only if not inferable)

1. "What is this module responsible for?"
2. "What interfaces does it expose?"
3. "Which personas interact with it?"
4. "What does it explicitly NOT own, and who owns that?"
5. "What does it depend on, and why?"
