# CLAUDE.md — recon-plugin

## What This Is

The Claude Code plugin package for recon. Installed via `/plugin install` or the custom marketplace. Bundles the skill files that users invoke as `/recon` and `/recon.add-feature`.

## Structure

```
recon-plugin/
  .claude-plugin/
    plugin.json          # Plugin metadata (name, version, author, description)
  skills/
    recon/
      SKILL.md           # /recon skill — full graph authoring session
    recon-add-feature/
      SKILL.md           # /recon.add-feature skill — add/update nodes in existing graph
```

## How It Works

1. User runs `/plugin install` → Claude Code copies this directory to `~/.claude/plugins/cache/`
2. Skills in `skills/` become available as slash commands (`/recon`, `/recon.add-feature`)
3. Skills inline the recon-author agent instructions and call recon-core MCP tools

## Relationship to Other Directories

- **`recon-author/`** — Source of truth for agent instructions. Skill content is derived from these files.
- **`recon-core/`** — Python library. The MCP server exposes recon-core's API as tools callable by the skill.
- **Install mechanism** — Users install via `/plugin marketplace add deploysquad-ai/recon` then `/plugin install recon@deploysquad-ai/recon`.

## Updating Skills

Edit `skills/recon/SKILL.md` or `skills/recon-add-feature/SKILL.md` directly. The canonical authoring guidance lives in `recon-author/` — keep the two in sync when changing behavior.

## Plugin Metadata

`plugin.json` fields: `name`, `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`. Bump `version` on any release.
