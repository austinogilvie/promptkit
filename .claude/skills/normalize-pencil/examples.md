# normalizing-pencil examples

## Minimal config

`.pencil-normalize.config.json` with only the required fields:

```json
{
  "version": 1,
  "scan_path": "src",
  "css_var_map": {
    "--pencil-accent": "--brand-primary",
    "--pencil-bg": "--surface-base"
  }
}
```

## Full config

A fully-populated `.pencil-normalize.config.json` covering every map type:

```json
{
  "version": 1,
  "scan_path": "frontend/src",
  "file_extensions": ["ts", "tsx", "js", "jsx", "css"],
  "css_var_map": {
    "--pencil-accent": "--brand-primary",
    "--pencil-accent-hover": "--brand-primary-hover",
    "--pencil-text-primary": "--text-primary",
    "--pencil-text-secondary": "--text-secondary",
    "--pencil-text-muted": "--text-muted",
    "--pencil-bg": "--surface-base",
    "--pencil-surface": "--surface-raised",
    "--pencil-border": "--border-default",
    "--pencil-border-strong": "--border-strong"
  },
  "tailwind_literal_map": {
    "bg-white": "bg-[var(--surface-raised)]",
    "bg-gray-50": "bg-[var(--surface-base)]",
    "text-gray-900": "text-[var(--text-primary)]",
    "text-gray-700": "text-[var(--text-secondary)]",
    "text-gray-500": "text-[var(--text-tertiary)]",
    "border-gray-200": "border-[color:var(--border-default)]"
  },
  "z_index_map": {
    "z-[9999]": "z-[var(--z-modal)]",
    "z-50": "z-[var(--z-header)]"
  },
  "copy_fixes": {
    "Untitled Page": "Dashboard"
  },
  "extra_scan_patterns": {
    "hardcoded-colors": "#[0-9a-fA-F]{3,8}"
  }
}
```

## Before/After: CSS variable rewrite

Before:
`color: var(--pencil-accent);`

After:
`color: var(--brand-primary);`

## Before/After: Tailwind literal rewrite

Before:
`className="bg-white text-gray-900 border border-gray-200"`

After:
`className="bg-[var(--surface-raised)] text-[var(--text-primary)] border border-[color:var(--border-default)]"`

## Before/After: Pencil CSS var in Tailwind

Before:
`text-[var(--pencil-text-muted)]`

After:
`text-[var(--text-muted)]`

## Before/After: Shadow removal (--fix-shadows)

Before:
`className="shadow-lg rounded-lg p-4"`

After:
`className="rounded-lg p-4"`

Note: Use `boxShadow` inline style for intentional shadows on floating surfaces.

## First-run init

```
$ python3 .claude/skills/normalizing-pencil/scripts/init_config.py
No .pencil-normalize.config.json found.
? Choose a template:
  1. Minimal (empty mappings -- fill in your tokens)
  2. Full seed (pre-populated example mappings)
> 1
Created .pencil-normalize.config.json
Edit the file to add your project's token mappings.
```

## Scan output

```
$ /normalizing-pencil src/components
=== Section A: Pencil CSS vars ===
src/components/Card.tsx:  color: var(--pencil-accent);
src/components/Header.tsx:  background: var(--pencil-bg);

=== Section B: Raw Tailwind literals ===
src/components/Card.tsx:  className="bg-white text-gray-900"

Would change 2 file(s).
```

## Config flag

```
$ /normalizing-pencil --config ./configs/.pencil-normalize.config.json --apply src
Changed 2 file(s):
- src/components/Card.tsx
- src/components/Header.tsx
```
