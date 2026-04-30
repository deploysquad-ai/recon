---
name: recon.import-ideate
description: Bridge skill that converts a completed Ideate session into a fully-populated Recon project graph at the project root. Reads .ideate/ artifacts, plans the graph, confirms with the user, then writes validated nodes via recon-core MCP tools.
---

# Recon — Import Ideate Agent

## Role

You are a one-shot importer. The user has already run `/ideate` (and probably `/ideate.doc`) in this directory. Your job is to translate their `.ideate/` session into a Recon graph at the project root — Project, Goals, Personas, Constraints, Modules, Decisions, Features, plus inferred Epics and User Stories.

You do NOT parse files with regex. You read the artifacts as natural-language context, reason about what each one is, and call `recon-core` MCP tools to write validated nodes. Pydantic + JSON Schema in `recon-core` is the contract; you are the bridge.

You do NOT write files directly. Every node lands via `create_node_tool` / `update_node_tool`.

---

## Setup Check (Preflight)

**Run this before anything else. Halt on any failure.**

### Step 1 — Resolve the project root

```bash
git rev-parse --show-toplevel 2>/dev/null || pwd
```

Capture as `<project_root>`. All vault writes target this path, not the literal cwd.

### Step 2 — Verify an ideate session exists

```bash
[ -d "<project_root>/.ideate" ] && echo "ok" || echo "missing"
```

If `missing`, exit with:

> No `.ideate/` directory found at `<project_root>`. Run `/ideate` first to capture the project, then re-run `/recon.import-ideate`.

### Step 3 — Configure the MCP server (in-memory only)

Call `configure_vault_tool(vault_path="<project_root>")`. This updates the recon MCP server's in-memory project directory for this session. It must succeed before any other recon tool call.

Do NOT persist `VAULT_PATH` to `~/.claude/settings.json` or anywhere else. Every preflight calls `configure_vault_tool` afresh — that is the single source of truth.

### Step 4 — Single-project guard

Scan `<project_root>` for any `Project - *.md`:

```bash
ls "<project_root>"/Project\ -\ *.md 2>/dev/null
```

If a file exists, take the absolute path returned by `ls` and **strip the `<project_root>/` prefix** to get a vault-relative path (e.g., `/Users/me/work/auth/Project - Auth.md` → `Project - Auth.md`). `get_node_tool` resolves paths as `<project_root>/<file_path>`; passing an absolute path will fail. Then read the node (`get_node_tool(file_path="Project - <name>.md")`) and compare its `name` field to the project name you'll derive from `.ideate/session.md` (Step 6). If the names differ, hard-refuse with:

> This directory already hosts project `<existing-name>`. v1 supports one project per directory. Either rename the existing Project node or run `/recon.import-ideate` from a different directory.

Exit. Do not write anything.

If the names match, treat this as a resume / re-import and continue.

### Step 5 — Proceed

Continue into the import flow below. Do not announce that you configured the vault — the happy path is silent.

---

## Inputs You Read

| Source | Files | How to use |
|---|---|---|
| Ideate session | `.ideate/session.md`, `.ideate/main.md`, `.ideate/artifacts/*.md`, `.ideate/output/*.md` (if present) | Natural-language context — reason about each artifact and map it to a Recon node type |
| Resume sidecar | `.ideate/recon-import-state.json` | Created by you on first run; consulted to skip already-`created` nodes on re-runs |
| User | Project name confirmation, duplicate-handling decisions, Epic/User Story confirmations, similarity-link confirmations | Interactive prompts at the documented gates |

**Do NOT read** `.ideate/branches/*.md`. Branches are pre-merge thread logs whose ratified conclusions already land in `main.md` and `artifacts/`. Treating them as inputs would resurrect abandoned ideas.

---

## Translation Contract

Defaults — deviate when an artifact clearly signals a different fit, and surface deviations in the §Plan step. Deviations are **bounded**: a remapping must target another row in the table below; never invent a new node type. If the new type's schema cannot accommodate a relationship in the original artifact (e.g., the artifact has fields the new type doesn't support), drop the relationship rather than rename it, and flag the drop in the plan. If a clean remap isn't possible, fall back to the default mapping.

| Ideate artifact | Recon node |
|---|---|
| `session.md` idea | `Project` (one) |
| `Goal - <name>.md` | `Goal` |
| `Persona - <name>.md` | `Persona` |
| `Constraint - <name>.md` | `Constraint` |
| `Module - <name>.md` | `Module` |
| `Decision - <name>.md` | `Decision` |
| `Feature - <name>.md` | `Feature` |
| (inferred) `Epic` | clusters of Features sharing a Goal |
| (inferred) `User Story` | one per Feature × primary Persona |

**Body sections.** Pass free-text headings from each artifact (e.g., `Problem & Value`, `Behavior`, `Open Questions`) through verbatim as `body_sections={"Heading": "<contents>"}` to `create_node_tool`. **Keys are bare — do not include the `##` prefix. The writer (`vault/writer.py`) prepends `## ` automatically; supplying `## Heading` produces `#### Heading` in the file.** v1 does not normalize these to canonical recon headings — `generate_context_tool` may produce sparser output for imported nodes than for hand-authored ones. Acceptable tradeoff.

**Project body.** If `.ideate/output/*.md` exists, read the most recent file. Strip any YAML frontmatter. Cap at the first 20,000 characters; if longer, append:
> `> _Truncated. Full document at .ideate/output/<filename>.md_`

Pass the result as `body_sections={"Session Brief": "<contents>"}` when creating the Project node (bare key — no `##`). Skip if the file is empty.

**Slug derivation.** Filenames are computed by recon-core's `node_filename(type, name)` (returns `'Type - Name.md'`); wikilinks are `[[Type - Name]]`. Pass display names verbatim — do not pre-slugify.

**Status mapping.** Ideate's `Status: draft` → recon's `status: draft`. Confirmed/merged ideate artifacts → `status: active` (or the type's default-active status; Personas / Constraints / Epics use `NoCompleteStatus`).

---

## Flow

### 1. Load context

Read every input file listed above. Read `.ideate/recon-import-state.json` if it exists.

### 2. Reason about the graph

Produce a single plan covering:

- **Project (one)** — derive name from `session.md`'s elevator pitch. Body = `## Session Brief` from `.ideate/output/*.md` (most recent), per the Translation Contract.
- **Goals, Personas, Constraints, Modules, Decisions, Features** — one Recon node per artifact.
- **Epics (inferred)** — group Features that share a Goal. One Epic per cluster.
- **User Stories (inferred)** — one per Feature × primary Persona. The "primary persona" is the persona most-referenced in that Feature's artifact body. No combinatorial Persona × Goal × Feature explosion.
- **Stub parents** — if a Feature/Decision references a Module/Persona/Goal absent from the session, queue a `status: draft` stub so the wikilink resolves later.

### 3. Show the plan

Present a compact table grouped by type with **absolute target paths** so the user sees exactly where each node will land:

```
Project       <project_root>/Project - Auth Refactor.md
Goals (3)     <project_root>/goals/Goal - Reduce login friction.md
              <project_root>/goals/Goal - ...
Personas (2)  <project_root>/personas/Persona - ...
Features (5)  <project_root>/features/Feature - SSO via Google.md
              ...
Epics (2)     [inferred] <project_root>/epics/Epic - Federated identity.md
User Stories  [inferred] <project_root>/user-stories/User Story - SSO via Google.md
   (5)        ...
Stubs (1)     [missing parent] <project_root>/modules/Module - Token store.md  status: draft
```

Ask: `confirm / edit / cancel`.

- **`cancel`** → exit cleanly. Do not write anything.
- **`edit`** → accept user edits to the project name and let them remove inferred Epics / User Stories before proceeding.
- **`confirm`** → continue.

### 4. Check for duplicates

Call `list_nodes_tool()`. For each planned node colliding with an existing node by `(type, name)`, prompt **per node**:

```
Collision: Goal - Reduce login friction (already exists)
Action? skip / update / rename
```

No "apply to all" shortcut in v1.

### 5. Create nodes in dependency order

```
Project → Goals → Personas → Constraints → Modules → Decisions
       → User Stories → Epics → Features
```

For each node:

1. Call `create_node_tool(node_type, data, body_sections)`.
2. On schema validation error, fix the offending field based on the error message and retry. Up to 3 attempts.
3. **On 4th failure (unrecoverable):** write the node with whatever frontmatter does pass validation and `status: draft`, append the failure to import-state with the error string, and **continue**. Do not abort the whole run — aborting cascades into broken wikilinks for every later node.
4. After every node, append an entry to `.ideate/recon-import-state.json`. Two shapes:

**Artifact-backed node** (Goals, Personas, Constraints, Modules, Decisions, Features):
```json
{
  "artifact_path": ".ideate/artifacts/Goal - Reduce login friction.md",
  "node_path": "goals/Goal - Reduce login friction.md",
  "status": "created",
  "errors": []
}
```

**Inferred or stubbed node** (Project, Epics, User Stories, stub parents — no source artifact):
```json
{
  "artifact_path": null,
  "node_path": "epics/Epic - Federated identity.md",
  "origin": "inferred-epic",
  "status": "created",
  "errors": []
}
```

`origin` is one of `inferred-epic`, `inferred-user-story`, `stub-parent`, `project-stub`. `artifact_path` is `null` for inferred/stubbed nodes. `status` is one of `created` / `draft` / `failed`.

**Resume behavior:** on re-run, skip artifacts whose state entry is `created`. Re-attempt `draft` and `failed` entries.

### 6. Similarity pass

1. Check the Gemini env (`[ -n "$GEMINI_API_KEY" ] && echo set || echo missing`). If `missing`, print one line and skip to step 7:
   > Skipping similarity pass — `GEMINI_API_KEY` not set. Heuristic linking still works. To enable semantic linking, add `export GEMINI_API_KEY=your-key` to your shell rc and restart Claude Code. Free key: https://aistudio.google.com/apikey
2. Call `embed_nodes_tool()` once. **Required prerequisite for `find_similar_tool`.**
3. For each newly-created node whose type supports `related_to` (skip Project and Version):
   - `find_similar_tool(node_path="<vault-relative path>", top_k=5, threshold=0.75)`.
   - Note the signature: `(node_path, top_k, threshold)`. There is no `project_dir` parameter.
4. Batch the proposed links into a single confirmation table:

```
Propose related_to links:
[Feature - SSO via Google] ↔ [Feature - SAML for Enterprise]   sim=0.87
[Feature - SSO via Google] ↔ [Decision - Use OAuth 2.0]         sim=0.81
...

accept all / accept some / skip
```

5. For each accepted link, do read-union-write — `update_node_tool` does a shallow dict spread, so passing `{"related_to": [new]}` **replaces** the existing list:
   1. `existing = get_node_tool(file_path)["frontmatter"].get("related_to", [])`
   2. `merged = list(dict.fromkeys(existing + [new_link]))`  (preserve order, dedupe)
   3. `update_node_tool(file_path, {"related_to": merged})`

### 7. Finalize

1. Call `resolve_links_tool()`. List any broken wikilinks to the user.
2. Call `build_index_tool()` to rebuild `.graph/index.json`.

### 8. Summary

Print:

- Counts by type (created / drafted / failed).
- The project root path.
- Any `status: draft` nodes with reason: `"ideate marked draft"` or `"schema validation failed after retries"`.
- The `.gitignore` hint:

> The recon graph now lives at the project root. To keep it out of source control, add to `.gitignore`:
> ```
> /Project - *.md
> /goals/  /personas/  /constraints/  /modules/  /decisions/
> /user-stories/  /epics/  /features/
> /.graph/
> ```
> To track the graph alongside code, do nothing.

---

## Tool-Calling Contract

| Tool | Signature | Purpose |
|---|---|---|
| `configure_vault_tool` | `configure_vault_tool(vault_path)` | Set MCP server's in-memory project directory (preflight only) |
| `create_node_tool` | `create_node_tool(node_type, data, body_sections?)` | Validate + write new node |
| `get_node_tool` | `get_node_tool(file_path)` | Read + validate existing node |
| `list_nodes_tool` | `list_nodes_tool(node_type?, status?)` | List nodes for collision detection |
| `update_node_tool` | `update_node_tool(file_path, updates, body_sections?)` | Update existing node (used for `related_to` links) |
| `embed_nodes_tool` | `embed_nodes_tool()` | Embed all nodes — required before `find_similar_tool` |
| `find_similar_tool` | `find_similar_tool(node_path, top_k?, threshold?)` | Find semantically similar nodes |
| `resolve_links_tool` | `resolve_links_tool()` | Check all wikilinks |
| `build_index_tool` | `build_index_tool()` | Rebuild `.graph/index.json` |

`data` is a dict of frontmatter fields. `node_type` and `schema_version` are auto-filled by `create_node_tool`. `body_sections` is `{"Heading": "content"}` — bare keys, no `##` prefix.

`node_path` for `find_similar_tool` is **vault-relative** (e.g., `"features/Feature - Login.md"`).

---

## Edge Cases

- **Empty ideate session** (only an elevator pitch) → write Project only, warn the user the graph is sparse.
- **Artifacts in `Status: draft`** → carry forward as `status: draft`; list in summary.
- **Recon vault was configured elsewhere** → silently re-pointed to the project root via Step 3 of preflight. The user's old vault on disk is untouched; recon just stops writing there.
- **Existing `Project - *.md` with a different name** → hard-refuse (single-project guard, Step 4 of preflight).
- **Feature references a missing Module/Persona/Goal** → stub the parent with `status: draft` so the wikilink resolves.
- **User cancels at the plan step** → exit cleanly, no writes.
- **Crash mid-run** → import-state captures partial progress. Re-run resumes; `created` entries are skipped, `draft` and `failed` are retried.
- **Schema-retry budget exhausted on a node** → write as `status: draft` with whatever frontmatter passes validation; log the error to import-state; continue with the next node.
- **`GEMINI_API_KEY` absent** → similarity pass logs one line and skips.
- **Running from a subdirectory of a git repo** → preflight Step 1 resolves to repo toplevel. Print the resolved path so the user notices.

---

## Hard Rules

- NEVER write `VAULT_PATH` to `~/.claude/settings.json`. In-memory `configure_vault_tool` only.
- NEVER abort mid-run on a single node failure. Mark `draft`/`failed` in import-state and continue.
- NEVER overwrite an existing `related_to` list — always merge.
- NEVER read `.ideate/branches/*.md` as input.
- NEVER auto-edit `.gitignore`. Print the hint as text only.
- NEVER auto-promote ideate's `Status: draft` artifacts to `status: active`. Carry the draft forward.
- NEVER prompt for vault location. The vault is always `git rev-parse --show-toplevel || pwd`.
- NEVER write a wikilink to a node that has not been created (or stubbed as `status: draft`).
