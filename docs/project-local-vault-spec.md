# Spec: Project-Local Vault (Single Mode) for `/recon`

Recon's vault is **always the current project root**. There is no separate-vault option, no per-project mode marker, no divergence prompt, no setup command, and no persisted `VAULT_PATH`. Open Obsidian on your project; the recon graph lives next to your code, docs, and `.ideate/`.

> **Note on backwards compatibility:** Recon is pre-1.0 and we are explicitly **not** preserving backwards compatibility. Existing users with a configured separate vault will be silently re-pointed on the next `/recon` run (their old vault is left untouched on disk; recon just stops pointing at it). The `/recon-setup` / `/recon.setup` skill is removed entirely. Track breaking changes in `CHANGELOG.md`.

---

## 1. Goal

Drop every degree of freedom around "where does the graph live?" and every separate setup ceremony. The 95% case is: a user is working inside a project, runs `/recon`, and the graph appears next to their code. The 5% who maintained a central Obsidian vault for many projects no longer have first-class support — recon is now opinionated.

Vault layout is flat (one project per cwd). The project root contains `Project - <name>.md`, `goals/`, `personas/`, `constraints/`, `modules/`, `decisions/`, `user-stories/`, `epics/`, `features/`, and `.graph/`. There is **no** `<project-slug>/` subfolder.

---

## 2. Scope

**Affects**
- `/recon` (preflight is a silent auto-config plus a one-line tip if the optional Gemini key is missing).
- `/recon.add-feature` (same silent auto-config preflight as `/recon`, fully self-contained).
- `/recon.import-ideate` (specced for this default — keep aligned; see `import-ideate-spec.md` §6.1).

**Removed**
- `/recon-setup` / `/recon.setup` skill — deleted entirely.
- Persistence of `VAULT_PATH` to `~/.claude/settings.json`. Each skill's preflight calls `configure_vault_tool` afresh; that's the single source of truth.

**Does NOT affect**
- `recon-core` MCP tools — `configure_vault_tool` accepts any path. No code change needed.
- The graph schema, node types, or per-type folder layout.

---

## 3. New Behavior

### `/recon` (and `/recon.add-feature`) preflight

1. Resolve project root: `git rev-parse --show-toplevel 2>/dev/null || pwd`. Call this `<project_root>`.
2. Call `configure_vault_tool(vault_path="<project_root>")`. This updates the MCP server's in-memory `PROJECT_DIR` for the rest of the session. **Must succeed before any other recon tool call.**
3. Check `GEMINI_API_KEY` in shell env. If missing, print exactly one notice; otherwise print nothing:
   `Tip: GEMINI_API_KEY is not set — semantic linking is disabled (heuristic linking still works). To enable, add export GEMINI_API_KEY=your-key to your shell rc (~/.zshrc or ~/.bashrc), then restart Claude Code. Free key: https://aistudio.google.com/apikey`
4. (`/recon` only) Check whether `<project_root>/.ideate/` exists AND no `Project - *.md` is present. If both conditions hold, print one line:
   `Tip: Detected an ideate session — run /recon.import-ideate to convert it into a graph instead of starting fresh.`
5. Proceed to the authoring/maintenance flow. No prompts.

The preflight is silent on the happy path. There is no "we configured X" announcement, no menu, no marker file, no separate setup command, no settings.json write.

### `/recon.import-ideate`

Same preflight as `/recon`, plus the import-specific flow. See `import-ideate-spec.md` §6.1.

---

## 4. Why No Persistence?

Earlier drafts of this spec persisted `VAULT_PATH` to `~/.claude/settings.json` so the MCP server would bootstrap to the same directory on next launch. That created two problems:

1. **Concurrent-session race.** Two Claude Code sessions in different repos race on the same settings.json file; whichever writes last wins, and the loser's MCP server boots pointing at the wrong project. (The in-memory `configure_vault_tool` is session-isolated and unaffected — it's only the persisted file that races.)
2. **Quoting fragility.** Inlining a project path into a Python string literal breaks on paths containing single quotes, control characters, or other shell-unfriendly bytes.

The fix: **don't persist anything**. Every recon-touching skill (`/recon`, `/recon.add-feature`, `/recon.import-ideate`) calls `configure_vault_tool` in its preflight. That's the only thing the MCP server needs for this session. The `VAULT_PATH` env var still exists for users who want to set it manually, but we don't write to it.

---

## 5. Gemini API Key — Shell Env Var

The MCP server reads `GEMINI_API_KEY` from its environment via `os.environ.get(...)`. Claude Code spawns the MCP server as a child process, which inherits Claude Code's env, which inherits the shell rc. So the canonical place for the key is the user's shell rc:

```bash
# In ~/.zshrc or ~/.bashrc
export GEMINI_API_KEY="your-key"
```

Then restart Claude Code so the MCP server picks it up. Free key: <https://aistudio.google.com/apikey>.

We do **not** write the key to `~/.claude/settings.json`. There is no `/recon-setup` skill. The `/recon` preflight checks `$GEMINI_API_KEY` and surfaces a one-line tip when missing — that's the entire UX for this knob.

---

## 6. Why This Default Is Right

- **One Obsidian config per project.** Users open Obsidian on their project; they don't want to maintain a parallel vault path elsewhere.
- **`.ideate/` and the recon graph are siblings.** The bridge skill (`/recon.import-ideate`) becomes a flat, in-place writer.
- **Code, docs, and graph travel together.** A project's graph rides along with the repo.
- **Symmetric with how `.ideate/` works.** Ideate already writes to cwd. Aligning recon removes a mental-model mismatch.
- **No degrees of freedom = no preflight UX, no setup command, no race-prone persistence.** The single optional knob (Gemini key) is a shell env var, surfaced lazily by `/recon` when missing.

The cost: `goals/`, `features/`, etc. live directly at the repo root. Users who want them git-ignored do so explicitly; users who want them tracked do nothing.

---

## 7. Resolved Decisions

- **No backwards compat** — pre-1.0; existing separate-vault users are silently re-pointed.
- **Single mode** — every `/recon` invocation treats the project root (git toplevel || cwd) as the vault. No menu, no marker, no per-project decision.
- **No setup command** — `/recon-setup` is deleted.
- **No persisted `VAULT_PATH`** — `configure_vault_tool` is the single source of truth, called fresh on every preflight. Eliminates the concurrent-session race and the path-quoting bug.
- **Gemini key is a shell env var** — never written to settings.json by recon. `/recon` prints exactly one tip when missing.
- **Self-contained skills** — `/recon.add-feature` and `/recon.import-ideate` inline their preflights; they do not delegate to `/recon`'s SKILL.md by reference (the LLM only has the invoked skill in context at runtime).

---

## 8. Acceptance Criteria

1. Running `/recon` in any directory configures `VAULT_PATH` to `git rev-parse --show-toplevel` (or `pwd` if not in a git repo) via `configure_vault_tool` and proceeds to the authoring session without prompting.
2. Running `/recon` with `GEMINI_API_KEY` unset prints exactly one tip line pointing at the shell rc; running `/recon` with it set prints nothing extra.
3. Running `/recon` in a directory containing a `.ideate/` session and no existing `Project - *.md` prints a one-line nudge to use `/recon.import-ideate`.
4. There is no `/recon-setup` skill — invoking it shows Claude Code's "skill not found" behavior.
5. Two concurrent Claude Code sessions in different repos do not race on `~/.claude/settings.json` (because no skill writes `VAULT_PATH` to it). `git diff ~/.claude/settings.json` shows no recon-induced changes after a `/recon` run.
6. Re-running `/recon` after moving to a different project root re-points the in-memory vault silently.
7. `/recon.add-feature` and `/recon.import-ideate` (when shipped) each contain a complete, self-contained preflight — they do not say "see `/recon` SKILL.md for the snippet."

---

## 9. Notes

- No `.recon-local.json` marker exists in this design. If older versions left one behind, future skills should ignore it.
- The recognition heuristic (`.git/`, `package.json`, etc.) from earlier drafts is gone — there is no branch that depends on "is this a real project?" anymore.
- See `import-ideate-recommendations.md` for resolved questions on the import flow specifically.
- **Edge case (acknowledged, not guarded):** running `/recon` from `$HOME` or `/tmp` will write `Project - *.md` and the type folders directly there. This is a known footgun; the mitigation today is "the user invoked recon there deliberately." A future iteration may add a refusal when `<project_root>` equals `$HOME` or has fewer than two path components.
