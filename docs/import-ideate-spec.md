# Spec: `/recon.import-ideate`

Bridge skill that turns a completed Ideate session into a fully-populated Recon project graph at the project root.

> **Note on backwards compatibility:** Recon is pre-1.0 and we are explicitly **not** preserving backwards compatibility. If a clean design needs `recon-core` changes, we make them. Existing user vaults are not protected. Track breaking changes in `CHANGELOG.md`.

---

## 1. Goal

Let a user run a single command after `/ideate.doc` and end up with a Recon graph in the same project directory that mirrors the ideation session — Project, Goals, Personas, Constraints, Modules, Decisions, plus inferred Epics and User Stories and the Features the user authored.

The skill is an LLM agent. It reads ideate's artifacts as natural-language context, reasons about how each one maps to a Recon node type, and calls `recon-core` MCP tools to write validated nodes. No regex, no parser, no intermediate JSON — Claude is the bridge. Recon-core's Pydantic + JSON Schema is the contract.

---

## 2. Scope

**In scope (v1)**
- One-shot import from a single `.ideate/` session in the current working directory.
- All ideate artifact types → Recon node types, plus inferred Epics and User Stories.
- Auto-stub of the Project node from `session.md`'s elevator pitch.
- Per-node duplicate-handling prompt.
- Resume after partial failure via an import-state sidecar.
- Post-import similarity pass: `embed_nodes_tool` → `find_similar_tool` → propose `related_to`.
- Final `resolve_links_tool` + `build_index_tool`.

**Out of scope (v1)**
- Watch / sync mode (re-run the skill instead).
- Reverse direction (Recon → Ideate).
- Multi-project per cwd. **One project per directory.** A second import in the same cwd that targets a different project name is hard-refused with a clear error.
- Version nodes (Recon's `Version` is for releases, absent from ideation).
- `--dry-run` (the plan-then-confirm step in §6.4 already provides this).

---

## 3. Inputs

| Source | Files |
|---|---|
| Ideate session | `.ideate/session.md`, `.ideate/main.md`, `.ideate/artifacts/*.md`, `.ideate/output/*.md` (if present) |
| Recon vault | **The resolved project root** (`git rev-parse --show-toplevel || pwd`). The skill `cd`s there before any MCP write. The project root IS the vault AND IS the project — flat layout, no subfolder. |
| Resume state | `.ideate/recon-import-state.json` (created by this skill on first run, consulted on re-runs) |
| User | Project name confirmation, duplicate-handling decisions, Epic/User-Story confirmation, similarity-link confirmations |

---

## 4. Outputs

After import the project root looks like:

```
<project>/
  .ideate/                          ← ideate session (hidden)
    recon-import-state.json         ← resume sidecar (this skill)
  .graph/
    index.json                      ← recon graph index
  Project - <name>.md               ← Project node at root
  goals/
  personas/
  constraints/
  modules/
  decisions/
  user-stories/
  epics/
  features/
  …user's source / docs / etc.…
```

This **does** mean `goals/`, `features/`, etc. sit directly alongside the user's source code. The skill's final summary prints a `.gitignore` hint so the user can decide whether to commit the graph or ignore it. (See §10 for the hint text.)

The user points Obsidian at the project root once and sees `.ideate/` plus the recon graph alongside their code.

---

## 5. Skill Location

`recon/plugin/recon-plugin/skills/recon-import-ideate/SKILL.md`

Slash command: `/recon.import-ideate`

Lives in the recon plugin (not ideate) because the destination owns the schema and the MCP tools.

---

## 6. Flow

### 6.1 Preflight

- Resolve **project root**: walk up from cwd to the nearest `.git/` (via `git rev-parse --show-toplevel`); if none, use cwd. All vault writes target the project root, not the literal cwd. The skill `cd`s there before invoking MCP tools.
- If `.ideate/` is missing at the project root → exit with a clear message ("Run `/ideate` first").
- Call `configure_vault_tool(vault_path=<project_root>)`. In-memory only — do **not** write `VAULT_PATH` to `~/.claude/settings.json`. No prompt — the vault is always the project root (see `project-local-vault-spec.md` §3 for the shared preflight logic and §4 for why we don't persist).
- **Single-project guard:** scan project root for an existing `Project - *.md`. If present, strip the `<project_root>/` prefix to get a vault-relative path before calling `get_node_tool` (the tool resolves paths against the configured project dir; absolute paths will fail). If its name does not match the imported session's project name → hard-refuse with: "This directory already hosts project `<X>`. v1 supports one project per directory. Either rename the existing Project node or run from a different directory." Exit.

### 6.2 Load context

Read `session.md`, `main.md`, every file in `.ideate/artifacts/`, and `.ideate/output/*.md` if present. Read `.ideate/recon-import-state.json` if it exists (resume mode). `.ideate/branches/*.md` are **not** read — they are pre-merge thread logs whose ratified conclusions already land in `main.md` and `artifacts/`. Treating them as inputs would resurrect abandoned ideas.

### 6.3 Reason about the graph

Produce a single plan covering:
- **Project (one)** — name, description, status. Stubbed from elevator pitch in `session.md`. **If `.ideate/output/*.md` exists, read the most recent file and pass its contents (minus YAML frontmatter, if any) as `body_sections={"Session Brief": "<contents>"}` to `create_node_tool` (bare key — the writer prepends `##`). Cap the inlined excerpt at the first 20KB; if longer, append `> _Truncated. Full document at .ideate/output/<name>.md_`. Skip if the file is empty.** User confirms or edits the name in §6.4.
- **Goals, Personas, Constraints, Modules, Decisions, Features** — directly mapped from artifacts.
- **Epics** — clusters of Features that share a Goal. One Epic per cluster.
- **User Stories** — **one per Feature × primary Persona**. The "primary persona" is the persona most referenced in that Feature's artifact body. No combinatorial Persona×Goal×Feature explosion.
- **Stub parents** — if a Feature/Decision references a Module/Persona/Goal that doesn't exist in the session, queue a `status: draft` stub so the wikilink resolves.

### 6.4 Show the plan

Compact table grouped by type, with absolute target paths so the user sees exactly what lands where:

```
Project       <project_root>/Project - Auth Refactor.md
Goals (3)     <project_root>/goals/Goal - Reduce login friction.md
              ...
Personas (2)  ...
Features (5)  <project_root>/features/Feature - SSO via Google.md
              ...
Epics (2)     [inferred] <project_root>/epics/Epic - Federated identity.md
User Stories  [inferred] <project_root>/user-stories/User Story - SSO via Google.md
   (5)        ...
Stubs (1)     [missing parent] <project_root>/modules/Module - Token store.md  status: draft
```

Ask: `confirm / edit / cancel`. On `cancel`, exit cleanly (no writes). On `edit`, accept user edits to the project name and let them remove inferred Epics/User Stories before proceeding.

### 6.5 Check for duplicates

Call `list_nodes_tool()`. For each planned node colliding with an existing node by `(type, name)`: prompt `skip / update / rename`. No "apply to all" shortcut — per-node prompts only in v1.

### 6.6 Create nodes in dependency order

```
Project → Goals → Personas → Constraints → Modules → Decisions
       → User Stories → Epics → Features
```

For each node:

1. Call `create_node_tool(node_type, data, body_sections)`.
2. On schema validation error → fix the offending field based on the error message and retry. Up to 3 attempts.
3. **On 4th failure (unrecoverable):** write the node with whatever frontmatter passes validation and `status: draft`, append the failure to import-state with the error, and **continue**. Do not abort the whole run. (Aborting cascades into broken wikilinks for every later node.)
4. Append `{artifact_path, node_path, status: created|draft|failed, errors: [...]}` to `.ideate/recon-import-state.json` after each node.

On re-run: skip artifacts whose import-state entry is `created`. Re-attempt `draft` and `failed` entries.

### 6.7 Similarity pass

1. Check for `GEMINI_API_KEY` in env. If absent → print one-line notice ("Skipping similarity pass — no `GEMINI_API_KEY` configured") and proceed to §6.8.
2. Call `embed_nodes_tool()` once. **Required prerequisite for `find_similar_tool`.**
3. For every newly-created node whose type supports `related_to`:
   - Call `find_similar_tool(node_path=<vault-relative path>, top_k=5, threshold=0.75)`.
   - Note: signature is `(node_path, top_k, threshold)`. No `project_dir` param.
4. Batch the proposed links into a single confirmation table for the user (`accept all / accept some / skip`).
5. Write accepted links via `update_node_tool(file_path, {"related_to": merged})`. `update_node` does a shallow dict spread (`{**existing, **updates}`), so list fields are **replaced**, not appended. The skill must read-union-write: call `get_node_tool` first, union the existing `related_to` with the new entries (dedupe, preserve order), then pass the merged list to `update_node_tool`.

### 6.8 Finalize

1. `resolve_links_tool()` → list any broken wikilinks; surface to user.
2. `build_index_tool()` → rebuild `.graph/index.json`.

### 6.9 Summary

Print:
- Counts by type (created / drafted / failed).
- The project root path.
- Any `status: draft` nodes (with reason: "ideate marked draft" or "schema validation failed after retries").
- A `.gitignore` hint:
  > "The recon graph now lives at the project root. To keep it out of source control, add to `.gitignore`:
  > ```
  > /Project - *.md
  > /goals/  /personas/  /constraints/  /modules/  /decisions/
  > /user-stories/  /epics/  /features/
  > /.graph/
  > ```
  > To track the graph alongside code, do nothing."

---

## 7. Translation Contract

The agent decides the mapping. These are *defaults*, not hard rules — Claude may deviate when an artifact clearly signals a different fit, and surfaces those deviations in the §6.4 plan.

**Bounded deviations.** A deviation must remap to another row in the table below — never invent a new node type. Reclassifications that change parent constraints (e.g., a `Feature` artifact reclassified as a `Module`) require:
1. Calling out the reclassification explicitly in the §6.4 plan with a one-line reason.
2. Verifying that any wikilinks in the original artifact still resolve under the new type's schema (e.g., a Feature's `actors` are Personas, but a Module's `actors` are also Personas — that holds; but a Feature's `implements` references Goals, which Modules don't have).
3. If a referenced relationship is incompatible with the new type, drop it (do not silently rename) and flag the dropped link in the plan.

If the deviation cannot be made schema-clean, fall back to the default mapping and import the artifact verbatim.

| Ideate artifact | Recon node |
|---|---|
| `session.md` idea | `Project` |
| `Goal - <name>.md` | `Goal` |
| `Persona - <name>.md` | `Persona` |
| `Constraint - <name>.md` | `Constraint` |
| `Module - <name>.md` | `Module` |
| `Decision - <name>.md` | `Decision` |
| `Feature - <name>.md` | `Feature` |
| (inferred) `Epic` | clusters of Features that share a Goal |
| (inferred) `User Story` | one per Feature × primary Persona |

**Body sections.** Free-text headings from each artifact (e.g., `Problem & Value`, `Behavior`, `Open Questions`) are passed through verbatim as `body_sections={"Heading": "<contents>"}` to `create_node_tool`. **Keys are bare — do not include the `##` prefix; the writer prepends it automatically.** v1 does **not** normalize these to recon's canonical headings per type — `generate_context_tool` may produce sparser CONTEXT.md output for imported nodes than for hand-authored ones. Acceptable tradeoff for v1; users can edit headings post-import. The Project node additionally receives a `Session Brief` body section sourced from `.ideate/output/*.md` (most recent), capped at 20KB — see §6.3.

**Slug derivation.** Filenames are computed by `recon-core`'s `node_filename(type, name)` (returns `'Type - Name.md'`); wikilinks are `[[Type - Name]]`. The Project's directory tag is derived via `project_slug(name)`. There is no separate per-node slug — names are passed through verbatim with the type display prefix. The user types/edits the *display name* only.

**Status mapping.** Ideate's `Status: draft` → recon's `status: draft`. Ideate's confirmed/merged artifacts → `status: active` (or whichever is the type's default-active status — Personas/Constraints/Epics use `NoCompleteStatus`).

---

## 8. Resolved Design Decisions

- **No backwards compatibility.** Recon-core is pre-1.0; break it when needed.
- **Translation engine:** LLM agent, no parser. Recon-core validation is the backstop.
- **Vault layout:** one project per cwd. Flat — `Project - X.md` and type folders live directly at the project root. Explicitly accepted tradeoff: clutters the repo root; `.gitignore` hint mitigates.
- **Project root resolution:** git toplevel if present, else cwd.
- **Missing types:** auto-stub Project; infer Epics (Feature clusters); infer User Stories as one-per-Feature × primary Persona. No combinatorial inference.
- **Idempotency / resume:** `.ideate/recon-import-state.json` sidecar. Per-node prompts on collision; no "apply to all" shortcut.
- **Schema-failure recovery:** 3 retries, then write as `status: draft`, log to import-state, continue. Never abort mid-run.
- **Similarity pass:** mandatory `embed_nodes_tool()` first; gracefully skip if `GEMINI_API_KEY` missing. Threshold default `0.75`, hidden from user.
- **Vault preflight:** silent auto-config to project root on every run — no prompts, no marker file, no persisted `VAULT_PATH` (in-memory `configure_vault_tool` is the single source of truth). (Single-mode vault per `project-local-vault-spec.md`.)
- **Branch logs:** not consumed by import — `main.md` and `artifacts/` are the post-merge source of truth.
- **Plugin home:** `recon-plugin`.

---

## 9. Acceptance Criteria

1. Running `/recon.import-ideate` in a directory with a complete ideate session produces a Recon graph at the project root with at least one node per artifact type that exists in the session, plus inferred Epics and one User Story per Feature.
2. All wikilinks resolve (`resolve_links_tool` returns no broken refs).
3. `build_index_tool` succeeds; `list_nodes_tool` returns the new nodes.
4. Re-running on the same session does not duplicate created nodes — collisions prompt per node, and `status: created` entries in import-state are skipped silently.
5. The user sees the full mapping plan with absolute target paths before any node is written, and can cancel without side effects.
6. Schema validation errors are recovered up to 3 times per node; failures are written as `status: draft` and logged in import-state — the run does not abort.
7. Similarity pass runs only when `embed_nodes_tool()` succeeded and `GEMINI_API_KEY` is set; gracefully no-ops with a one-line notice otherwise.
8. A second `/recon.import-ideate` in the same project root targeting a different project name is hard-refused with a clear error and exits without writes.
9. Final summary prints a `.gitignore` hint.

---

## 10. Edge Cases

- **Empty ideate session** (only an elevator pitch) → write Project only, warn graph is sparse.
- **Artifacts in `Status: draft`** → carry forward as `status: draft`; list in summary.
- **Recon vault configured elsewhere** → silently re-pointed to the project root on this run (single-mode vault). The user's old vault on disk is untouched; recon just stops writing there.
- **Existing `Project - *.md` with different name** → hard-refuse (single-project guard).
- **Feature references a missing Module/Persona/Goal** → stub parent with `status: draft` so wikilinks resolve.
- **User cancels at the §6.4 plan** → exit cleanly, no writes.
- **Crash mid-run** → import-state captures the partial state. Re-run resumes; created nodes are skipped, drafts/failures are retried.
- **Schema-retry budget exhausted on a node** → write the node as `status: draft` with whatever passed validation; log error to import-state; continue with remaining nodes.
- **`GEMINI_API_KEY` absent** → similarity pass logs a one-line notice and skips. Linking fall back to whatever is already in artifacts.
- **Running from a subdirectory of a git repo** → resolve to repo toplevel; all writes target there. Print the resolved path so the user notices.

---

## 11. Open Questions

Moved to `import-ideate-recommendations.md`. The author of that doc has stated recommendations for each. Confirm before implementation; revisit before v1.1 if any prove wrong.
