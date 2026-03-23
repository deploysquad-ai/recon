# Obsidian Project Graph Schema Design

**Date:** 2026-03-23  
**Status:** Draft  
**Schema Version:** 1  
**Project:** recon

---

## Overview

A structured Obsidian vault schema that acts as the project and feature layer above spec-kit. The LLM both authors and reads this graph through conversation, and uses it to generate enriched context bundles before handing off to spec-kit for feature execution.

---

## Node Types

| Type | Purpose |
|---|---|
| **Project** | Top-level container — name, description, status |
| **Goal** | A strategic objective the project aims to achieve — Features and User Stories trace back to Goals |
| **Version** | Release target (MVP, v1.0, v2.0) |
| **Module** | Functional subsystem (e.g. Auth, Payments, Notifications) |
| **User Story** | A user-facing behavior the system must exhibit, written as "As a [persona], I want [goal], so that [benefit]" |
| **Epic** | A product-level body of work grouping related Features within a Module |
| **Feature** | Leaf node — handed off to spec-kit for spec + implementation |
| **Decision** | ADR-style architectural/design decision with rationale and alternatives |
| **Persona** | A user, role, or system actor that interacts with the project — includes goals and context |
| **Constraint** | Hard limits — tech stack, compliance, performance budgets |

---

## Edge Types (Frontmatter Fields)

All relationships are encoded as frontmatter fields using `[[wikilinks]]`. These are the typed edges that make the graph traversable with meaning.

| Field | Used On | Points To | Cardinality | Meaning |
|---|---|---|---|---|
| `belongs_to` | Version, Module, Constraint, Persona, Goal | Project | exactly one | Structural parent (these nodes always belong to a Project) |
| `belongs_to` | User Story, Feature, Epic | Module | exactly one | Structural parent (these nodes always belong to a Module) |
| `belongs_to` | Decision | Project **or** Module | exactly one | Structural parent — a Decision may be project-wide or module-scoped |
| `target_version` | Feature, User Story, Epic | Version | zero or one | Release scope — optional during authoring, assigned as a late-binding scoping decision |
| `supports` | Feature, User Story, Epic | Goal (list) | zero or more | Which strategic goals this work advances — enables "why" traceability |
| `epic` | Feature | Epic | zero or one | Optional grouping — which Epic this Feature is part of |
| `implements` | Feature | User Story (list) | one or more | Which user stories this feature satisfies. Always required — if no User Story exists yet, create a stub User Story with `status: draft` first. |
| `depends_on` | Feature, Module | Feature or Module (list) | zero or more | Build-order dependency |
| `actors` | Feature, Module, User Story | Persona (list) | zero or more (required on User Story) | Which personas interact with this node |
| `governed_by` | Feature, Module, User Story, Decision | Constraint or Decision (list) | zero or more | Hard rules that apply |
| `related_to` | Any node type | Any node type (list) | zero or more | Soft contextual association (opt-in, not required) |

### Structural rules
- A Feature belongs to **exactly one** Module. Cross-module features are not supported; if shared behavior is needed, create a shared Module.
- Modules are **flat** — a Module belongs to a Project only, never to another Module.
- A Decision belongs to **either** a Project or a Module (not both) — specified via `belongs_to`.

---

## Status Lifecycle

Unified across all node types:

```
draft → active → complete → archived
```

**Status semantics by node type:**

| Node | `active` means | `complete` means | `archived` means |
|---|---|---|---|
| Project | In development | Shipped / no longer evolving | Abandoned or superseded |
| Goal | Actively being pursued | Achieved | No longer relevant |
| Version | Currently being built | Released | No longer relevant |
| Module | Being developed | All features delivered | Deprecated or removed |
| Persona | In scope | — (not applicable) | No longer relevant |
| User Story | In scope and relevant | Fully implemented | No longer applicable |
| Epic | Actively being worked on | All features delivered | Removed from scope |
| Feature | Actively being specced or built | Implemented and verified | Removed from scope |
| Decision | In effect | — (not applicable) | Superseded by a newer Decision |
| Constraint | In effect | — (not applicable) | Lifted or no longer applicable |

---

## Frontmatter Schemas

All nodes include a `schema_version` field for future migration detection.

### Project
```yaml
---
type: project
schema_version: 1
name: "<canonical project name>"
status: draft | active | complete | archived
description: "<one-line summary>"
---
```

### Goal
```yaml
---
type: goal
schema_version: 1
name: "<goal name>"
status: draft | active | complete | archived
belongs_to: "[[Project - <name>]]"
related_to:                  # optional — any node type
  - "[[Goal - <name>]]"
---

## Description
<what this goal aims to achieve and why it matters>

## Success Criteria
<how you know this goal has been achieved — measurable where possible>
```
> Note: Goals replace the flat `goals` list that previously lived on the Project node. Features and User Stories reference Goals via the `supports` edge, enabling full "why" traceability from implementation to strategic intent.

### Version
```yaml
---
type: version
schema_version: 1
name: "<version name>"
status: draft | active | complete | archived
belongs_to: "[[Project - <name>]]"
sequence: <integer>          # ordering within the project (1 = first)
target_date: "YYYY-MM-DD"   # optional
---
```

### Module
```yaml
---
type: module
schema_version: 1
name: "<module name>"
status: draft | active | complete | archived
belongs_to: "[[Project - <name>]]"
depends_on:                  # optional — modules that must be complete before this one
  - "[[Module - <name>]]"
governed_by:                 # optional
  - "[[Constraint - <name>]]"
  - "[[Decision - <name>]]"
related_to:                  # optional — any node type (examples only)
  - "[[Module - <name>]]"
---
```

### Persona
```yaml
---
type: persona
schema_version: 1
name: "<persona name>"
status: draft | active | archived
belongs_to: "[[Project - <name>]]"
goals:                       # required — what this persona is trying to achieve
  - "<goal 1>"
  - "<goal 2>"
context: "<brief description of this persona's background, technical proficiency, and usage patterns>"
related_to:                  # optional — other Personas (e.g. Admin is a type of User)
  - "[[Persona - <name>]]"
---

## Description
<who this persona is and what they do in the context of this project>
```
> Note: Personas are project-scoped, not module-scoped. They are referenced by Features, Modules, and User Stories via the `actors` field. Shared personas between nodes is a strong semantic signal for proposing links during the linking pass. Personas do not reach `complete` — they are `active` (in scope) or `archived` (no longer relevant).

### User Story
```yaml
---
type: user-story
schema_version: 1
name: "<user story name>"
status: draft | active | complete | archived
belongs_to: "[[Module - <name>]]"
target_version: "[[Version - <name>]]"   # optional — assign during scoping, not authoring
actors:                      # required — the persona(s) this story is written for
  - "[[Persona - <name>]]"
acceptance_criteria:         # required — list of testable conditions for "done"
  - "<Given [context], when [action], then [outcome]>"
governed_by:                 # optional — Constraint or Decision
  - "[[Constraint - <name>]]"
  - "[[Decision - <name>]]"
related_to:                  # optional — any node type
  - "[[User Story - <name>]]"
---

## Story
As a [persona], I want [goal], so that [benefit].

## Rationale
<why this story exists; business or technical driver>
```
> Note: Non-functional requirements (performance, security, compliance) should be modeled as Constraint nodes, not User Stories. User Stories capture user-facing behavior only.

### Epic
```yaml
---
type: epic
schema_version: 1
name: "<epic name>"
status: draft | active | complete | archived
belongs_to: "[[Module - <name>]]"
target_version: "[[Version - <name>]]"   # optional
supports:                    # optional — which Goals this epic advances
  - "[[Goal - <name>]]"
related_to:                  # optional — any node type
  - "[[Epic - <name>]]"
---

## Description
<what this epic delivers as a user-facing outcome>
```
> Note: Epics group related Features into a product-level body of work. A Feature optionally references its Epic via the `epic` field. Modules are technical decomposition; Epics are product-level work streams. They may cross-cut differently.

### Feature
```yaml
---
type: feature
schema_version: 1
name: "<feature name>"
status: draft | active | complete | archived
belongs_to: "[[Module - <name>]]"
target_version: "[[Version - <name>]]"   # optional — assign during scoping, not authoring
epic: "[[Epic - <name>]]"   # optional — product-level work grouping
implements:
  - "[[User Story - <name>]]"
depends_on:                  # optional — Feature or Module (examples only; any node type valid per edge table)
  - "[[Feature - <name>]]"
  - "[[Module - <name>]]"
governed_by:                 # optional — examples only; any Constraint or Decision is valid
  - "[[Constraint - <name>]]"
  - "[[Decision - <name>]]"
related_to:                  # optional — any node type (examples only)
  - "[[Feature - <name>]]"
---
```
> Note: The Feature note body is managed by spec-kit, not this schema. Acceptance criteria live on the User Story nodes this Feature implements. Leave the body empty or add a brief summary; spec-kit will populate the full spec during its authoring flow.

### Constraint
```yaml
---
type: constraint
schema_version: 1
name: "<constraint name>"
status: draft | active | archived
belongs_to: "[[Project - <name>]]"
related_to:                  # optional — any node type (examples only)
  - "[[Constraint - <name>]]"
---

## Description
<what this constraint requires and why it exists>

## Scope
<what systems, modules, or features this constraint applies to>
```
> Note: Constraints do not reach `complete`. They are either `active` (in effect) or `archived` (lifted/superseded).

### Decision
```yaml
---
type: decision
schema_version: 1
name: "<decision name>"
status: draft | active | archived
belongs_to: "[[Project - <name>]]" | "[[Module - <name>]]"  # exactly one
governed_by:                 # optional — Constraint only (a Decision cannot be governed_by another Decision)
  - "[[Constraint - <name>]]"
related_to:                  # optional
  - "[[Feature - <name>]]"
  - "[[Decision - <name>]]"
---

## Context
<why this decision was needed>

## Alternatives Considered
- <option 1>
- <option 2>

## Decision
<what was decided and why>
```
> Note: Decisions do not reach `complete`. They are either `active` (in effect) or `archived` (superseded by a newer Decision).

---

## Required vs Optional Fields

| Field | Required on |
|---|---|
| `type` | All nodes |
| `schema_version` | All nodes |
| `name` | All nodes |
| `status` | All nodes |
| `belongs_to` | All except Project |
| `implements` | Feature |
| `acceptance_criteria` | User Story |
| `actors` | User Story |
| `goals` | Persona |
| `context` | Persona |
| `sequence` | Version |
| `target_version` | Optional on Feature, User Story, Epic |
| `epic` | Optional on Feature |
| `supports` | Optional on Feature, User Story, Epic |
| `governed_by` | Optional on all |
| `depends_on` | Optional on Feature, Module |
| `related_to` | Optional on all |
| `target_date` | Optional on Version |

---

## Vault Folder Structure

```
vault/
  {project-slug}/
    Project - <name>.md       ← the Project node (follows naming convention)
    goals/
      Goal - <name>.md
    versions/
      Version - MVP.md
      Version - v1.0.md
    personas/
      Persona - <name>.md
    modules/
      Module - <name>.md
    user-stories/
      User Story - <name>.md
    epics/
      Epic - <name>.md
    features/
      Feature - <name>.md
    decisions/
      Decision - <name>.md
    constraints/
      Constraint - <name>.md
```

- One folder per project, named by slug (kebab-case)
- The project root node is `Project - <name>.md` (consistent with all other node types)
- Note filenames follow: `{Type} - {Name}.md`

---

## Note Naming Convention

```
{Type} - {Human-readable name}.md
```

Examples:
- `Project - Payments Platform.md`
- `Feature - Card tokenization.md`
- `User Story - Tokenize card data.md`
- `Decision - Use Stripe Elements.md`
- `Persona - Developer.md`
- `Constraint - PCI DSS.md`

Wikilinks use the full filename without `.md`:
```
[[Feature - Card tokenization]]
[[Module - Checkout]]
[[Project - Payments Platform]]
```

**Name field vs filename:** The frontmatter `name` field and the filename must stay in sync — the filename is derived from the name (`{Type} - {name}.md`). The frontmatter `name` is the canonical source of truth. If they diverge, the context builder uses the frontmatter `name` and the filename is considered stale. Renames must update both.

**Important:** Renaming a note will break all wikilinks that reference it. Obsidian's rename-with-link-update feature handles this in the UI. Programmatic renames must use `obsidian-cli move` which updates wikilinks automatically.

---

## Node Authoring Order

When creating nodes through conversation, the LLM must follow this creation order to ensure `belongs_to` references always resolve:

```
1. Project
2. Goal(s)            ← strategic objectives, right after Project
3. Persona(s)         ← who interacts with the system
4. Constraint(s)
5. Module(s)
6. Decision(s)        ← after Module, since may belong_to a Module
7. User Story(s)      ← written for Personas, within Modules
8. Epic(s)            ← groups Features into product-level work streams
9. Feature(s)         ← last, references all other node types
10. Version(s)        ← late-binding scope — assign after you know what exists
--- version assignment pass ---
11. Assign target_version to User Stories, Epics, and Features
```

A parent node **must exist** before any child node that references it via `belongs_to`.

**Broken reference handling:** If the LLM attempts to create a node that references a node that does not yet exist (via any edge field), it must:
1. Pause and create the referenced node first (following authoring order), then create the original node
2. If the referenced node cannot be created yet (e.g. insufficient information), create a stub node with `status: draft` and a placeholder name, then return to fill it in
3. Never write a wikilink to a non-existent note — broken links silently fail graph traversal

---

## Context Bundle Format

When retrieving context for a Feature, the context builder emits a structured Markdown file (`CONTEXT.md`) with the following sections. This file is the handoff artifact passed to spec-kit.

```markdown
<!-- context_bundle_version: 1 -->
# Context Bundle: {Feature name}

## Project
- **Name:** {project name}
- **Description:** {description}

## Goals this Feature supports
*(from the Feature's and its User Stories' `supports` edges, deduplicated)*
- **{Goal name}**: {goal description} — Success criteria: {success criteria}
- ...

## Version
- **Target:** {version name}
- **Sequence:** {sequence}
- **Target Date:** {target_date if set}

## Module
- **Name:** {module name}
- **Governed by:** {constraints + decisions list}

## User Stories this Feature implements
- **{User Story name}**: {story statement}
  - Acceptance criteria: {criteria list}
- ...

## Constraints in effect
*(union of the Feature's and Module's `governed_by` Constraint entries, deduplicated)*
- **{Constraint name}**: {constraint description} — Scope: {constraint scope}
- ...

## Relevant Decisions
*(union of the Feature's and Module's `governed_by` Decision entries, deduplicated)*
- **{Decision name}**: {decision summary}
- ...

## Dependencies (must be complete before this feature)
*(from the Feature's `depends_on` — may include Features and/or Modules)*
- [[Feature - <name>]] — status: {status}
- [[Module - <name>]] — status: {status}
- ...

## Related Features (context only)
- [[Feature - <name>]]
- ...
```

This format is the contract between the context builder and spec-kit. It is intentionally human-readable so a human can also review it before spec-kit runs.

---

## Architecture: LLM as Conversational UI, Not Database Engine

The LLM (Claude or any agent) is the **conversational interface**. It interviews the user, understands their intent, and calls structured tool functions. It does **not** write files directly.

### Tool-Calling Contract

The LLM interacts with the vault exclusively through `recon-core` tool functions:

| Tool | Purpose |
|---|---|
| `create_node(type, data)` | Validate data against JSON Schema, write `.md` file to vault |
| `update_node(path, data)` | Update an existing node's frontmatter and/or body |
| `get_node(path)` | Read and parse a node file |
| `list_nodes(type?, status?)` | List nodes in the vault, optionally filtered |
| `resolve_links(projectDir)` | Check all wikilinks, return valid + broken |
| `build_index(projectDir)` | Rebuild `graph.json` from vault files |
| `generate_context(featureName)` | Traverse graph, emit `CONTEXT.md` |

**Why this matters:**
- The LLM cannot produce invalid nodes — `recon-core` validates against JSON Schema before writing
- Every write is deterministic and testable
- The agent instruction files describe *conversation flow* (what to ask, in what order), not *file format rules*
- The same `recon-core` library works for scripted/CI use without any LLM

### Build Order

```
1. JSON Schemas          ← machine-readable source of truth for all node types
2. recon-core library    ← parse, write, validate, index (the engine)
3. context-builder       ← traversal + CONTEXT.md export (MVP gate — proves value without LLM)
4. Agent instruction     ← conversational flow, question prompts, tool-calling patterns
5. CLI                   ← wires LLM + recon-core together
```

The context-builder (step 3) is the **MVP gate**: if we can hand-author vault files and generate a flawless `CONTEXT.md` for spec-kit, the core premise works before any LLM integration.

---

## Infrastructure

| Layer | Preferred tool | Alternative |
|---|---|---|
| Vault read/write | `recon-core` library (direct file I/O with validation) | `obsidian-cli` |
| Graph traversal | Frontmatter parsing via `recon-core` | `obsidian-graph-query` skill (richer algorithms) |
| Embedding (v1.0) | OpenAI `text-embedding-3-small` (direct API call) | Anthropic embeddings |
| LLM interface | Claude Code via tool-calling | Any LLM with function calling |
| Execution layer | spec-kit (`specify` CLI) | — |

**MVP choices:**
- Use **`recon-core`** for all vault reads and writes — deterministic, testable, schema-validated
- Use **frontmatter parsing** for context bundle generation (simpler, self-contained)
- **Defer embeddings to v1.0** — for graphs under ~200 nodes, heuristic linking (shared personas, name mentions, module co-membership) is sufficient
- Use **`obsidian-graph-query`** if advanced traversal is needed later (e.g. cycle detection, shortest path)

**Embedding notes (v1.0, not MVP):**
- Embed each node as a **single unit** (frontmatter + body concatenated) — nodes are small structured records, not large documents; no chunking required
- No LangChain — call the embedding API directly in a batch loop
- Batch embed after Phase 1 (all nodes authored), before the linking pass; re-embed changed nodes on-demand
- Vectors stored in `graph.json` under each node entry alongside metadata and resolved edges
- Cosine similarity over vectors, combined with shared-persona signal, drives link proposals during Phase 2

---

## Known Limitations (POC)

These are accepted gaps for the POC, to be addressed in v1.0:

- **No session resume** — if an authoring session crashes mid-Phase 1, there is no mechanism to detect which nodes already exist and resume from where you left off
- **No idempotent writes** — re-running the authoring session may duplicate nodes rather than updating existing ones
- **No partial vault detection** — the tool does not warn if a vault is in an incomplete state
- **Inference quality** — The LLM infers graph nodes from natural conversation (see brainstorm Decision 11). If inference quality is poor, the user spends more time correcting drafts than they would writing from scratch. Early dog-food runs will validate whether the schema is inferable from typical project descriptions.
- **Embeddings deferred** — semantic link proposals are heuristic-only until v1.0

---

## What Is NOT in Scope

- Implementation-level details (types, response objects, API contracts) — stored in feature spec files, not the graph
- Test cases — spec-kit's responsibility
- Code — spec-kit's responsibility
- Embedding pipeline (deferred to v1.0)
- Cross-project node references
- UI / web interface
