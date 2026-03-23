# Phase C+D: Agent Instruction Files + Dog-Food Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the agent instruction files that drive LLM-powered graph authoring sessions, then dog-food the entire pipeline by authoring the `recon` project itself as vault nodes and generating a CONTEXT.md handoff.

**Architecture:** The LLM is a conversational UI. It does NOT write files directly. It calls structured tool functions exposed by the `recon-core` Python library, which handles all validation, file I/O, and index management. The agent instruction files define the LLM's role, the authoring workflow, and per-type guidance. They are loaded as system context by the CLI.

**Tech Stack:** Markdown (instruction files), Python/Pydantic (`recon-core` library — already built), Obsidian vault (output)

**Specs:**
- `docs/architecture/brainstorm-decisions.md` — Decisions 1-12
- `docs/architecture/schema-design.md` — Node type schema spec (10 types)
- `recon-core/src/deploysquad_recon_core/` — Pydantic models (source of truth for validation)
- `docs/plan.md` — Feedback tasklist (T10-T13)

---

## recon-core Tool Functions (already implemented)

The LLM calls these 7 functions. It never touches the filesystem directly.

| Function | Signature | Purpose |
|---|---|---|
| `create_node` | `(node_type, data, project_dir, body_sections=None) -> Path` | Validate + write a new .md node file |
| `get_node` | `(file_path) -> dict` | Read + validate an existing node |
| `list_nodes` | `(project_dir, node_type=None, status=None) -> list[dict]` | List nodes with optional filters |
| `update_node` | `(file_path, updates, body_sections=None) -> Path` | Merge updates into existing node, re-validate, rewrite |
| `resolve_links` | `(project_dir) -> dict` | Check all wikilinks; returns `{"valid": [...], "broken": [...]}` |
| `build_index` | `(project_dir) -> dict` | Build `.graph/index.json` from vault files |
| `generate_context` | `(feature_name, project_dir) -> str` | Traverse graph from Feature, emit CONTEXT.md string |

---

## 10 Node Types (authoring order)

```
1. Project      — top-level container (no belongs_to)
2. Goal         — strategic objective (belongs_to: Project)
3. Persona      — user/role/system with goals + context (belongs_to: Project)
4. Constraint   — hard limit (belongs_to: Project)
5. Module       — functional subsystem (belongs_to: Project)
6. Decision     — ADR-style record (belongs_to: Project | Module)
7. User Story   — "As a [persona]..." (belongs_to: Module)
8. Epic         — product-level work grouping (belongs_to: Module)
9. Feature      — leaf node, handed to spec-kit (belongs_to: Module)
10. Version     — release target, assigned late (belongs_to: Project)
    → version assignment pass (bind Features/Epics/User Stories to Versions)
    → linking pass (heuristic cross-references)
```

---

## Module Layout

```
recon-author/
  AGENT.md                      <- always-loaded base context
  schemas/
    project.md                  <- Project: field ref + question prompts + body template
    goal.md                     <- Goal
    persona.md                  <- Persona (was Actor)
    constraint.md               <- Constraint
    module.md                   <- Module
    decision.md                 <- Decision
    user-story.md               <- User Story (was Requirement)
    epic.md                     <- Epic (new)
    feature.md                  <- Feature
    version.md                  <- Version
  linking-pass.md               <- heuristic linking (no embeddings in MVP)
  context-bundle.md             <- references recon-core generate_context()
```

Each file is **independently injectable** — the CLI loads `AGENT.md` always, plus whichever schema/phase file is relevant to the current step.

---

## Chunk 1: Agent Orchestration

### Task 1: Write `recon-author/AGENT.md`

**Files:**
- Create: `recon-author/AGENT.md`

This is the always-present base context. It defines the LLM's role, tool-calling contract, authoring workflow, and interaction rules. It must NOT include individual node schemas (those are lazy-loaded per phase).

- [ ] **Step 1: Create `recon-author/AGENT.md`**

The file must cover these sections:

**1.1 Role**
- You are a graph authoring agent. Your job: help the user build a structured project graph by calling recon-core tool functions.
- You do NOT write files. You call `create_node()`, `update_node()`, etc.
- You do NOT validate data. recon-core validates via Pydantic models. If a call fails, report the error and ask the user to fix the input.

**1.2 Tool-Calling Contract**
- List all 7 tool functions with their signatures (from the table above).
- Emphasize: every write goes through `create_node` or `update_node`. Never emit raw YAML/Markdown for the user to paste.
- `body_sections` is a `dict[str, str]` mapping heading names to content (e.g. `{"Description": "...", "Scope": "..."}`)

**1.3 Inference-First Approach (Decision 11)**
- The user describes their project in natural language.
- The LLM infers and drafts a batch of nodes (show a summary table), then asks for confirmation.
- This is NOT a sequential interview. Do not ask one question at a time per field.
- Progressive disclosure: start with Project/Goals/Personas from the user's description. Only dig deeper (Modules, Decisions, etc.) once the foundation is confirmed.
- The user can always override, add, or remove inferred nodes.

**1.4 Authoring Order (10 types)**
- List the 10-type order with the version-assignment and linking passes at the end.
- Explain why order matters: `belongs_to` links must resolve to existing nodes.

**1.5 Phase Transitions**
- Phase 1: Author all nodes (types 1-9)
- Phase 2: Version assignment — bind `target_version` on Features, Epics, User Stories
- Phase 3: Linking pass — heuristic cross-references (load `linking-pass.md`)
- Phase 4: Build index + generate context bundles (load `context-bundle.md`)
- After each phase, announce completion and wait for user confirmation before proceeding.

**1.6 Vault Path + Folder Structure**
- Default: `~/obsidian-vault-agents`
- Project folder: `{vault}/{project-slug}/`
- Subfolder map (from `vault/paths.py`):
  - `project` -> root, `goal` -> `goals/`, `version` -> `versions/`, `persona` -> `personas/`, `constraint` -> `constraints/`, `module` -> `modules/`, `decision` -> `decisions/`, `user-story` -> `user-stories/`, `epic` -> `epics/`, `feature` -> `features/`
- Filename convention: `{Type Display} - {Name}.md` (e.g. `User Story - Login.md`)
- Wikilink convention: `[[Type Display - Name]]` (e.g. `[[Persona - Developer]]`)

**1.7 Interaction Rules**
- Never invent data without the user's input. When unsure, offer concrete options.
- Show a summary of what will be created before calling `create_node`.
- After each batch of nodes, run `resolve_links()` and report any broken links.
- If the user wants to skip a node type, confirm explicitly and move on.

- [ ] **Step 2: Review and commit**

```bash
git add recon-author/AGENT.md
git commit -m "feat: add recon-author/AGENT.md — agent orchestration with tool-calling contract"
```

---

## Chunk 2: Schema Prompt Files (10 files)

Each schema prompt file lives in `recon-author/schemas/` and contains:

1. **Field Reference** — a table of frontmatter fields referencing the Pydantic model. NOT a duplicate schema. Format: field name, type, required/optional, notes.
2. **Body Section Template** — which `## Heading` sections the body expects (passed as `body_sections` dict to `create_node`).
3. **Question Prompts (FALLBACK)** — conversation hints the LLM uses ONLY if the inference-first approach did not surface enough data. These are NOT a sequential interview script.
4. **Example `create_node` Call** — a concrete example showing the function call with realistic data.

Validation rules are NOT repeated here. recon-core's Pydantic models are the single source of truth.

---

### Task 2: Write `schemas/project.md`

**Files:** `recon-author/schemas/project.md`

- [ ] **Step 1: Create the file**

Field reference (from `ProjectNode`):
| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | min 1 char, becomes filename |
| `status` | FullStatus | yes | draft / active / complete / archived |
| `description` | string | yes | min 1, max 120 chars |

Body sections: none required (free-form optional body).

Example call:
```python
create_node("project", {
    "name": "recon",
    "status": "active",
    "description": "Structured project graphs in Obsidian vaults for LLM-driven spec generation",
})
```

Fallback prompts:
1. "What is your project called?" -> `name`
2. "Describe your project in one line (max 120 chars)." -> `description`
3. "Status?" -> default `draft`

- [ ] **Step 2: Commit**

---

### Task 3: Write `schemas/goal.md`

**Files:** `recon-author/schemas/goal.md`

- [ ] **Step 1: Create the file**

Field reference (from `GoalNode`):
| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | short goal title |
| `status` | FullStatus | yes | draft / active / complete / archived |
| `belongs_to` | Wikilink | yes | must be `[[Project - ...]]` |
| `related_to` | list[Wikilink] | no | other Goals |

Body sections:
- `## Description` — what this goal means
- `## Success Criteria` — how you know it's achieved

Example call:
```python
create_node("goal", {
    "name": "Prove context-builder value",
    "status": "active",
    "belongs_to": "[[Project - recon]]",
}, body_sections={
    "Description": "Demonstrate that a structured vault can generate useful CONTEXT.md for spec-kit.",
    "Success Criteria": "Hand-authored vault produces correct CONTEXT.md for at least one Feature.",
})
```

- [ ] **Step 2: Commit**

---

### Task 4: Write `schemas/persona.md`

**Files:** `recon-author/schemas/persona.md`

- [ ] **Step 1: Create the file**

Field reference (from `PersonaNode`):
| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | e.g. "Developer", "End User" |
| `status` | NoCompleteStatus | yes | draft / active / archived (no "complete") |
| `belongs_to` | Wikilink | yes | `[[Project - ...]]` |
| `goals` | list[string] | yes | min 1 entry — what this persona wants |
| `context` | string | yes | background, constraints, environment |
| `related_to` | list[Wikilink] | no | other Personas |

Body sections: none required (goals and context are in frontmatter).

Example call:
```python
create_node("persona", {
    "name": "Developer",
    "status": "active",
    "belongs_to": "[[Project - recon]]",
    "goals": ["Author project graphs quickly", "Get useful context bundles for spec writing"],
    "context": "Uses CLI tools, familiar with Obsidian, wants LLM-assisted workflows.",
})
```

Note: Personas replace the old "Actor" type. They have richer fields (`goals`, `context`) to support inference-first authoring.

- [ ] **Step 2: Commit**

---

### Task 5: Write `schemas/constraint.md`

**Files:** `recon-author/schemas/constraint.md`

- [ ] **Step 1: Create the file**

Field reference (from `ConstraintNode`):
| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | short descriptive name |
| `status` | NoCompleteStatus | yes | draft / active / archived |
| `belongs_to` | Wikilink | yes | `[[Project - ...]]` |
| `related_to` | list[Wikilink] | no | other Constraints |

Body sections:
- `## Description` — what this constraint requires and why
- `## Scope` — what it applies to

Example call:
```python
create_node("constraint", {
    "name": "No external databases",
    "status": "active",
    "belongs_to": "[[Project - recon]]",
}, body_sections={
    "Description": "The project must not require any external database. All data lives in Obsidian vault Markdown files.",
    "Scope": "All modules — storage is vault-only.",
})
```

- [ ] **Step 2: Commit**

---

### Task 6: Write `schemas/module.md`

**Files:** `recon-author/schemas/module.md`

- [ ] **Step 1: Create the file**

Field reference (from `ModuleNode`):
| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | functional subsystem name |
| `status` | NoCompleteStatus | yes | draft / active / archived |
| `belongs_to` | Wikilink | yes | `[[Project - ...]]` |
| `actors` | list[Wikilink] | no | must reference Persona nodes only (validated) |
| `depends_on` | list[Wikilink] | no | other Modules |
| `governed_by` | list[Wikilink] | no | Constraints and/or Decisions |
| `related_to` | list[Wikilink] | no | other Modules |

Body sections:
- `## Description` — what this module is responsible for

Example call:
```python
create_node("module", {
    "name": "Vault Writer",
    "status": "active",
    "belongs_to": "[[Project - recon]]",
    "actors": ["[[Persona - Developer]]"],
    "governed_by": ["[[Constraint - No external databases]]"],
}, body_sections={
    "Description": "Writes validated node Markdown files to the Obsidian vault.",
})
```

- [ ] **Step 2: Commit**

---

### Task 7: Write `schemas/decision.md`

**Files:** `recon-author/schemas/decision.md`

- [ ] **Step 1: Create the file**

Field reference (from `DecisionNode`):
| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | ADR-style title |
| `status` | NoCompleteStatus | yes | draft / active / archived |
| `belongs_to` | Wikilink | yes | `[[Project - ...]]` or `[[Module - ...]]` |
| `governed_by` | list[Wikilink] | no | Constraints ONLY (validated — no Decisions) |
| `related_to` | list[Wikilink] | no | other Decisions, Features, etc. |

Body sections:
- `## Context` — why this decision was needed
- `## Alternatives Considered` — options evaluated
- `## Decision` — what was decided and why
- `## Rationale` — deeper justification (optional)

Example call:
```python
create_node("decision", {
    "name": "LLM infers the graph",
    "status": "active",
    "belongs_to": "[[Project - recon]]",
}, body_sections={
    "Context": "Users describing their project should not be interviewed one field at a time.",
    "Alternatives Considered": "- Sequential interview per field\n- Free-form dump then manual structuring",
    "Decision": "The LLM infers a batch of nodes from the user's natural language description, then confirms.",
})
```

- [ ] **Step 2: Commit**

---

### Task 8: Write `schemas/user-story.md`

**Files:** `recon-author/schemas/user-story.md`

- [ ] **Step 1: Create the file**

Field reference (from `UserStoryNode`):
| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | short descriptive name |
| `status` | FullStatus | yes | draft / active / complete / archived |
| `belongs_to` | Wikilink | yes | `[[Module - ...]]` |
| `actors` | list[Wikilink] | yes (min 1) | must reference Persona nodes (validated) |
| `acceptance_criteria` | list[string] | yes (min 1) | testable conditions |
| `supports` | list[Wikilink] | no | Goal nodes this story supports |
| `target_version` | Wikilink or null | no | assigned during version pass |
| `governed_by` | list[Wikilink] | no | Constraints / Decisions |
| `related_to` | list[Wikilink] | no | other User Stories |

Body sections:
- `## Story` — "As a [persona], I want [goal], so that [benefit]" format

Example call:
```python
create_node("user-story", {
    "name": "Author project node",
    "status": "draft",
    "belongs_to": "[[Module - Vault Writer]]",
    "actors": ["[[Persona - Developer]]"],
    "acceptance_criteria": [
        "Project node file is created with valid frontmatter",
        "Description is under 120 characters",
    ],
    "supports": ["[[Goal - Prove context-builder value]]"],
}, body_sections={
    "Story": "As a Developer, I want to create a Project node via CLI, so that I can start building my project graph.",
})
```

Note: User Stories replace the old "Requirement" type. All stories use the "As a [persona]..." format. Non-functional requirements should be expressed as Constraints instead.

- [ ] **Step 2: Commit**

---

### Task 9: Write `schemas/epic.md`

**Files:** `recon-author/schemas/epic.md`

- [ ] **Step 1: Create the file**

Field reference (from `EpicNode`):
| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | product-level work stream |
| `status` | NoCompleteStatus | yes | draft / active / archived |
| `belongs_to` | Wikilink | yes | `[[Module - ...]]` |
| `target_version` | Wikilink or null | no | assigned during version pass |
| `supports` | list[Wikilink] | no | Goal nodes |
| `related_to` | list[Wikilink] | no | other Epics |

Body sections:
- `## Description` — what this epic covers
- `## Scope` — what is in/out of scope

Example call:
```python
create_node("epic", {
    "name": "Graph Authoring",
    "status": "active",
    "belongs_to": "[[Module - Vault Writer]]",
    "supports": ["[[Goal - Prove context-builder value]]"],
}, body_sections={
    "Description": "All work related to creating and updating nodes in the vault.",
    "Scope": "In: create, update, validate nodes. Out: linking, indexing, context generation.",
})
```

Note: Epics group Features at the product level. Modules remain the technical decomposition. A Feature optionally references an Epic via its `epic` field.

- [ ] **Step 2: Commit**

---

### Task 10: Write `schemas/feature.md`

**Files:** `recon-author/schemas/feature.md`

- [ ] **Step 1: Create the file**

Field reference (from `FeatureNode`):
| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | feature name |
| `status` | FullStatus | yes | draft / active / complete / archived |
| `belongs_to` | Wikilink | yes | `[[Module - ...]]` |
| `implements` | list[Wikilink] | yes (min 1) | User Story nodes |
| `actors` | list[Wikilink] | no | Persona nodes (validated) |
| `supports` | list[Wikilink] | no | Goal nodes |
| `target_version` | Wikilink or null | no | assigned during version pass |
| `epic` | Wikilink or null | no | optional Epic grouping |
| `depends_on` | list[Wikilink] | no | other Features / Modules |
| `governed_by` | list[Wikilink] | no | Constraints / Decisions |
| `related_to` | list[Wikilink] | no | other Features |

Body sections: minimal or empty. Detailed specs belong in spec-kit, not here.

Example call:
```python
create_node("feature", {
    "name": "Write project node",
    "status": "draft",
    "belongs_to": "[[Module - Vault Writer]]",
    "implements": ["[[User Story - Author project node]]"],
    "actors": ["[[Persona - Developer]]"],
    "supports": ["[[Goal - Prove context-builder value]]"],
})
```

- [ ] **Step 2: Commit**

---

### Task 11: Write `schemas/version.md`

**Files:** `recon-author/schemas/version.md`

- [ ] **Step 1: Create the file**

Field reference (from `VersionNode`):
| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | e.g. "MVP", "v1.0" |
| `status` | FullStatus | yes | draft / active / complete / archived |
| `belongs_to` | Wikilink | yes | `[[Project - ...]]` |
| `sequence` | int | yes | >= 1, ordering within project |
| `target_date` | string or null | no | YYYY-MM-DD format |

Body sections: optional free-form (scope notes).

Example call:
```python
create_node("version", {
    "name": "MVP",
    "status": "active",
    "belongs_to": "[[Project - recon]]",
    "sequence": 1,
})
```

Note: Versions are authored LAST in the authoring order. After creation, run a version assignment pass to bind `target_version` on Features, Epics, and User Stories using `update_node()`.

- [ ] **Step 2: Commit**

---

## Chunk 3: Phase Files

### Task 12: Write `recon-author/linking-pass.md`

**Files:** `recon-author/linking-pass.md`

This file is injected after all nodes are authored and versions are assigned.

- [ ] **Step 1: Create the file**

The linking pass uses **heuristic signals only** (no embeddings for MVP — Decision 8/T8). The file must cover:

**Heuristic Link Signals (all of these, combined):**
1. **Shared Personas** — two nodes that reference the same Persona in their `actors` field are strong `related_to` candidates
2. **Name mentions** — a node's body text mentions another node's name (exact or close match) -> strong candidate
3. **Module co-membership** — two Features in the same Module that share User Stories or Personas -> `related_to` candidate
4. **Constraint/Decision propagation** — if a Module has a `governed_by` entry, its child Features likely inherit that governance

**Traversal Order for Proposals:**
1. Modules -> propagate `governed_by` to child Features/User Stories
2. Features -> `related_to` between Features sharing Personas or User Stories
3. User Stories -> `related_to` between stories in the same Module
4. Decisions -> `related_to` to Features they impact

**Proposal Format:**
```
Propose: [[Feature - X]] -> related_to -> [[Feature - Y]]
Signal: shared persona [[Persona - Developer]], same module [[Module - Auth]]
Accept? [y/n/skip]
```

**Execution:**
- Batch all proposals, show to user
- Only write confirmed links via `update_node(file_path, {"related_to": [...existing, new_link]})`
- After all confirmed links are written, run `resolve_links()` to verify no broken links
- Run `build_index()` to rebuild `.graph/index.json`

**No embeddings for MVP.** Embeddings are deferred to v1.0 (see Decision 9 in brainstorm-decisions.md).

- [ ] **Step 2: Commit**

---

### Task 13: Write `recon-author/context-bundle.md`

**Files:** `recon-author/context-bundle.md`

This file is injected on-demand after the graph is complete.

- [ ] **Step 1: Create the file**

The file must cover:

**Purpose:** Generate a CONTEXT.md handoff for spec-kit by traversing the graph from a Feature node.

**How:** Call `generate_context(feature_name, project_dir)` from recon-core. This is already implemented and tested. The function:
1. Reads the Feature node
2. Traverses: Feature -> Module -> Project, Feature -> Version, Feature -> User Stories -> Goals, Feature + Module -> Constraints, Feature + Module -> Decisions, Feature -> Dependencies, Feature -> Related
3. Renders a structured Markdown document

**Output location:** The CLI writes the returned string to `{project_dir}/features/CONTEXT - {feature_name}.md`

**When to generate:**
- After linking pass is complete
- On-demand for any Feature: `generate-context <feature-name>`
- Can regenerate at any time (idempotent — overwrites previous output)

**Validation before generating:**
- Run `resolve_links()` first. If there are broken links involving the target Feature, warn the user.
- If any node in the traversal chain is missing, `generate_context()` will skip that section (not fail).

**This is the MVP gate (Decision 12 / T7b).** If generate_context produces a useful CONTEXT.md from hand-authored vault files, the core premise is validated.

- [ ] **Step 2: Commit**

---

## Chunk 4: Dog-Food

### Task 14: Hand-author vault for `recon` (Phase D — T12)

**Files:**
- Read: `recon-author/AGENT.md`, all `recon-author/schemas/*.md`, both spec docs
- Write: `~/obsidian-vault-agents/recon/` (full node set via `create_node`)

This task proves the data model before wiring up the LLM agent. Use recon-core programmatically (Python script or REPL) to create nodes.

- [ ] **Step 1: Set up vault directory**

```bash
mkdir -p ~/obsidian-vault-agents/recon/.graph
```

- [ ] **Step 2: Author nodes using recon-core**

Write a Python script `scripts/dogfood_author.py` that calls `create_node()` for each node in order:

1. **Project:** recon
2. **Goals:** (2-3) e.g. "Prove context-builder value", "Enable LLM-driven graph authoring"
3. **Personas:** (3) Developer, LLM Agent, CLI User
4. **Constraints:** (2-3) e.g. "No external databases", "Obsidian-compatible Markdown"
5. **Modules:** (4-5) e.g. Vault Writer, Index Builder, Context Generator, Link Resolver, Schema Engine
6. **Decisions:** (3-5) key decisions from brainstorm doc (e.g. "LLM infers the graph", "Heuristic linking for MVP", "Context-builder as MVP gate")
7. **User Stories:** (4-6) e.g. "Author project node", "Generate context bundle", "Resolve broken links"
8. **Epics:** (2-3) e.g. "Graph Authoring", "Context Generation"
9. **Features:** (4-6) e.g. "Write project node", "Build index", "Generate CONTEXT.md", "Heuristic link proposals"
10. **Versions:** (2) MVP (sequence 1), v1.0 (sequence 2)
11. **Version assignment pass:** `update_node()` to bind `target_version` on Features/Epics/User Stories

- [ ] **Step 3: Run link resolution and index build**

```python
from deploysquad_recon_core import resolve_links, build_index, write_index

result = resolve_links("~/obsidian-vault-agents/recon")
print(f"Valid: {len(result['valid'])}, Broken: {len(result['broken'])}")
assert len(result['broken']) == 0, f"Broken links: {result['broken']}"

index = build_index("~/obsidian-vault-agents/recon")
write_index(index, "~/obsidian-vault-agents/recon")
```

- [ ] **Step 4: Generate CONTEXT.md for a Feature**

```python
from deploysquad_recon_core import generate_context

ctx = generate_context("Write project node", "~/obsidian-vault-agents/recon")
print(ctx)
# Write to file
Path("~/obsidian-vault-agents/recon/features/CONTEXT - Write project node.md").expanduser().write_text(ctx)
```

- [ ] **Step 5: Verify output**

```bash
find ~/obsidian-vault-agents/recon -type f | sort
cat ~/obsidian-vault-agents/recon/features/CONTEXT\ -\ Write\ project\ node.md
```

Verify the CONTEXT.md contains: Project info, Goals, Module info, User Stories with acceptance criteria, Constraints, Decisions, Dependencies.

- [ ] **Step 6: Commit dogfood script**

```bash
git add scripts/dogfood_author.py
git commit -m "feat: add dogfood authoring script for recon vault"
```

---

### Task 15: Wire up CLI + LLM-driven session (Phase D — T13)

**Files:**
- Read: all `recon-author/` instruction files
- Write: CLI integration code (TBD location)

This task wires up the recon-core tool functions as callable tools for an LLM agent, then runs an interactive authoring session.

- [ ] **Step 1: Define tool schemas for LLM**

Create JSON tool definitions (OpenAI/Anthropic function-calling format) for the 7 recon-core functions. Each tool definition maps 1:1 to a recon-core function.

- [ ] **Step 2: Build minimal CLI harness**

A Python script that:
1. Loads `AGENT.md` as system prompt
2. Lazy-loads schema files based on current authoring phase
3. Exposes recon-core functions as callable tools
4. Runs a conversation loop: user input -> LLM response -> tool calls -> results back to LLM
5. Handles phase transitions (authoring -> version assignment -> linking -> context generation)

- [ ] **Step 3: Run interactive session**

Run the CLI against a fresh vault. The LLM should:
1. Ask the user to describe their project
2. Infer a batch of nodes from the description
3. Show the inferred nodes for confirmation
4. Call `create_node()` for each confirmed node, in authoring order
5. Run version assignment, linking pass, and context generation

- [ ] **Step 4: Compare output quality**

Compare LLM-authored vault output against hand-authored (Task 14) output:
- Are all expected nodes present?
- Are wikilinks valid? (`resolve_links()` returns zero broken)
- Does `generate_context()` produce equivalent quality?

- [ ] **Step 5: Document findings and commit**

```bash
git add -A
git commit -m "feat: CLI harness for LLM-driven graph authoring sessions"
```

---

## Summary

| Chunk | Deliverable | Tasks |
|---|---|---|
| 1 | `recon-author/AGENT.md` — orchestration + tool-calling contract | 1 |
| 2 | 10 schema prompt files in `recon-author/schemas/` | 2-11 |
| 3 | Phase files: `linking-pass.md`, `context-bundle.md` | 12-13 |
| 4 | Dog-food: hand-author vault (T12) + LLM-driven session (T13) | 14-15 |

**Total:** 15 tasks across 4 chunks. Each chunk is independently reviewable and committable.

**Key differences from the old plan:**
- recon-core exists — the LLM calls tool functions, not writes files
- 10 node types (was 8): added Goal, Epic; renamed Actor->Persona, Requirement->User Story
- No `embedding.md` for MVP — heuristic linking only
- Inference-first approach — the LLM drafts nodes in bulk from natural language, not sequential interview
- `context-bundle.md` references `generate_context()` (already implemented), not a traversal spec
- Dog-food split into hand-authored (proves data model) then LLM-driven (proves agent UX)
