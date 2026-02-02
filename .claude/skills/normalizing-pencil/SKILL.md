---
name: normalizing-pencil
description: >-
  Normalize Pencil/MCP-generated UI code to a project's design system tokens.
  Use when reviewing Pencil output, after generating UI with Pencil MCP,
  or when running design system compliance checks. Detects and rewrites
  CSS variable references, Tailwind literal classes, shadows, and z-index.
disable-model-invocation: true
user-invocable: true
argument-hint: "[--check|--apply] [--fix-shadows] [--fix-z] [--fix-copy] [--strict] [--config path] [path]"
allowed-tools: ["Read", "Write", "Bash", "Glob", "Grep"]
---

# normalizing-pencil

Normalize Pencil/MCP-generated UI code to your project's design system.

## Prerequisites

- Python 3.8+ with `docopt` (`pip install docopt`)
- ripgrep (`brew install ripgrep` / `apt install ripgrep`)

## First Run

On first invocation the skill walks upward from CWD looking for `.pencil-normalize.config.json`. If no config is found it runs `scripts/init_config.py` interactively to scaffold one from built-in templates. The config file defines all project-specific token mappings (CSS vars, Tailwind literals, shadows, z-index).

## Invocation

- `/normalizing-pencil [path]` -- scan report + diff preview (no writes)
- `/normalizing-pencil --apply [path]` -- apply rewrites
- `/normalizing-pencil --check [path]` -- CI mode (non-zero exit if changes needed)
- `/normalizing-pencil --apply --strict [path]` -- all fix passes
- `/normalizing-pencil --config path/to/config [path]` -- use explicit config

### Arguments

- `--apply` -- write rewritten files (creates `.bak` backups)
- `--check` -- exit non-zero if any Pencilisms remain (CI-friendly)
- `--fix-shadows` -- rewrite `shadow-*` utilities per config
- `--fix-z` -- rewrite z-index literals per config
- `--fix-copy` -- rewrite hard-coded copy strings per config
- `--strict` -- shorthand for `--fix-shadows --fix-z --fix-copy`
- `--config` -- path to an explicit config file (skips CWD walk)
- `[path]` -- directory to scan; defaults to `scan_path` from config

## What this skill enforces

1. **Detect Pencilisms** -- `--pencil-*` CSS vars, raw Tailwind literals (`bg-white`, `text-gray-*`, `border-gray-*`), `shadow-*` usage, z-index patterns (`z-[9999]`, `z-50`).
2. **Rewrite tokens deterministically** -- replace detected patterns with project tokens per config mappings.

Does NOT do AST refactors (e.g. `<button>` to `<Button>`).

## Command behavior

1. Run scan: `bash .claude/skills/normalizing-pencil/scripts/scan.sh [path]`
2. Run token mapping based on flags:
   - `--apply`: `python3 scripts/map_tokens.py apply [path] --backup`
   - `--check`: `python3 scripts/map_tokens.py check [path]`
   - default: `python3 scripts/map_tokens.py scan [path]`

## Navigation

- [`reference.md`](reference.md) -- config format and mapping tables
- [`examples.md`](examples.md) -- before/after examples

## Executables

- [`scripts/scan.sh`](scripts/scan.sh) -- fast Pencilism scan (ripgrep)
- [`scripts/map_tokens.py`](scripts/map_tokens.py) -- deterministic token replacement
- [`scripts/init_config.py`](scripts/init_config.py) -- interactive config scaffolding
