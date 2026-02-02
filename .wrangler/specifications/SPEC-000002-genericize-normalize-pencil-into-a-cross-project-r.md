---
id: SPEC-000002
title: >-
  Genericize normalize-pencil into a cross-project reusable skill
  (normalizing-pencil)
type: specification
status: open
priority: high
labels:
  - specification
  - design
  - skill
  - normalize-pencil
  - genericization
createdAt: '2026-02-02T15:15:25.554Z'
updatedAt: '2026-02-02T15:15:25.554Z'
project: promptkit
---
# Specification: Genericize normalize-pencil → normalizing-pencil

## Executive Summary

**What:** Transform the existing `normalize-pencil` skill from a Cloakling-specific tool into a generic, cross-project reusable Claude Code skill called `normalizing-pencil`. The skill will detect and rewrite Pencil/MCP-generated CSS variable references and Tailwind literal classes into whatever design system tokens a given project defines. On first invocation in a new project, the skill initializes a project-local config file. On subsequent invocations it behaves like today's skill but reads mappings from that config instead of hardcoded Python dicts.

**Why:** The scanning engine, diff preview, apply-with-backup workflow, and CI check mode are all project-agnostic. The only project-specific parts are the token mapping tables, z-index/shadow policies, default scan path, and copy regression patterns. Extracting these into a per-project config makes the skill reusable across any project that uses Pencil for UI generation.

**Scope:**
- **Included:** Config file format design, first-run initialization flow, refactor of `map_tokens.py` and `scan.sh` to read config, migration of Cloakling mappings into a seed config, rename to gerund form, updated SKILL.md/reference.md/examples.md, `docopt` dependency documentation
- **Excluded:** AST-level component refactors (`<button>` → `<Button>`), new rewrite rule types beyond what exists today, GUI/TUI for config editing, publishing to a plugin registry

## Goals and Non-Goals

### Goals

1. Any project can adopt this skill by running `/normalizing-pencil` once to initialize config, then use it identically to how Cloakling uses it today
2. The Cloakling project continues working with zero behavior change after migration — its existing mappings become the seed config
3. The config file is human-readable, version-controllable, and editable without touching Python
4. The scanning/diffing/applying engine remains unchanged — only the data source changes
5. Fix all warnings from the validation review: gerund naming, trigger phrases in description, `docopt` docs, reference.md drift

### Non-Goals

- Adding new rewrite rule categories (e.g., font normalization, color palette expansion)
- Supporting multiple config files or config inheritance/composition
- Building a config validation CLI (the skill itself validates on load)
- Plugin registry publishing or npm/pip packaging
- Rewriting `scan.sh` in Python (keep both tools, both read config)

## Background & Context

### Problem Statement

The `normalize-pencil` skill works well for the Cloakling project but cannot be used in any other project because:
- Token mappings (`--pencil-accent` → `--accent-interactive`) are hardcoded in `map_tokens.py` lines 109-146
- Z-index rules are hardcoded in `map_tokens.py` lines 183-189
- Copy regression fixes are Cloakling-specific in `map_tokens.py` lines 201-213
- Default scan path `frontend/src` is hardcoded in both scripts
- `reference.md` documents Cloakling's specific design system tokens
- `scan.sh` patterns include a Cloakling-specific "refresh required" copy regression check

### Current State

```
.claude/skills/normalize-pencil/
├── SKILL.md              # References "Cloakling's design system"
├── reference.md          # Cloakling token tables (authoritative)
├── examples.md           # Cloakling before/after examples
└── scripts/
    ├── map_tokens.py     # Hardcoded dicts for Cloakling tokens
    └── scan.sh           # Hardcoded patterns + default path
```

Invocation: `/normalize-pencil [--apply] [path]`
Data flow: SKILL.md tells Claude to run `scan.sh` then `map_tokens.py`. Both scripts have Cloakling mappings baked in.

### Proposed State

```
.claude/skills/normalizing-pencil/
├── SKILL.md              # Generic description, first-run init docs
├── reference.md          # Documents the config format (not project tokens)
├── examples.md           # Generic before/after + config examples
├── templates/
│   └── pencil-normalize.config.json   # Starter template (empty/minimal)
└── scripts/
    ├── map_tokens.py     # Reads config, no hardcoded mappings
    ├── scan.sh           # Reads config for path + patterns
    └── init_config.py    # Creates project config on first run
```

Per-project artifact (created on first run):
```
<project-root>/.pencil-normalize.config.json
```

Invocation: `/normalizing-pencil [--apply] [path]`
Data flow: SKILL.md checks for config → if missing, runs init → then runs scan/apply using config-loaded mappings.

## Requirements

### Functional Requirements

- **FR-001:** On first invocation in a project without `.pencil-normalize.config.json`, the skill MUST run an interactive initialization that creates the config file at the project root
- **FR-002:** The initialization flow MUST ask the user for: (a) default scan path, (b) whether to start with an empty config or seed from a template, and (c) the target design system token prefix (e.g., `--ds-` or `--cloakling-`)
- **FR-003:** After initialization, the skill MUST immediately offer to run a scan using the new config
- **FR-004:** On subsequent invocations, the skill MUST load `.pencil-normalize.config.json` from the project root and use it for all mappings
- **FR-005:** `map_tokens.py` MUST accept a `--config <path>` flag and also auto-discover `.pencil-normalize.config.json` in the current working directory or nearest ancestor
- **FR-006:** `scan.sh` MUST read the default scan path and custom scan patterns from the config file
- **FR-007:** If the config file exists but is malformed or missing required fields, the skill MUST report a clear error with the specific validation failure
- **FR-008:** All existing CLI modes MUST continue working: `scan`, `apply`, `check`, with all existing flags (`--backup`, `--fix-shadows`, `--fix-z`, `--fix-copy`, `--strict`, `--ext`, `--include-tests`)
- **FR-009:** A Cloakling-specific seed config MUST be provided as a migration path so the Cloakling project can adopt the new skill with zero behavior change
- **FR-010:** The skill directory MUST be renamed from `normalize-pencil` to `normalizing-pencil` and the frontmatter `name` field updated to match

### Non-Functional Requirements

- **Backward compatibility:** The Cloakling project must produce identical scan/apply/check output after migrating to the config-based version (given the seed config)
- **No new runtime dependencies:** The config loader must use only Python stdlib (`json` module). Do not add `pyyaml`, `toml`, or other parsers. `docopt` remains the only external dependency.
- **Config file size:** The config file should be readable in a single screen (~60-80 lines for a typical project)

## Architecture

### Config File Format

The config file is JSON (no YAML — avoids adding a dependency). Located at `<project-root>/.pencil-normalize.config.json`.

```json
{
  "$schema": "https://raw.githubusercontent.com/austinogilvie/promptkit/main/schemas/pencil-normalize.config.schema.json",
  "version": 1,
  "scan_path": "frontend/src",
  "file_extensions": ["ts", "tsx", "js", "jsx", "css", "md"],
  "css_var_map": {
    "--pencil-accent": "--accent-interactive",
    "--pencil-accent-hover": "--accent-attention",
    "--pencil-text-primary": "--foreground-primary"
  },
  "tailwind_literal_map": {
    "bg-white": "bg-[var(--surface-level-1)]",
    "bg-gray-50": "bg-[var(--surface-level-1)]",
    "text-gray-900": "text-[var(--foreground-primary)]"
  },
  "shadow_policy": {
    "action": "strip",
    "allowed_shadow": "0 8px 24px -12px rgba(0,0,0,0.18)",
    "allowed_contexts": ["popover", "dropdown", "tooltip", "modal", "toast"]
  },
  "z_index_map": {
    "z-[9999]": "z-[var(--z-popover)]",
    "z-[1000]": "z-[var(--z-popover)]",
    "z-50": "z-[var(--z-popover)]",
    "z-40": "z-[var(--z-sidebars)]",
    "z-20": "z-[var(--z-header)]"
  },
  "copy_fixes": {
    "requires refresh": "",
    "Refresh detection": "Re-run detection"
  },
  "extra_scan_patterns": {
    "Pencil CSS variables": "var\\(--pencil-[a-zA-Z0-9_-]+\\)",
    "Legacy pencil tokens": "--pencil-[a-zA-Z0-9_-]+"
  }
}
```

**Field descriptions:**

| Field | Required | Description |
|-------|----------|-------------|
| `version` | Yes | Config schema version. Currently `1`. |
| `scan_path` | Yes | Default directory to scan when no path argument is given |
| `file_extensions` | No | File extensions to process. Defaults to `["ts", "tsx", "js", "jsx", "css", "md"]` |
| `css_var_map` | Yes | Map of `--pencil-*` CSS variable names to target design system tokens |
| `tailwind_literal_map` | No | Map of raw Tailwind classes to tokenized replacements |
| `shadow_policy` | No | Shadow handling config. If absent, shadows are left untouched. |
| `z_index_map` | No | Map of raw z-index classes to design system z-index tokens |
| `copy_fixes` | No | Map of text patterns to replacements for copy regression fixes |
| `extra_scan_patterns` | No | Additional ripgrep patterns for `scan.sh` to check |

### Components

#### Component 1: Config Loader (`_load_config` in map_tokens.py)

**Responsibility:** Find, read, validate, and return the parsed config as a Python dict.

**Behavior:**
1. If `--config <path>` is passed, use that path directly
2. Otherwise, walk from CWD upward looking for `.pencil-normalize.config.json`
3. If not found, exit with error code and message: "No .pencil-normalize.config.json found. Run `/normalizing-pencil` to initialize."
4. Validate required fields (`version`, `scan_path`, `css_var_map`)
5. Return parsed dict

**Interfaces:**
- Input: optional explicit path, or auto-discovery from CWD
- Output: validated Python dict, or `sys.exit(1)` with error message

#### Component 2: Config Initializer (`scripts/init_config.py`)

**Responsibility:** Interactive first-run setup that creates `.pencil-normalize.config.json`.

**Behavior:**
1. Check if config already exists — if yes, ask whether to overwrite or abort
2. Prompt for: default scan path, whether to seed from a template
3. If seeding, copy the template and let the user know to edit the token maps
4. If starting empty, write a minimal config with empty `css_var_map` and placeholder `scan_path`
5. Print confirmation with the path to the created file

**Interfaces:**
- Input: stdin prompts (or `--non-interactive` flag with `--scan-path` and `--template` for CI)
- Output: `.pencil-normalize.config.json` written to project root

#### Component 3: Updated `scan.sh`

**Responsibility:** Read `scan_path` and `extra_scan_patterns` from config, plus run the hardcoded Pencil-detection patterns.

**Changes from current:**
- Read `scan_path` default from config instead of hardcoding `frontend/src`
- Read `extra_scan_patterns` from config and run them in addition to the built-in Pencil-detection patterns
- The built-in patterns (sections A-E: `--pencil-*` vars, Tailwind gray/blue literals, shadow classes, z-index) remain hardcoded since they detect Pencil output universally
- Section F (copy regression) becomes conditional: only run if `copy_fixes` is non-empty in config
- Accept optional `--config <path>` flag, otherwise auto-discover

#### Component 4: Updated SKILL.md

**Responsibility:** Orchestrate the init-or-run flow.

**New behavior in the skill body:**
```
1. Check if .pencil-normalize.config.json exists in project root
2. If NOT found:
   a. Run: python3 scripts/init_config.py
   b. After init, offer to run a scan
3. If found:
   a. Run scan.sh (same as today)
   b. Run map_tokens.py with --config flag (same as today)
```

### Key Algorithm: Config Discovery

```
function find_config(start_dir):
    dir = start_dir
    while dir != filesystem_root:
        candidate = dir / ".pencil-normalize.config.json"
        if candidate.exists():
            return candidate
        dir = dir.parent
    return None
```

This mirrors how tools like `.eslintrc`, `.prettierrc`, and `tsconfig.json` are discovered.

## Implementation Details

### File Structure (after migration)

```
.claude/skills/normalizing-pencil/
├── SKILL.md                                    # Updated: generic, init flow
├── reference.md                                # Updated: documents config format
├── examples.md                                 # Updated: generic examples + config examples
├── templates/
│   ├── pencil-normalize.config.json            # Minimal starter config
│   └── pencil-normalize.config.cloakling.json  # Cloakling seed config
└── scripts/
    ├── map_tokens.py                           # Updated: config-driven
    ├── scan.sh                                 # Updated: config-driven
    └── init_config.py                          # New: first-run initializer
```

### Changes to map_tokens.py

**Remove:** Hardcoded `css_var_map` dict (lines 109-120), `tailwind_literal_map` dict (lines 136-146), z-index rules (lines 183-189), copy fixes (lines 201-213), default path `"frontend/src"` (line 423).

**Add:**
- `--config <path>` option to docopt interface
- `_find_config(start: Path) -> Path` function — walks up from `start` to find config
- `_load_config(config_path: Path) -> dict` function — reads JSON, validates required fields, returns dict
- `_build_rules` refactored to accept config dict instead of using module-level constants

**Preserve unchanged:** All regex engine logic, `_apply_rules`, `_diff`, `_collapse_classname_spaces`, `_iter_files`, `_is_allowed_file`, `_read_text`, `_write_text`, `_run_scan`, `_run_apply`, `_run_check`, the `RewriteRule` dataclass.

### Changes to scan.sh

**Remove:** Hardcoded `TARGET="${1:-frontend/src}"`, Section F hardcoded "refresh required" pattern.

**Add:**
- Config file discovery (parse JSON with `python3 -c` one-liner or `jq` if available)
- Read `scan_path` for default target
- Read `copy_fixes` keys to build Section F pattern dynamically
- Read `extra_scan_patterns` and run each as an additional section

**Preserve unchanged:** Sections A-E patterns (these detect Pencil output universally), the `print_section` function, all glob exclusions.

### Changes to SKILL.md

**Remove:** All references to "Cloakling's design system".

**Add:**
- First-run initialization flow documentation
- Config file format summary (with pointer to reference.md for full docs)
- Updated invocation examples showing `--config` flag
- Prerequisites section documenting `docopt` and `rg`
- Trigger phrases in description

**Update:** `name` field to `normalizing-pencil`, description to generic language.

### Changes to reference.md

**Remove:** All Cloakling-specific token tables.

**Replace with:** Config file format documentation — field-by-field reference with types, defaults, and examples. This becomes the authoritative doc for the config schema.

### Changes to examples.md

**Remove:** Cloakling-specific before/after examples.

**Replace with:**
1. Example of a minimal config file
2. Example of a fully-populated config file
3. Generic before/after rewrite examples using placeholder tokens
4. Example of first-run initialization output

### New file: templates/pencil-normalize.config.json

Minimal starter:
```json
{
  "version": 1,
  "scan_path": "src",
  "css_var_map": {},
  "tailwind_literal_map": {}
}
```

### New file: templates/pencil-normalize.config.cloakling.json

The full Cloakling config extracted from today's hardcoded values — serves as both a migration path and a reference example.

### New file: scripts/init_config.py

~80-100 lines. Reads stdin for interactive prompts, writes JSON config. Uses only Python stdlib (`json`, `pathlib`, `sys`). No `docopt` dependency (simple enough for `sys.argv` parsing).

## Migration Path

### For the Cloakling project

1. Copy `templates/pencil-normalize.config.cloakling.json` to Cloakling project root as `.pencil-normalize.config.json`
2. Delete the old `normalize-pencil` skill directory (if it was project-local)
3. Install the new `normalizing-pencil` skill (global at `~/.claude/skills/` or via plugin)
4. Run `/normalizing-pencil --check frontend/src` — should produce identical output to before
5. Commit `.pencil-normalize.config.json` to Cloakling repo

### For new projects

1. Run `/normalizing-pencil` in the project
2. Skill detects no config → runs `init_config.py`
3. User answers prompts (scan path, seed template)
4. Config created, skill offers to run first scan
5. User edits config to add their project's token mappings
6. Subsequent runs work like today

## Testing Strategy

### Verification approach

1. **Snapshot test:** Run the current `normalize-pencil` against a fixture directory. Save output. Run the new `normalizing-pencil` with the Cloakling seed config against the same fixtures. Output must be identical.
2. **Config validation test:** Feed malformed configs (missing `version`, missing `css_var_map`, invalid JSON) to `_load_config` and verify clear error messages.
3. **Init flow test:** Run `init_config.py --non-interactive --scan-path=src --template=minimal` and verify the output file is valid JSON with expected structure.
4. **Empty config test:** Run with a config that has empty `css_var_map` and `tailwind_literal_map` — should produce no changes.
5. **Config discovery test:** Place config at various ancestor directory levels and verify discovery works.

## Open Questions & Decisions

### Resolved Decisions

| Decision | Options Considered | Chosen | Rationale |
|----------|-------------------|--------|-----------|
| Config format | JSON, YAML, TOML | JSON | No new dependencies; Python stdlib `json` module; familiar to all developers |
| Config location | Project root, `.claude/`, `~/.config/` | Project root (`.pencil-normalize.config.json`) | Version-controllable per project; mirrors `.eslintrc` pattern |
| Config discovery | Explicit path only, CWD-upward walk | CWD-upward walk with `--config` override | Matches developer expectations from eslint/prettier/tsconfig |
| Skill rename | Keep `normalize-pencil`, rename to `normalizing-pencil` | Rename | Aligns with Anthropic gerund naming convention; clean break |
| Cloakling migration | Auto-detect old skill, manual migration | Manual migration with seed template | Simpler, less magic, one-time effort |

### Open Questions

- [ ] **Q1:** Should the config support comments (JSONC) or stay strict JSON?
  - **Impact:** Developer experience when editing config
  - **Options:** Strict JSON (simplest), JSONC via strip-comments preprocessing, or JSON5
  - **Recommendation:** Strict JSON — add a `"_comment"` convention for inline docs if needed

- [ ] **Q2:** Should `scan.sh` be rewritten in Python to share the config loader, or kept as bash with JSON parsing via `python3 -c`?
  - **Impact:** Maintenance burden, startup latency
  - **Options:** Keep bash + `python3 -c` bridge, rewrite in Python, drop `scan.sh` entirely
  - **Recommendation:** Keep bash with `python3 -c` bridge — `scan.sh` is fast and simple

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Config format changes require migration | Low | Medium | `version` field enables future schema migrations |
| Users forget to commit config to repo | Medium | Low | Init script prints reminder to `git add` the config |
| `jq` not available on all systems for scan.sh | Medium | Low | Fall back to `python3 -c "import json; ..."` |
| Cloakling output differs after migration | Low | High | Snapshot test comparing before/after output |

## Success Criteria

### Launch Criteria

- [ ] Cloakling project produces identical scan/apply/check output with seed config
- [ ] New project can init + configure + scan in under 2 minutes of user effort
- [ ] All existing CLI flags continue to work
- [ ] Config validation produces clear, actionable error messages
- [ ] `docopt` and `rg` prerequisites documented
- [ ] `reference.md` documents the config format completely
- [ ] Skill passes `/validating-agent-tools` with no errors and no warnings

### Post-Launch

- Skill is usable in at least one non-Cloakling project without modification
- Config file is intuitive enough that a developer can populate it without reading reference.md

## References

### Related Files (current state)

- `.claude/skills/normalize-pencil/SKILL.md` — current skill entry point
- `.claude/skills/normalize-pencil/reference.md` — current Cloakling token tables
- `.claude/skills/normalize-pencil/examples.md` — current Cloakling examples
- `.claude/skills/normalize-pencil/scripts/map_tokens.py` — current rewrite engine
- `.claude/skills/normalize-pencil/scripts/scan.sh` — current ripgrep scanner
- `CLAUDE_MEMO_AI_TOOLS_REVIEW.md` — validation review identifying warnings to fix

### Prior Art

- `.eslintrc.json` / `eslint.config.js` — per-project config with CWD-upward discovery
- `.prettierrc` — per-project formatting config
- `tsconfig.json` — per-project TypeScript config with `extends` support

## Appendix

### Glossary

- **Pencilism:** A CSS variable, Tailwind class, shadow, or z-index pattern generated by Pencil/MCP that doesn't conform to the project's design system
- **Token:** A CSS custom property (e.g., `--foreground-primary`) that represents a semantic design value
- **Seed config:** A pre-populated config file that replicates today's hardcoded Cloakling mappings
- **Config discovery:** The process of walking from CWD upward to find `.pencil-normalize.config.json`

### Assumptions

- Projects using this skill have a single design system token set (no multi-theme config needed at this stage)
- Python 3.8+ is available in all target environments
- The Pencil MCP tool will continue generating `--pencil-*` CSS variables as its output convention
