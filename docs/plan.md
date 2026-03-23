# Feedback Tasklist

**Date:** 2026-03-23
**Source:** Staff Engineer Review (SE-*) + Product Review (PR-*) + Gemini External Review

---

## Phase A: Schema & Terminology Fixes (do first — changes propagate everywhere)

- [x] **T1 (PR-3): Rename Requirement -> User Story**
  - Rename node type from `requirement` to `user-story`
  - Replace `requirement_type: functional | non-functional` with: all user stories are functional; NFRs become Constraints
  - Update frontmatter schema to use User Story format ("As a [persona], I want [goal], so that [benefit]")
  - Add `acceptance_criteria` list field (addresses PR-4)
  - Update: schema spec, brainstorm decisions doc, implementation plan

- [x] **T2 (PR-5): Enrich Actor -> Persona**
  - Add optional `goals` (list) and `context` (string) fields to Actor schema
  - Consider renaming type from `actor` to `persona` (decide and document)
  - Update: schema spec, brainstorm decisions doc, implementation plan

- [x] **T3 (PR-1): Add Goal/Objective node type**
  - Create a new `goal` or `objective` node type (belongs_to: Project)
  - Features and User Stories should be traceable back to Goals via a `supports` edge
  - Replace flat `goals` list on Project with links to Goal nodes
  - Update: schema spec, brainstorm decisions doc, implementation plan

- [x] **T4 (PR-2): Add Epic node type**
  - Create `epic` node type (belongs_to: Module, target_version: Version)
  - Features belong to an Epic (optional) for work grouping
  - Modules remain technical decomposition; Epics capture product-level work streams
  - Update: schema spec, brainstorm decisions doc, implementation plan

- [x] **T5 (PR-6): Make target_version optional, adjust authoring order**
  - Change `target_version` from required to optional on Feature and User Story
  - Update authoring order to: Project -> Personas -> Goals -> Modules -> User Stories -> Constraints -> Decisions -> Epics -> Features -> Version assignment (late-binding)
  - Update: schema spec, brainstorm decisions doc, implementation plan

## Phase B: Technical Foundation (do before rewriting agent docs)

### Step 1: Data Layer

- [ ] **T6 (SE-1): Create JSON Schema definitions for all node types**
  - Write a `.schema.json` file for each node type (project, goal, version, constraint, persona, module, decision, user-story, epic, feature)
  - These are the machine-readable source of truth
  - Agent prompt files reference these schemas, not the other way around

### Step 2: Core Engine

- [ ] **T7a (SE-3): Build recon-core library — parse, write, validate, index**
  - `parseFrontmatter(filePath)` -> typed node metadata
  - `writeNode(type, data)` -> writes validated .md file to vault (rejects invalid data)
  - `validateNode(type, data)` -> validates against JSON Schema
  - `resolveLinks(projectDir)` -> returns valid + broken wikilinks
  - `buildIndex(projectDir)` -> generates graph.json
  - Target: ~200-300 lines TypeScript or Python
  - **Key principle:** The LLM never writes files directly. It calls structured tool functions (`create_node`, `update_node`) which go through recon-core. Graph-core is the write path; the LLM is the conversational UI.

### Step 3: Handoff Generator (MVP gate)

- [ ] **T7b: Build context-builder as standalone proof-of-value**
  - `generateContext(featureName, projectDir)` -> generates CONTEXT.md
  - Traverses the graph: Feature -> User Stories -> Module -> Personas -> Goals -> Constraints -> Decisions -> Dependencies
  - **This is the MVP gate.** If we can hand-author a few vault files and generate a flawless CONTEXT.md for spec-kit, the core premise works — no LLM needed yet.
  - Test with manually created vault files before wiring up the agent.

### Step 4: Remaining Foundation

- [ ] **T8 (SE-2): Replace embedding pipeline with heuristic linker for MVP**
  - Remove Phase 2a (batch embed) from MVP scope
  - Implement rule-based link proposal: shared personas, same module, name-mention matching, module co-membership
  - Document embeddings as a v1.0 enhancement
  - Update: schema spec, brainstorm decisions doc, implementation plan

- [ ] **T9 (SE-4 + Gemini): Document known gaps and risks for POC**
  - Add a "Known Limitations" section to the spec
  - Call out: no session resume, no idempotent writes, no partial vault detection
  - **Add friction risk (Gemini):** 10 node types is a lot of interviewing. The authoring session must use progressive disclosure — start with Project/Goals/Personas, let the user go deeper only as needed. If it feels like doing taxes, people bail.
  - Mark these as v1.0 items

## Phase C: Rewrite Agent Docs (after A and B are done)

- [ ] **T10: Rewrite implementation plan**
  - Incorporate all schema changes from Phase A
  - Reorder tasks: JSON schemas (Step 1) -> recon-core (Step 2) -> context-builder (Step 3) -> agent docs (Step 4) -> dog-food
  - Remove embedding tasks from MVP scope
  - Update chunk/task structure to reflect new build order

- [ ] **T11: Rewrite agent instruction files**
  - Rewrite `recon-author/AGENT.md` with updated authoring order and tool-calling contract
  - The LLM's job: interview the user, call `create_node(type, data)` — NOT write files
  - Rewrite all schema prompt files to reference JSON Schemas and use new terminology
  - Rewrite `linking-pass.md` to use heuristic linker instead of embeddings
  - Remove `embedding.md` from MVP (keep as v1.0 reference)
  - Update `context-bundle.md` for new node types (Goal, Epic, User Story)

## Phase D: Prove It (after C)

- [ ] **T12: Dog-food run — hand-author vault, generate context**
  - Manually author vault files for `recon` itself using the schemas
  - Run context-builder to generate CONTEXT.md for a Feature
  - Verify the output is correct and useful as a spec-kit handoff
  - This proves the data model before wiring up the LLM agent

- [ ] **T13: Dog-food run — LLM-driven authoring session**
  - Run an interactive session via `/recon` skill + MCP server
  - Validate that the LLM can author nodes via `create_node` and the output matches hand-authored quality
  - Distribution setup: skill install (`skill/recon.md`) and MCP server config (`deploysquad_recon_core/mcp_server.py`) are part of the setup

---

## Dependency Graph

```
T1 (User Story) ─┐
T2 (Persona)    ─┤
T3 (Goal)       ─├─> T6 (JSON Schemas) ─> T7a (recon-core) ─> T7b (context-builder / MVP gate)
T4 (Epic)       ─┤                                          ─> T8 (Heuristic linker)
T5 (Authoring)  ─┘                                          ─> T9 (Known gaps + friction)
                                                                    │
                                            T7b + T8 + T9 ─> T10 (Rewrite plan) ─> T11 (Rewrite agent docs)
                                                                                          │
                                                              T11 ─> T12 (Hand-author dog-food) ─> T13 (LLM dog-food)
```

Phase A: Schema fixes (independent, parallelizable) — **DONE**
Phase B: Technical foundation (sequential steps 1-4) — **DONE** (212 tests, recon-core library complete)
Phase C: Rewrite agent docs (depends on A + B) — **DONE** (AGENT.md + 10 schema files + phase files)
Phase D: Prove it — hand-authored first, then LLM-driven (depends on C)
