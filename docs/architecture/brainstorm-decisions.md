# Brainstorm Decisions — recon Claude Integration

**Date:** 2026-03-23
**Status:** Agreed — ready for full design session

---

## What We're Building

A CLI tool (similar to `speckit.specify`) that lets users build a structured project graph in an Obsidian vault through an interactive LLM-driven conversation. The LLM (Claude Code) authors and links graph nodes, using the vault as a file store and maintaining a separate index for fast relationship traversal.

---

## Decisions

### 1. Entry Point
**CLI command**, installed per-project (same pattern as `speckit init` / `specify`).
Not an OpenClaw skill, not a speckit subcommand — a standalone tool.

---

### 2. Vault Interface
**Direct file writes to the Obsidian vault** (`~/obsidian-vault-agents` or user-configured path).
No dependency on Obsidian being open. No MCP plugin required for core authoring.
Files are plain Markdown with YAML frontmatter — readable by Obsidian, humans, and tooling equally.

---

### 3. Linking Strategy — Two-Phase Authoring
**Phase 1 — Author:** Claude authors all nodes in schema order (Project → Goals → Personas → Constraints → Modules → Decisions → User Stories → Epics → Features → Versions), writing files as it goes.
**Phase 2 — Link traversal pass:** After all nodes exist, Claude reads the full graph and proposes/resolves links. Links are written into frontmatter wikilinks (`implements`, `depends_on`, `governed_by`, `actors`, `related_to`).
Rationale: you can't reliably link a Feature to a Requirement that doesn't exist yet. Full graph visibility = more accurate linking.

---

### 4. Graph Storage — Markdown Frontmatter is Source of Truth
Wikilinks in frontmatter ARE the graph edges. No external graph database.
The `.md` files are the canonical, human-readable, Obsidian-compatible representation of the graph.

---

### 5. Index Layer — Cache for Relationships
A `graph.json` index lives alongside the vault (e.g. `vault/{project-slug}/.graph/index.json`).
It caches:
- All node metadata (type, name, status, path)
- All resolved edges (from frontmatter)
- Persona memberships (which personas appear on which nodes)
- Embedding vectors (for semantic linking suggestions)

The index is **rebuilt from source** at any time — it is never the source of truth.
Used for: context bundle generation, semantic search, cycle detection/validation, fast traversal without re-reading all files.

---

### 6. Personas — First-Class Nodes (formerly "Actors")
Personas are full graph nodes with their own `.md` files and frontmatter. They are richer than UML actors — they include goals, context, and usage patterns.
- `belongs_to`: Project (personas are project-scoped, not module-scoped)
- `goals`: list of what this persona is trying to achieve
- `context`: background, technical proficiency, usage patterns
- `related_to`: other Personas (e.g. Admin is a type of User)
- Referenced by: Feature, Module, User Story via `actors:` field

Personas serve as **semantic anchors** during the linking pass — shared personas between nodes is a strong signal to propose a relationship.

Authoring order: Personas are authored after Constraints, before Modules.

---

### 7. LLM Integration
Claude Code (or any LLM via the CLI) drives the interactive authoring session.
The CLI provides:
- The schema (node types, frontmatter schemas, authoring order)
- The vault path
- The current graph state (from index or live file reads)
The LLM handles: asking the user questions, authoring node content, proposing links, writing files via the CLI's file-write interface.

---

### 8. Context Bundle
After graph authoring is complete, the CLI can generate a `CONTEXT.md` for any Feature node.
Traversal: reads frontmatter at runtime (no index required for small graphs).
Output format: per the schema spec (`docs/superpowers/specs/2026-03-23-obsidian-project-graph-schema-design.md`).
This is the handoff artifact to spec-kit.

---

## Vault Folder Structure (updated with Personas)

```
vault/
  {project-slug}/
    Project - <name>.md
    goals/
      Goal - <name>.md
    .graph/
      index.json
    personas/
      Persona - <name>.md
    versions/
      Version - <name>.md
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

---

## Node Authoring Order (updated)

```
1. Project
2. Goal(s)           ← strategic objectives, right after Project
3. Persona(s)        ← who interacts with the system
4. Constraint(s)
5. Module(s)
6. Decision(s)
7. User Story(s)     ← written for Personas, within Modules
8. Epic(s)           ← groups Features into product-level work streams
9. Feature(s)
10. Version(s)       ← late-binding scope — assign after you know what exists
--- version assignment pass ---
11. Assign target_version to User Stories, Epics, and Features
--- linking pass ---
9. Resolve all edges, write wikilinks into frontmatter
10. Rebuild index
```

---

---

### 9. Embedding Strategy (deferred to v1.0)

**Status:** Deferred from MVP. For graphs under ~200 nodes, heuristic linking (shared personas, name mentions, module co-membership) is sufficient. Embeddings add API cost, latency, and infrastructure for minimal gain at small scale.

**When embeddings become valuable:** At ~200+ nodes where manual/rule-based traversal breaks down and semantic similarity meaningfully surfaces connections that heuristics miss.

**MVP linking approach (replaces embeddings):**
- Shared personas: two nodes referencing the same Persona → strong `related_to` candidate
- Name mentions: node body mentions another node's name → strong candidate
- Module co-membership: two Features in the same Module with shared User Stories → candidate `related_to`
- Constraint reach: a Constraint governing a Module applies to all Features in that Module

**Embedding details (for v1.0 implementation):**
- Batch after Phase 1, before linking pass. No per-node embedding during authoring.
- Each node embedded as a single unit (frontmatter + body). No chunking — nodes are small structured records.
- Preferred model: OpenAI `text-embedding-3-small`. No LangChain.
- Vectors stored in `graph.json` alongside node metadata.
- Cosine similarity > 0.82 → surface as link candidate, combined with heuristic signals above.

**Updated authoring flow (MVP):**
```
Phase 1:  Author all nodes → write .md files via recon-core
Phase 2a: Linking pass — use heuristics for link proposals (no embeddings)
Phase 2b: Write resolved wikilinks into frontmatter
Phase 2c: Rebuild full index
```

---

### 10. LLM as Conversational UI, Not Database Engine

The LLM's only job is to **chat with the user**, understand what they want to build, and **call structured tool functions** (`create_node(type, data)`). It does not write files directly.

**Why:**
- LLMs following prose validation rules is probabilistic — sometimes they get it right, sometimes they don't
- A `recon-core` library validates against JSON Schema before every write — deterministic, testable, rejects invalid data
- The agent instruction files become thin (conversation flow + question prompts), not thick (file format rules + validation logic)
- The same `recon-core` library works for scripted/CI use without any LLM

**Tool contract:**
| Tool | Purpose |
|---|---|
| `create_node(type, data)` | Validate + write new node to vault |
| `update_node(path, data)` | Validate + update existing node |
| `get_node(path)` | Read and parse a node file |
| `list_nodes(type?, status?)` | List nodes, optionally filtered |
| `resolve_links(projectDir)` | Check all wikilinks |
| `build_index(projectDir)` | Rebuild `graph.json` |
| `generate_context(featureName)` | Traverse graph, emit `CONTEXT.md` |

---

### 11. LLM Infers the Graph — The User Describes, Not Fills Forms

The schema defines **structure**, not a questionnaire. The user should never feel like they're filling out 10 forms with 8 fields each. The LLM's job is to have a natural conversation, extract structure from unstructured input, and **draft the entire graph** for the user to review.

**How it works in practice:**

User says: *"I'm building a payments platform — developers integrate it via API, merchants use a dashboard, and we need PCI compliance."*

LLM infers and drafts:
- 1 Project node (Payments Platform)
- 2-3 Goal nodes (extracted from context)
- 2 Persona nodes (Developer, Merchant)
- 1 Constraint (PCI DSS)
- 2 Module nodes (API, Dashboard)
- Potentially a Decision or two

Then presents: *"Here's what I inferred from what you told me. Anything wrong or missing?"*

**Key principles:**
- The user **describes** their project in natural language. The LLM **infers** the graph nodes.
- The schema is the target structure, not a form to fill out. Most fields can be inferred from a few sentences of natural conversation.
- The LLM drafts nodes in bulk, then asks for confirmation — not one field at a time.
- The user only needs to correct or add to what the LLM got wrong, not start from scratch.
- The authoring order in the schema (Project → Goals → Personas → ...) is the *data dependency order* for writes, not the conversation order. The LLM may extract multiple node types from a single user message.

**What the question prompts in schema files are for:**
The question prompts are fallback guidance for the LLM when it can't infer a required field — not a script to follow sequentially. If the user's description is rich enough, the LLM may never need to ask a single explicit question.

---

### 12. Context-Builder as MVP Gate

Before wiring up the LLM agent, prove the data model works by building and testing the context-builder standalone.

**Test:** Hand-author 5-10 vault files (Project, a couple Goals, a Persona, a Module, a User Story, a Feature). Run `generate_context("Feature - X")`. If the output `CONTEXT.md` is a correct, complete, useful handoff to spec-kit — the core premise works.

**Why this comes before the agent:**
- Forces the schema to be tested with real data before the LLM touches it
- The context-builder has zero LLM dependency — it's pure graph traversal
- If the output is bad, the problem is in the schema or traversal logic, not in prompt engineering

---

## Out of Scope (for now)

- Embedding pipeline (deferred to v1.0 — heuristic linking for MVP)
- Cross-project persona/node references
- Obsidian MCP plugin (nice-to-have for future live-vault features)
- UI / web interface
- Cycle detection UI (index can flag it, but no visual tooling yet)
