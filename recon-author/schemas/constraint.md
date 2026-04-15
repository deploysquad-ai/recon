# Schema: Constraint

> Goal: each Constraint is a hard rule the project must honor. Detailed enough that a downstream designer can tell whether a proposed Decision or Feature violates it.

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

- `## Description` — **REQUIRED.** 2-4 sentences. Open with the rule in imperative or declarative form ("All X must Y" / "No X may Z"). Follow with one or two sentences on origin and why it exists (regulatory, technical, business, contractual).

- `## Scope` — **REQUIRED unless the constraint is unambiguously project-wide.** 3-6 bullets naming the systems, modules, features, or decision categories this applies to. Include "does not apply to" when the boundary is non-obvious. Avoid vague terms like "everything."

- `## Implications` — **REQUIRED.** 3-6 bullets of actionable developer- or designer-facing consequences. What this forecloses, what patterns it requires, what extra work it triggers. A reviewer should be able to use it as a checklist when judging a design.

- `## Verification` — **OPTIONAL but preferred.** How compliance is demonstrated: test, review gate, lint rule, audit, runtime check. Name the mechanism and where it lives.

- `## Rationale` — **OPTIONAL.** 2-4 sentences on the underlying reason, especially if the constraint is likely to be questioned. Cite the source (regulation, contract clause, prior incident, architectural principle).

- `## Exceptions` — **OPTIONAL.** Known carve-outs and the conditions under which they apply. Omit the section if none exist.

## Writing Guidance

- **Description**: Rule first, origin second. Present tense, declarative.
- **Scope**: Name specific modules or categories. If you find yourself writing "everything," narrow it.
- **Implications**: Developer-facing commands. "This means we cannot use X; we must implement Y."
- **Verification**: Point at the artifact. "Enforced by CI lint rule X," not "checked during review."
- **Rationale**: Quote the source where possible. Future readers will question constraints that lack this.

## Question Prompts (fallback — use only if not inferable)

1. "What does this constraint require or prohibit?"
2. "Where does it come from? (regulation, contract, architecture)"
3. "What does it apply to, and what does it not apply to?"
4. "What are the practical implications for developers?"
5. "How do we verify compliance?"
