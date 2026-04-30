# Changelog

All notable changes to recon are tracked in this file.

Recon is pre-1.0. We do **not** preserve backwards compatibility — when a clean design needs core changes or behavior shifts, we make them. Existing user vaults are not protected; users re-running setup may see different defaults.

## 0.3.0 — 2026-04-30

### Added — `/recon.import-ideate` bridge skill

A new skill that converts a completed `/ideate` session into a fully-populated Recon graph at the project root. Reads `.ideate/` artifacts as natural-language context, plans the graph, confirms with the user, then writes validated nodes via `recon-core` MCP tools.

- **One-shot import** from `.ideate/session.md`, `.ideate/main.md`, `.ideate/artifacts/*.md`, and `.ideate/output/*.md`. Branches (`.ideate/branches/`) are explicitly not consumed — they are pre-merge thread logs.
- **Auto-stub of the Project node** from `session.md`'s elevator pitch, with the most recent `.ideate/output/*.md` inlined as a `Session Brief` body section (capped at 20KB).
- **Inferred Epics and User Stories** — Epics cluster Features by shared Goal; User Stories are one per Feature × primary Persona. No combinatorial explosion.
- **Plan-then-confirm gate** before any write. Absolute target paths shown in the plan table. `cancel` exits cleanly with no side effects.
- **Per-node duplicate prompt** (`skip / update / rename`) — no "apply to all" shortcut in v1.
- **Resume after partial failure** via `.ideate/recon-import-state.json` sidecar. State entries are `created` / `draft` / `failed`; `created` is skipped on re-run, the others are retried.
- **Schema-failure recovery** — up to 3 retries per node; the 4th failure writes the node as `status: draft` with whatever frontmatter passes validation, logs the error, and continues. Never aborts mid-run.
- **Similarity pass** via `embed_nodes_tool` + `find_similar_tool` (threshold 0.75) when `GEMINI_API_KEY` is set; gracefully skipped with a one-line notice otherwise. `related_to` writes use a read-union-write sequence (the underlying `update_node` shallow-spreads updates and would otherwise replace lists).
- **Single-project guard** — a second import targeting a different project name in the same directory hard-refuses.
- **`.gitignore` hint printed at the end** — never auto-edits `.gitignore`.

Spec: `docs/import-ideate-spec.md`. Resolved questions: `docs/import-ideate-recommendations.md`.

### Changed — `configure_vault_tool` docstring (recon-core)

Updated the MCP tool docstring to reflect the no-persistence rule. Previously instructed callers to also persist to `settings.json`; now explicitly forbids it (with a pointer to `project-local-vault-spec.md` §4 for the rationale). No behavior change — only the documented contract.

### Changed — single-mode vault, no setup command, no persistence, env-var Gemini key

Recon no longer asks where to put the graph, no longer ships a setup skill, and no longer persists `VAULT_PATH` to `~/.claude/settings.json`. The vault is **always** the current project root, resolved as `git rev-parse --show-toplevel || pwd`. The graph (`Project - <name>.md`, `goals/`, `features/`, ...) lives directly under the project root, alongside code, docs, and `.ideate/`. Layout is flat — no `<project-slug>/` subfolder.

- **`/recon` preflight is silent.** It resolves the project root, calls `configure_vault_tool`, optionally prints two one-line tips (Gemini key missing; ideate session detected), and proceeds. No prompts, no menus, no markers, no settings.json writes.
- **No persistence of `VAULT_PATH`.** Earlier drafts wrote `VAULT_PATH` to `~/.claude/settings.json` on every `/recon` run. That created a race when two Claude Code sessions ran against different repos concurrently, and the inlined-string-literal write was vulnerable to project paths containing single quotes. Both bugs are gone — `configure_vault_tool` is now the only place the vault path lives, and it's session-isolated in MCP server memory.
- **Gemini key lives in the shell env, not settings.json.** The MCP server reads `GEMINI_API_KEY` from `os.environ` and inherits it via Claude Code → shell. Users set `export GEMINI_API_KEY=...` in `~/.zshrc` (or equivalent) and restart Claude Code. The `/recon` preflight prints a one-line tip with the exact shell-rc instruction when the env is unset.
- **`/recon` adds an ideate-session nudge.** When `.ideate/` exists at the project root and there is no `Project - *.md` yet, `/recon` prints one line pointing at `/recon.import-ideate`.
- **`/recon.add-feature` is self-contained.** It no longer says "see `/recon` SKILL.md for the snippet." It inlines its own preflight — resolve project root, `configure_vault_tool`, Gemini-env check — so the LLM has everything it needs in one file. Also fixed: it now calls `embed_nodes_tool()` with no args (the MCP signature) instead of the previously-incorrect `embed_nodes_tool(project_dir)`.
- **`/recon` Context Bundle output path** — was documented as `{vault}/{project-slug}/features/CONTEXT - {name}.md`; now correctly `{vault}/features/CONTEXT - {name}.md`. Matches the flat layout and the in-skill "How to Call" block.
- **No `recon-core` change required.** `configure_vault_tool` already accepts any directory and treats it as the project root. `embed_nodes_tool()` already takes no args.

**Removed:**

- The `/recon-setup` (a.k.a. `/recon.setup`) skill — deleted entirely.
- Persistence of `VAULT_PATH` to `~/.claude/settings.json`.
- Separate-vault mode and the two-option setup menu.
- The `.recon-local.json` per-project marker.
- The "recognizable project root" heuristic (`.git/`, `package.json`, etc.).
- The `keep / switch` divergence prompt.
- The `{vault}/{project-slug}/` folder layout in skill docs.

**Breaking changes:**

- **`/recon-setup` no longer exists.** Users who previously bookmarked or scripted it will need to remove those references. The optional Gemini key now lives in the shell env (`export GEMINI_API_KEY=...` in `~/.zshrc` or `~/.bashrc`); `/recon` prints the exact instruction when the key is missing.
- **`VAULT_PATH` is no longer written to `~/.claude/settings.json`.** Users who previously relied on the persisted value (e.g., for tooling outside recon that reads settings.json) should set it manually if needed. Recon itself does not require it — every preflight configures the path fresh.
- **Separate vaults are silently dropped on next `/recon` run.** Users with a previously configured central vault will be re-pointed at the project root. The old vault is left untouched on disk — recon just stops writing there. Users who want their old graph re-imported should `git mv` (or copy) it into the new project root.

Spec: `docs/project-local-vault-spec.md`.
