# Schema: Feature

> Goal: a Feature node must be detailed enough to hand directly to a spec-driven implementation agent (spec-kit, planner, codegen). Err toward more detail, not less.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| type | `"feature"` | auto-filled | |
| schema_version | `1` | auto-filled | |
| name | string | yes | feature name |
| status | `draft` / `active` / `complete` / `archived` | yes | default: `draft` |
| belongs_to | wikilink | yes | `[[Module - <name>]]` |
| implements | list[wikilink] | yes, min 1 | User Story references: `[[User Story - <name>]]` |
| actors | list[wikilink] | no | Persona references: `[[Persona - <name>]]` |
| supports | list[wikilink] | no | Goal references: `[[Goal - <name>]]` |
| target_version | wikilink | no | `[[Version - <name>]]` — assigned during version pass |
| epic | wikilink | no | `[[Epic - <name>]]` — product-level grouping |
| spec_path | string | no | path to the generated spec artifact. Leave blank during authoring; populated after spec-kit runs. |
| depends_on | list[wikilink] | no | Features or Modules this feature relies on |
| governed_by | list[wikilink] | no | Constraints and/or Decisions that shape this feature |
| related_to | list[wikilink] | no | other Features |

## Body Sections

Required sections are marked **REQUIRED**. Optional sections are marked **OPTIONAL** — include them whenever they add signal. For any feature expected to drive implementation, prefer including Acceptance Criteria, Interface, Errors, and Test Scenarios.

- `## Description` — **REQUIRED.** What this feature does, stated as observable behavior. 2-5 sentences. Lead with the user-facing outcome, then the surface area ("three MCP tools exposed to...", "a new CLI subcommand that..."). No implementation detail beyond the surface.

- `## Acceptance Criteria` — **REQUIRED.** Bulleted list of observable, falsifiable conditions that define "done" at the feature level. 4-10 bullets. Each bullet is one testable behavior or invariant. These roll up from (but are richer than) the acceptance criteria on child User Stories — include edge cases, terminal states, and cross-cutting invariants that individual stories don't capture.

- `## Interface` — **OPTIONAL but preferred.** The contract this feature exposes to its callers. Include:
  - **Entry points** — tool names, function signatures, CLI commands, HTTP routes, or events.
  - **Input / output shapes** — dataclasses, TypedDicts, JSON schemas, or tables of fields with types. Be concrete; prefer code blocks over prose.
  - **Contract decisions** — the non-obvious rules a caller must honor (identity, idempotency, ordering, blocking vs async, auth assumptions, trust boundary). Cross-link to governing Decision nodes via `[[Decision - <name>]]`.

- `## Data & State` — **OPTIONAL.** Any persistent or in-flight state this feature owns or mutates: tables, files, cache keys, checkpoints, queue topics. Include field-level shape for new state and note ownership vs. shared-with-X.

- `## Errors` — **OPTIONAL but preferred when the feature has a callable surface.** Enumerate observable error conditions, the structured response they produce, and the category (validation / not-found / protocol / internal). Include what information surfaces to the caller (e.g. "names the missing field", "lists known pipeline names").

- `## Test Scenarios` — **OPTIONAL but preferred.** Narrative, end-to-end scenarios a test suite must cover — one bullet per scenario. Include the happy path, each error case, idempotency/retry behavior, and any cross-turn / cross-process persistence. These are the scenarios, not the unit tests.

- `## Observability` — **OPTIONAL.** What this feature logs, metrics it emits, traces it participates in. Per-operation: level, key fields, cardinality-safe labels. Include any new alerts or dashboards.

- `## Non-Functional Requirements` — **OPTIONAL but preferred when NFRs apply.** Summarize applicable non-functional requirements inline — latency and throughput targets, availability/error-budget expectations, security posture, compliance obligations, accessibility, internationalization. When the requirement is already captured in a `governed_by` Constraint, restate it briefly here (one line) so a spec-kit / codegen agent working from this node alone does not miss it. Cross-link to the Constraint by wikilink.

- `## Out of Scope` — **REQUIRED.** Flat bulleted list of what this feature explicitly does *not* cover: deferred extensions, adjacent features owned elsewhere, tempting-but-rejected variations, and capabilities a reader might otherwise assume. Out-of-scope bullets are the single highest-leverage section for preventing the implementation agent (and the LLM authoring downstream nodes) from drifting into adjacent territory. Be blunt and specific; list the concrete thing, not a category. If it could plausibly be built into this feature and a reader might argue for it, it belongs here.

- `## Approach` — **OPTIONAL.** Preliminary solution sketch — enough to constrain implementation without prescribing it. Name the substrate ("uses LangGraph StateGraph"), the pattern ("blocking call wrapped in MCP tool"), or the storage ("reuses the existing session store"). Mark as preliminary; the implementing agent may adapt.

- `## Dependencies` — **OPTIONAL.** Why each `depends_on` and `governed_by` link exists in one line. Gives downstream readers the reason, not just the edge.

- `## Example` — **OPTIONAL but high-value for spec-driven handoff.** A concrete worked example: one or two request/response pairs, or a CLI transcript, or a realistic flow through the feature. Use code blocks with real payload shapes. This is the single best artifact for disambiguating the spec.

- `## Open Questions` — **OPTIONAL.** Unresolved design questions. Each item is a literal question, not a statement. Promote each to a Decision node once answered.

## Writing Guidance

- **Description**: A developer at 9am with no context should know *what* this feature is and *where* it sits from these sentences alone.
- **Acceptance Criteria**: Write each bullet so a reviewer can point at the system and say "yes / no." Avoid "works correctly" — name the observable.
- **Interface**: Concrete shapes beat prose. If the surface changes, the Interface section is the first thing to update.
- **Contract decisions**: Each bullet should answer "what rule must the caller learn that they couldn't guess from the types?" — identity, retries, auth, ordering, blocking.
- **Errors**: List by triggering condition, not by exception class. "Unknown run_id on resume → structured error naming the id."
- **Test Scenarios**: Narrative ("start to completion", "duplicate resume"). Implementation agents turn these into test cases.
- **Out of Scope**: Be blunt. "Out of scope: password reset" saves a week. Name the specific thing, not the category.
- **Non-Functional Requirements**: Restate inline even if the source is a linked Constraint — a codegen agent should not have to traverse the graph to find a latency target.

## Notes

- A Feature body is the primary spec-kit handoff artifact. During graph authoring, capture as much as the conversation reveals; leave Open Questions for the rest.
- Feature-level Acceptance Criteria complement, not replace, User Story acceptance criteria. Story criteria are per-actor-goal; feature criteria cover the whole surface including invariants and error behavior.
- If no User Story exists yet, create a stub User Story (`status: draft`) before linking `implements`.
- Cross-link every non-obvious contract rule to the governing Decision — this is how future readers reconstruct why the feature behaves as it does.

## Question Prompts (fallback — use only if not inferable)

1. "What does this feature do, and what surface does it expose?"
2. "What must be true for this feature to be considered done? (acceptance criteria)"
3. "What are the inputs, outputs, and non-obvious contract rules?"
4. "What errors or terminal states must callers handle?"
5. "What test scenarios cover the happy path, errors, and edge cases?"
6. "What is explicitly out of scope?"
