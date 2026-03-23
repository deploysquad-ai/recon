#!/usr/bin/env python3
"""Dog-food: author obsidian-spec-graph vault using recon-core.

Creates a complete vault describing THIS project using the graph schema,
then verifies all links resolve and generates CONTEXT.md output.
"""
import shutil
import sys
from pathlib import Path

# Ensure recon-core is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "recon-core" / "src"))

from deploysquad_recon_core import (
    create_node,
    update_node,
    get_node,
    resolve_links,
    build_index,
    generate_context,
)
from deploysquad_recon_core.index import write_index
from deploysquad_recon_core.vault.paths import node_filepath

PROJECT_DIR = Path(__file__).parent.parent / "dogfood-vault" / "obsidian-spec-graph"


def main():
    # Clean slate for idempotency
    if PROJECT_DIR.exists():
        shutil.rmtree(PROJECT_DIR)
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1. Project ──────────────────────────────────────────────
    create_node("project", {
        "name": "obsidian-spec-graph",
        "status": "active",
        "description": "CLI tool for building structured project graphs in Obsidian vaults via LLM conversation",
    }, PROJECT_DIR)
    print("[+] Project: obsidian-spec-graph")

    # ── 2. Goals ────────────────────────────────────────────────
    create_node("goal", {
        "name": "Structured Graph Authoring",
        "status": "active",
        "belongs_to": "[[Project - obsidian-spec-graph]]",
    }, PROJECT_DIR, body_sections={
        "Description": "Enable users to build structured project graphs through natural conversation with an LLM.",
        "Success Criteria": "- Users can describe a project in natural language\n- LLM infers and creates all 10 node types\n- Graph passes link validation with 0 broken links",
    })
    print("[+] Goal: Structured Graph Authoring")

    create_node("goal", {
        "name": "Spec-Kit Handoff",
        "status": "active",
        "belongs_to": "[[Project - obsidian-spec-graph]]",
    }, PROJECT_DIR, body_sections={
        "Description": "Generate CONTEXT.md files that serve as complete handoff artifacts to spec-kit.",
        "Success Criteria": "- CONTEXT.md includes Project, Goals, Module, User Stories, Constraints, Decisions\n- Output starts with context_bundle_version comment\n- Missing optional sections omitted gracefully",
    })
    print("[+] Goal: Spec-Kit Handoff")

    # ── 3. Personas ─────────────────────────────────────────────
    create_node("persona", {
        "name": "Product Developer",
        "status": "active",
        "belongs_to": "[[Project - obsidian-spec-graph]]",
        "goals": [
            "Define project structure quickly",
            "Get useful spec artifacts",
        ],
        "context": "Technical user comfortable with CLI tools, wants to capture product decisions in a structured format.",
    }, PROJECT_DIR)
    print("[+] Persona: Product Developer")

    create_node("persona", {
        "name": "LLM Agent",
        "status": "active",
        "belongs_to": "[[Project - obsidian-spec-graph]]",
        "goals": [
            "Infer graph structure from natural language",
            "Call recon-core tools accurately",
        ],
        "context": "AI agent loaded with AGENT.md + schema files, interacts via tool calls.",
    }, PROJECT_DIR)
    print("[+] Persona: LLM Agent")

    # ── 4. Constraints ──────────────────────────────────────────
    create_node("constraint", {
        "name": "Markdown Source of Truth",
        "status": "active",
        "belongs_to": "[[Project - obsidian-spec-graph]]",
    }, PROJECT_DIR, body_sections={
        "Description": "The vault's .md files ARE the graph. No separate database, no lock-in.",
        "Scope": "All modules — every read/write must go through .md files.",
    })
    print("[+] Constraint: Markdown Source of Truth")

    create_node("constraint", {
        "name": "Obsidian Compatibility",
        "status": "active",
        "belongs_to": "[[Project - obsidian-spec-graph]]",
    }, PROJECT_DIR, body_sections={
        "Description": "Plain markdown + YAML frontmatter + wikilinks — all native Obsidian features.",
        "Scope": "File format and naming conventions.",
    })
    print("[+] Constraint: Obsidian Compatibility")

    # ── 5. Modules ──────────────────────────────────────────────
    create_node("module", {
        "name": "Graph Core",
        "status": "active",
        "belongs_to": "[[Project - obsidian-spec-graph]]",
        "actors": ["[[Persona - LLM Agent]]"],
        "governed_by": ["[[Constraint - Markdown Source of Truth]]"],
    }, PROJECT_DIR, body_sections={
        "Description": "Python library for reading, writing, validating, and indexing vault files. Pydantic v2 models, atomic writes, wikilink resolution.",
    })
    print("[+] Module: Graph Core")

    create_node("module", {
        "name": "Context Builder",
        "status": "active",
        "belongs_to": "[[Project - obsidian-spec-graph]]",
        "actors": ["[[Persona - Product Developer]]"],
        "governed_by": ["[[Constraint - Markdown Source of Truth]]"],
    }, PROJECT_DIR, body_sections={
        "Description": "Traverses the graph from a Feature node and generates CONTEXT.md handoff artifacts for spec-kit.",
    })
    print("[+] Module: Context Builder")

    create_node("module", {
        "name": "Agent CLI",
        "status": "active",
        "belongs_to": "[[Project - obsidian-spec-graph]]",
        "actors": [
            "[[Persona - Product Developer]]",
            "[[Persona - LLM Agent]]",
        ],
        "depends_on": ["[[Module - Graph Core]]"],
    }, PROJECT_DIR, body_sections={
        "Description": "Interactive CLI that loads agent instruction files and wires recon-core as tool functions for the LLM.",
    })
    print("[+] Module: Agent CLI")

    # ── 6. Decisions ────────────────────────────────────────────
    create_node("decision", {
        "name": "Two-Phase Authoring",
        "status": "active",
        "belongs_to": "[[Project - obsidian-spec-graph]]",
    }, PROJECT_DIR, body_sections={
        "Decision": "Phase 1 authors all nodes, Phase 2 resolves links. Can't reliably link to nodes that don't exist yet.",
        "Rationale": "Forward-reference problem — full graph visibility produces more accurate linking.",
    })
    print("[+] Decision: Two-Phase Authoring")

    create_node("decision", {
        "name": "Heuristic Linking for MVP",
        "status": "active",
        "belongs_to": "[[Project - obsidian-spec-graph]]",
    }, PROJECT_DIR, body_sections={
        "Decision": "Use shared personas, name mentions, and module co-membership for link proposals. No embeddings.",
        "Rationale": "Embeddings add cost/complexity for graphs under 200 nodes where heuristics work fine.",
    })
    print("[+] Decision: Heuristic Linking for MVP")

    create_node("decision", {
        "name": "LLM as Conversational UI",
        "status": "active",
        "belongs_to": "[[Module - Agent CLI]]",
    }, PROJECT_DIR, body_sections={
        "Decision": "The LLM calls create_node(type, data) — it never writes files directly. recon-core validates.",
        "Rationale": "Deterministic validation beats probabilistic LLM compliance with prose rules.",
    })
    print("[+] Decision: LLM as Conversational UI")

    # ── 7. User Stories ─────────────────────────────────────────
    create_node("user-story", {
        "name": "Author Project Graph",
        "status": "active",
        "belongs_to": "[[Module - Agent CLI]]",
        "actors": ["[[Persona - Product Developer]]"],
        "acceptance_criteria": [
            "User can describe project in natural language",
            "LLM infers and drafts nodes in bulk",
            "User reviews and confirms before write",
            "All 10 node types can be authored",
        ],
        "supports": ["[[Goal - Structured Graph Authoring]]"],
    }, PROJECT_DIR, body_sections={
        "Story": "As a Product Developer, I want to describe my project in natural language so that the LLM builds a structured graph for me.",
    })
    print("[+] User Story: Author Project Graph")

    create_node("user-story", {
        "name": "Generate Context Bundle",
        "status": "active",
        "belongs_to": "[[Module - Context Builder]]",
        "actors": ["[[Persona - Product Developer]]"],
        "acceptance_criteria": [
            "Context includes Project, Goals, Module, User Stories, Constraints, Decisions",
            "Output starts with context_bundle_version comment",
            "Missing optional sections omitted gracefully",
        ],
        "supports": ["[[Goal - Spec-Kit Handoff]]"],
    }, PROJECT_DIR, body_sections={
        "Story": "As a Product Developer, I want to generate a CONTEXT.md for any Feature so that I can hand it off to spec-kit.",
    })
    print("[+] User Story: Generate Context Bundle")

    create_node("user-story", {
        "name": "Validate Node Data",
        "status": "active",
        "belongs_to": "[[Module - Graph Core]]",
        "actors": ["[[Persona - LLM Agent]]"],
        "acceptance_criteria": [
            "Invalid data rejected with clear error message",
            "Type field enforced via Literal types",
            "Wikilink format validated via regex pattern",
        ],
        "supports": ["[[Goal - Structured Graph Authoring]]"],
    }, PROJECT_DIR, body_sections={
        "Story": "As an LLM Agent, I want node data validated before writing so that the vault never contains invalid files.",
    })
    print("[+] User Story: Validate Node Data")

    # ── 8. Epics ────────────────────────────────────────────────
    create_node("epic", {
        "name": "Graph Authoring System",
        "status": "active",
        "belongs_to": "[[Module - Agent CLI]]",
        "supports": ["[[Goal - Structured Graph Authoring]]"],
    }, PROJECT_DIR, body_sections={
        "Description": "End-to-end interactive graph authoring via LLM conversation.",
    })
    print("[+] Epic: Graph Authoring System")

    create_node("epic", {
        "name": "Handoff Pipeline",
        "status": "active",
        "belongs_to": "[[Module - Context Builder]]",
        "supports": ["[[Goal - Spec-Kit Handoff]]"],
    }, PROJECT_DIR, body_sections={
        "Description": "Generate spec-kit-ready CONTEXT.md files from the graph.",
    })
    print("[+] Epic: Handoff Pipeline")

    # ── 9. Features ─────────────────────────────────────────────
    create_node("feature", {
        "name": "Create Node via Tool Call",
        "status": "active",
        "belongs_to": "[[Module - Graph Core]]",
        "implements": ["[[User Story - Validate Node Data]]"],
        "actors": ["[[Persona - LLM Agent]]"],
        "supports": ["[[Goal - Structured Graph Authoring]]"],
        "epic": "[[Epic - Graph Authoring System]]",
        "governed_by": ["[[Constraint - Markdown Source of Truth]]"],
    }, PROJECT_DIR, body_sections={
        "Description": "create_node(type, data) validates against Pydantic models and writes an atomic .md file.",
        "Scope": "All 10 node types, frontmatter validation, atomic file writes.",
    })
    print("[+] Feature: Create Node via Tool Call")

    create_node("feature", {
        "name": "Generate CONTEXT.md",
        "status": "active",
        "belongs_to": "[[Module - Context Builder]]",
        "implements": ["[[User Story - Generate Context Bundle]]"],
        "actors": ["[[Persona - Product Developer]]"],
        "supports": ["[[Goal - Spec-Kit Handoff]]"],
        "epic": "[[Epic - Handoff Pipeline]]",
        "governed_by": ["[[Constraint - Markdown Source of Truth]]"],
    }, PROJECT_DIR, body_sections={
        "Description": "generate_context(feature_name) traverses Feature -> Module -> Project, collecting User Stories, Constraints, Decisions, Goals.",
        "Scope": "Graph traversal, section rendering, graceful handling of missing optional data.",
    })
    print("[+] Feature: Generate CONTEXT.md")

    create_node("feature", {
        "name": "Interactive Authoring Session",
        "status": "active",
        "belongs_to": "[[Module - Agent CLI]]",
        "implements": ["[[User Story - Author Project Graph]]"],
        "actors": [
            "[[Persona - Product Developer]]",
            "[[Persona - LLM Agent]]",
        ],
        "supports": ["[[Goal - Structured Graph Authoring]]"],
        "epic": "[[Epic - Graph Authoring System]]",
        "depends_on": ["[[Feature - Create Node via Tool Call]]"],
    }, PROJECT_DIR, body_sections={
        "Description": "CLI loads AGENT.md + schema files, wires recon-core as tools, runs conversation loop.",
        "Scope": "Phase 1 (authoring) + Phase 2 (version assignment + heuristic linking).",
    })
    print("[+] Feature: Interactive Authoring Session")

    # ── 10. Version ─────────────────────────────────────────────
    create_node("version", {
        "name": "MVP",
        "status": "active",
        "belongs_to": "[[Project - obsidian-spec-graph]]",
        "sequence": 1,
    }, PROJECT_DIR, body_sections={
        "Description": "Core recon-core library + context builder + agent instruction files. No embeddings, no CLI yet.",
    })
    print("[+] Version: MVP")

    # ── Version Assignment Pass ─────────────────────────────────
    print("\n[*] Assigning target_version: [[Version - MVP]] ...")

    # User Stories
    for us_name in ["Author Project Graph", "Generate Context Bundle", "Validate Node Data"]:
        fp = node_filepath("user-story", us_name, PROJECT_DIR)
        update_node(fp, {"target_version": "[[Version - MVP]]"})
        print(f"    Updated User Story: {us_name}")

    # Epics
    for epic_name in ["Graph Authoring System", "Handoff Pipeline"]:
        fp = node_filepath("epic", epic_name, PROJECT_DIR)
        update_node(fp, {"target_version": "[[Version - MVP]]"})
        print(f"    Updated Epic: {epic_name}")

    # Features
    for feat_name in ["Create Node via Tool Call", "Generate CONTEXT.md", "Interactive Authoring Session"]:
        fp = node_filepath("feature", feat_name, PROJECT_DIR)
        update_node(fp, {"target_version": "[[Version - MVP]]"})
        print(f"    Updated Feature: {feat_name}")

    # ── Verification ────────────────────────────────────────────
    print("\n[*] Verifying links ...")
    result = resolve_links(PROJECT_DIR)
    valid_count = len(result["valid"])
    broken_count = len(result["broken"])
    print(f"    Valid links: {valid_count}, Broken: {broken_count}")
    if broken_count > 0:
        for b in result["broken"]:
            print(f"    BROKEN: {b}")
        sys.exit(1)

    # Build index
    print("\n[*] Building index ...")
    index = build_index(PROJECT_DIR)
    write_index(index, PROJECT_DIR)
    print(f"    Index: {len(index['nodes'])} nodes")

    # Generate CONTEXT.md for features
    for feature_name in ["Create Node via Tool Call", "Generate CONTEXT.md", "Interactive Authoring Session"]:
        ctx = generate_context(feature_name, PROJECT_DIR)
        print(f"\n{'='*60}")
        print(f"CONTEXT.md for '{feature_name}':")
        print(f"{'='*60}")
        print(ctx)

    print("\n[OK] Dog-food vault authored successfully!")


if __name__ == "__main__":
    main()
