---
name: normalize-pencil
description: Normalize Pencil/MCP-generated UI code to Cloakling’s design system (tokens, primitives, shadows, z-index, spacing).
disable-model-invocation: true
argument-hint: "[--check|--apply] [--fix-shadows] [--fix-z] [--fix-copy] [--strict] [path=frontend/src]"
---

# normalize-pencil

Normalize Pencil/MCP-generated UI code into Cloakling’s design system.

## Invocation

- `/normalize-pencil [path]`: show scan report + show unified diff preview (no writes)
- `/normalize-pencil --apply [path]`: apply deterministic rewrites (writes files)
- `/normalize-pencil --check [path]`: CI mode (non-zero / fail if changes needed)
- `/normalize-pencil --apply --fix-shadows --fix-z --fix-copy [path]`: Apply strict normalization: tokens, shadow removal, z-index, & copy fixes
- `/normalize-pencil --apply --strict [path]`: Shorthand for all fix passes (equivalent to --fix-shadows --fix-z --fix-copy)

Arguments:
- `$ARGUMENTS` may include any combination of:
  - `--apply`
  - `--check`
  - `--fix-shadows`
  - `--fix-z`
  - `--fix-copy`
  - `--strict` (equivalent to --fix-shadows --fix-z --fix-copy)
- `[path]` defaults to `frontend/src` if omitted.

## What this skill enforces

1) Detect "Pencilisms"
   - `--pencil-*` css vars
   - raw Tailwind literals (bg-white, text-gray-*, border-gray-*)
   - shadow-* usage
   - z-[9999] / z-50 etc

2) Rewrite tokens deterministically
   - Replace `var(--pencil-*)` with Cloakling tokens per [`reference.md`](reference.md)
   - Replace a small allowlist of Tailwind literals with tokenized equivalents

This skill intentionally does NOT yet:
- do AST refactors (e.g., `<button>` → `<Button>`) unless explicitly added later
- attempt to "fix everything" beyond the deterministic mappings

## Command behavior (required)

Always run the scan first:

1) `bash .claude/skills/normalize-pencil/scripts/scan.sh [path]`

Then run token mapping using `.claude/skills/normalize-pencil/scripts/map_tokens.py`:

- If `$ARGUMENTS` contains `--apply`:
  2) `python3 .claude/skills/normalize-pencil/scripts/map_tokens.py apply [path] --backup`
  3) Print list of changed files

- Else if `$ARGUMENTS` contains `--check`:
  2) `python3 .claude/skills/normalize-pencil/scripts/map_tokens.py check [path]`
  3) If it fails, print the offender file list and exit

- Else (default preview mode):
  2) `python3 .claude/skills/normalize-pencil/scripts/map_tokens.py scan [path]`
  3) Show unified diff previews (no writes)

## Navigation

- See [`reference.md`](reference.md) for authoritative mapping tables and ordered passes.
- See [`examples.md`](examples.md) for before/after and recommended Pencil prompt templates.

## Executables
- Executables:
- [`scripts/scan.sh`](scripts/scan.sh) — fast "Pencilism" scan report (ripgrep)
- [`scripts/map_tokens.py`](scripts/map_tokens.py) — deterministic token replacement (preview/apply/check)
