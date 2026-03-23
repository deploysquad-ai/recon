# CLAUDE.md — recon-core

## What This Is

Python library that reads, writes, validates, and indexes an Obsidian vault structured as a project graph. It also generates CONTEXT.md files by traversing the graph from a Feature node.

## Quick Start

```bash
cd recon-core
pip install -e ".[dev]"
pytest -v                  # 212 tests
```

## Public API

All functions importable from `deploysquad_recon_core`:

```python
from deploysquad_recon_core import create_node, get_node, list_nodes, update_node
from deploysquad_recon_core import resolve_links, build_index, generate_context
```

| Function | Purpose |
|---|---|
| `create_node(type, data, project_dir, body_sections?)` | Validate + write new node |
| `get_node(file_path)` | Read + validate, returns dict with model/frontmatter/body_sections |
| `list_nodes(project_dir, type?, status?)` | List nodes, optionally filtered |
| `update_node(file_path, updates, body_sections?)` | Merge updates into existing node |
| `resolve_links(project_dir)` | Returns `{"valid": [...], "broken": [...]}` |
| `build_index(project_dir)` | Returns index dict (call `write_index()` to persist) |
| `generate_context(feature_name, project_dir)` | Returns CONTEXT.md string |

## Module Layout

```
src/deploysquad_recon_core/
  __init__.py          # Public API (thin wrappers)
  errors.py            # ReconCoreError, ValidationError, NodeNotFoundError, etc.
  models/
    base.py            # BaseNode (tags: list[str]), Wikilink, FullStatus, NoCompleteStatus
    project.py         # ProjectNode (description max 120 chars)
    goal.py            # GoalNode (belongs_to Project)
    version.py         # VersionNode (sequence int, target_date optional)
    persona.py         # PersonaNode (NoCompleteStatus, goals/context in body sections)
    constraint.py      # ConstraintNode (NoCompleteStatus)
    module.py          # ModuleNode (actors validated as Persona refs)
    decision.py        # DecisionNode (governed_by validated as Constraint refs only)
    user_story.py      # UserStoryNode (actors min 1, acceptance_criteria in body)
    epic.py            # EpicNode (NoCompleteStatus)
    feature.py         # FeatureNode (implements min 1, actors validated as Persona refs)
    __init__.py        # NODE_TYPE_MAP registry, get_model_for_type()
  vault/
    paths.py           # type_to_subfolder, node_filename, node_filepath, parse_filename, etc.
    reader.py          # read_node() → dict with frontmatter/body/body_sections/model
    writer.py          # write_node() with atomic writes (tempfile + os.replace)
  links.py             # parse_wikilink, extract_wikilinks, resolve_link, resolve_all_links
  index.py             # build_index, write_index, read_index (.graph/index.json)
  context.py           # generate_context() — graph traversal from Feature → CONTEXT.md
  schemas.py           # export_schema(type), export_schemas() via model_json_schema()
```

## Conventions

- **Pydantic v2** for all models. Type enforcement via `Literal["type-name"]` on the type field.
- **Wikilink** is `Annotated[str, Field(pattern=r"^\[\[[A-Z]...")]` — not a custom class.
- **FullStatus** (draft/active/complete/archived) vs **NoCompleteStatus** (draft/active/archived) — some node types can never be "complete".
- **Type-target validators**: `actors` fields have `@field_validator` ensuring `[[Persona - ...]]` prefix. `governed_by` on Decision validates `[[Constraint - ...]]` only.
- **Vault paths**: Project nodes live at root, all others in type-specific subfolders (features/, modules/, etc.).
- **Atomic writes**: writer.py uses tempfile + os.replace to prevent partial writes.
- **Auto-tagging**: `create_node` and `update_node` auto-inject a `tags: [project/{slug}]` field derived from the project name. This enables Obsidian graph view filtering by `tag:#project/ideate`.

## Testing

```bash
pytest tests/ -v                          # Full suite
pytest tests/test_models/ -v              # Models only
pytest tests/test_vault/ -v               # Vault I/O only
pytest tests/test_context.py -v           # Context builder (MVP gate)
pytest tests/test_api.py -v               # Integration tests
```

Test fixtures live in `tests/fixtures/sample_vault/my-project/` — a complete 10-node hand-authored graph with all wikilinks resolving.

## Adding a New Node Type

1. Create model in `src/deploysquad_recon_core/models/<type>.py` inheriting `BaseNode`
2. Add to `NODE_TYPE_MAP` in `models/__init__.py`
3. Add subfolder mapping in `vault/paths.py` (`_TYPE_TO_SUBFOLDER` and `_TYPE_TO_DISPLAY`)
4. Add fixture file in `tests/fixtures/sample_vault/my-project/`
5. Write tests in `tests/test_models/test_<type>.py`

## Wikilink Format

`[[Type - Name]]` — e.g. `[[Feature - JWT Login]]`, `[[User Story - Login Flow]]`

The type display name in the wikilink must match `_TYPE_TO_DISPLAY` in `vault/paths.py`.
