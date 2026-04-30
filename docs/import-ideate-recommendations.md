# Recommendations: Open Questions for `/recon.import-ideate` and Project-Local Vault

These are the questions that survived the staff-engineer review and the structural decisions. Each has my recommended answer and the reasoning. Confirm before implementation; revisit before v1.1 if any prove wrong.

---

## Q1. Should `output/*.md` (the assembled ideate doc) attach to the Project node's body?

**Recommendation: yes — attach as a `body_sections` entry under `## Session Brief`.**

The ideate-generated doc is the most coherent prose summary the project has at that point — narrative overview, goals, personas, decisions, the works. Attaching it to the Project node:
- Gives Obsidian users a single click to read the full backstory.
- Gives Obsidian's outline / preview a meaningful Project page out of the box. (`generate_context_tool` only accepts Feature names today; extending it to Projects is out of scope for this spec.)
- Costs nothing — the file already exists; we just inline it.

Implementation: if `.ideate/output/*.md` exists, read the most recent file and pass its contents (minus the YAML frontmatter, if any) as `body_sections={"## Session Brief": "<contents>"}` when creating the Project node. Skip if the file is empty.

**Risk:** if the doc is huge (>50KB), Project node becomes unwieldy. Cap the inlined excerpt at the first 20KB and append `> _Truncated. Full document at .ideate/output/<name>.md_` if longer.

---

## Q2. Default similarity threshold for `find_similar_tool`?

**Recommendation: `0.75`.**

Empirical sweet spot from existing `recon-author/linking-pass.md` and Gemini text-embedding-004 norms: above 0.85 you mostly find duplicates (already handled by collision detection), below 0.65 you get noise. 0.75 surfaces "these are clearly related but distinct" — which is what `related_to` is for.

Hide the knob in v1. If users complain "too many" or "too few" suggestions, expose a setting in v1.1.

---

## Q3. Should `/recon` auto-detect `.ideate/` and route to import instead of the full interview?

**Recommendation: no. Keep `/recon` and `/recon.import-ideate` as separate commands.**

Reasons:
- The full `/recon` interview is for greenfield authoring — no prior context, conversational discovery. Different mental model from import.
- Auto-routing makes `/recon`'s behavior depend on hidden state (presence of `.ideate/`). That's a debuggability hazard.
- Users who want both flows already have them; the import command is one extra slash.
- This nudge is already shipped: `/recon`'s preflight prints `Detected an ideate session — run /recon.import-ideate to convert it into a graph instead of starting fresh.` when `.ideate/` exists and no `Project - *.md` is present (see `project-local-vault-spec.md` §3 step 4 and `plugin/recon-plugin/skills/recon/SKILL.md` Step 4). It is a one-line tip, not auto-execution.

**Revisit if:** users keep running `/recon` then asking how to import. The nudge line catches the obvious case.

---

## Q4. Should the recon graph be auto-added to `.gitignore`?

**Recommendation: no. Print a hint, do not auto-modify `.gitignore`.**

Reasons:
- `.gitignore` is the user's file. Modifying it without explicit consent is the kind of action the system prompt warns about.
- Different teams will want opposite defaults — some want the graph tracked as living docs, some want it ignored.
- A printed snippet the user can copy is fast enough.

The hint is already specced into `import-ideate-spec.md` §6.9. Keep it as text-only.

**Revisit if:** users frequently commit the graph by accident. Add an opt-in `--gitignore` flag in v1.1.

---

## Q5. Should ideate's `Status: draft` artifacts always carry forward as `status: draft` in recon, or be promoted?

**Recommendation: carry forward `draft` verbatim. Do not auto-promote.**

Reasons:
- `Status: draft` in ideate means "I wrote this down but didn't confirm." That signal is useful in recon — it tells future readers (and `generate_context_tool`) which nodes are firm.
- Auto-promoting on import would launder uncertainty and produce overconfident graphs.
- Users can promote via `/recon.add-feature` after review.

The final summary already lists draft nodes (§6.9) so the user knows what to revisit.

---

## Q6. Should `/recon` ever auto-replace the full-interview path entirely?

**Recommendation: no, not in v1.**

Same reasoning as Q3. Separate paths, separate mental models, lower coupling. Worth revisiting only if usage data shows >70% of `/recon` invocations happen post-ideate — at which point the interview path is mostly dead code anyway.

---

## Q7. Should `.recon-local.json` be one file or merged into a broader project marker? — *moot*

Obsolete in the current design. There is no `.recon-local.json` marker — see `project-local-vault-spec.md`. The vault is always the project root; per-project mode state is unnecessary because there is only one mode.

---

## Q8. What about ad-hoc mode ("ask me each time which vault to use")? — *moot*

Obsolete in the current design. There is no separate-vault mode and no `/recon-setup` command. Every `/recon` invocation silently auto-configures to the current project root.

---

## Summary of Recommended Defaults

| Question | Recommendation |
|---|---|
| Q1. Attach ideate output to Project body? | Yes, as `## Session Brief`, capped at 20KB |
| Q2. Default similarity threshold? | 0.75, hidden |
| Q3. Auto-detect `.ideate/` from `/recon`? | No; print a one-line nudge |
| Q4. Auto-edit `.gitignore`? | No; print hint only |
| Q5. Promote ideate drafts to active? | No; carry `draft` forward |
| Q6. Replace `/recon` interview with import? | No |
| Q7. `.recon-local.json` shape? | Moot — marker removed in single-mode vault |
| Q8. Ad-hoc vault mode? | Moot — single-mode vault, no `/recon-setup` |

If you want any of these flipped, tell me which and I'll update both specs to match. Otherwise I'll proceed to scaffold the skill against these defaults.
