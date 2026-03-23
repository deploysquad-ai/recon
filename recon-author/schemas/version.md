# Schema: Version

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

- `## Goal` — The outcome this version achieves. 1-3 sentences on what becomes possible after this release. Not a feature list.
- `## Scope` — Two sub-lists: **Included** (key capabilities) and **Not included** (explicitly deferred, with pointer to which version takes it if known). 4-10 bullets total.
- `## Exit Criteria` — Conditions that define "done" for this version. Quality bar, completeness conditions, or sign-offs required. 2-5 bullets.

## Writing Guidance

- **Goal**: Product announcement framing. "With MVP, developers can build and test a full project graph end-to-end."
- **Scope / Included**: Name capabilities, not tasks. "Context bundle generation from any Feature node."
- **Scope / Not included**: "Embedding-based link suggestions (deferred to v1.0)."
- **Exit Criteria**: Independently verifiable. "All 10 node types can be created via create_node" — not "the system works."

## Notes

- Versions are authored late — after Features, User Stories, and Epics exist
- After Version creation, a version assignment pass assigns `target_version` to relevant nodes

## Question Prompts (fallback — use only if not inferable)

1. "What should this version be called?"
2. "What order does it come in? (e.g. MVP = 1)"
3. "Is there a target release date?"
4. "What are the exit criteria for shipping?"
