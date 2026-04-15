# Schema: Project

> Goal: the Project node is the root of the graph and the top of every CONTEXT bundle. Make it detailed enough that a reader can understand what is being built, why, and how success is measured — without reading any child node.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| type | `"project"` | auto-filled | |
| schema_version | `1` | auto-filled | |
| name | string | yes | canonical project name |
| status | `draft` / `active` / `complete` / `archived` | yes | default: `draft` |
| description | string | yes | one-line tagline, max 120 chars |

> `tags` is auto-managed by recon-core (`project/<slug>`); do not author it by hand.

## Body Sections

- `## Overview` — **REQUIRED.** 3-6 sentence expansion of the tagline. What the project does, who it's for, why it exists, what changes once it ships. Not a restatement of `description` — this is the "why we're building this" paragraph the CEO would read.

- `## Problem` — **REQUIRED.** The specific problem this project solves, in 2-4 sentences. Who has it, how they work around it today, and what breaks or becomes unbearable without this project.

- `## Success Metrics` — **REQUIRED.** 2-5 measurable outcomes that define "this project succeeded." Each bullet is falsifiable and named at the project level, not feature level. Adoption numbers, latency targets, error budgets, revenue, time-to-task.

- `## Scope` — **REQUIRED.** Two sub-lists: **In scope** (what this project covers) and **Out of scope** (what it explicitly does not). Parallel structure, verb-led bullets. Use Out of scope to foreclose tempting-but-deferred directions.

- `## Stakeholders` — **OPTIONAL but preferred.** Who cares about this project and in what role: sponsor, primary users (link to Personas), approvers, blocking reviewers. One line each.

- `## Background` — **OPTIONAL.** 2-5 sentences on origin: what triggered this project, what it replaces, prior attempts and why they didn't land. Include only if non-obvious.

- `## Assumptions` — **OPTIONAL.** What must be true for this project to make sense. Call these out so readers can challenge them. "Users already have an Obsidian vault." "Gemini embeddings remain available."

## Writing Guidance

- **Overview**: Declarative, present tense, plain English. Write for a stakeholder seeing the project for the first time.
- **Problem**: Concrete and specific. "Ops engineers lose 30 min per incident searching across four dashboards" beats "observability is hard."
- **Success Metrics**: Each bullet must be independently verifiable. Name the metric, the target, and (if useful) the measurement window.
- **Scope**: Parallel, verb-led. "Supports authoring 10 node types." "Does not include live sync between vaults."
- **Background**: Past tense, factual, terse.

## Question Prompts (fallback — use only if not inferable)

1. "What is this project called?"
2. "Give me a one-line summary (under 120 characters)."
3. "What problem does it solve, and for whom?"
4. "How will you know it succeeded?"
5. "What is explicitly out of scope?"
