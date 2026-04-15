# Schema: Version

> Goal: each Version defines a release checkpoint in enough detail that teams can plan toward it, assess readiness against it, and agree on what shipped vs. what slipped.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| type | `"version"` | auto-filled | |
| schema_version | `1` | auto-filled | |
| name | string | yes | e.g. "MVP", "v1.0", "Beta" |
| status | `draft` / `active` / `complete` / `archived` | yes | default: `draft` |
| belongs_to | wikilink | yes | `[[Project - <name>]]` |
| sequence | integer | yes | ordering within the project (1 = first). Must be >= 1. |
| target_date | string | no | `YYYY-MM-DD` format |

## Body Sections

- `## Goal` — **REQUIRED.** 2-4 sentences. The outcome this version achieves — what becomes possible, provable, or released. Product-announcement framing, not a feature list.

- `## Scope` — **REQUIRED.** Two sub-lists: **Included** (key capabilities, named as capabilities not tasks) and **Not included** (explicitly deferred, with a pointer to the receiving version where known). 5-12 bullets total.

- `## Exit Criteria` — **REQUIRED.** 3-6 bullets. Independently verifiable conditions for shipping this version: quality bars, completeness conditions, sign-offs, measurable thresholds. "All 290+ tests pass" beats "the system works."

- `## Release Gates` — **OPTIONAL but preferred for formal releases.** Approvals, reviews, or automated checks required before ship: security review, perf sign-off, docs complete, rollback plan filed. One bullet per gate with owner.

- `## Risks & Mitigations` — **OPTIONAL.** 2-4 bullets on what could cause this version to slip or ship broken, with the mitigation or trigger for each. Useful for versions with aggressive dates or external dependencies.

- `## Dependencies` — **OPTIONAL.** External teams, vendor milestones, or upstream Versions that this release depends on. Include the failure mode if the dependency misses.

- `## Rollout Plan` — **OPTIONAL.** How this version reaches users: staged rollout, feature flags, migration steps, comms plan. Include only when non-trivial.

## Writing Guidance

- **Goal**: "With MVP, developers can build and test a full project graph end-to-end." Product framing.
- **Included**: Capabilities, not tasks. "Context bundle generation from any Feature node."
- **Not included**: With redirect. "Embedding-based link suggestions — deferred to v1.0."
- **Exit Criteria**: Each bullet must be independently verifiable. Name the observable, not the feeling.
- **Release Gates**: Name the owner. Unowned gates are wishes.

## Notes

- Versions are authored late — after Features, User Stories, and Epics exist.
- After Version creation, a version assignment pass assigns `target_version` to relevant nodes.
- For early-stage "spike" or "dogfood" versions, Scope and Exit Criteria may be lighter, but do not skip them — the act of writing them exposes hidden assumptions.

## Question Prompts (fallback — use only if not inferable)

1. "What should this version be called, and what sequence number?"
2. "What is the target release date, if any?"
3. "What becomes possible after this version ships? (Goal)"
4. "What is included, and what is explicitly deferred?"
5. "What are the exit criteria for shipping?"
6. "What approvals or gates are required?"
