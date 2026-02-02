# normalizing-pencil reference

## Config file discovery

The skill looks for `.pencil-normalize.config.json` starting from the current working directory and walking upward through parent directories until it reaches the filesystem root.

- Override the search with the `--config <path>` flag on both `map_tokens.py` and `scan.sh`.
- If no config file is found, the skill prompts to run `init_config.py` to scaffold one interactively.

## Config field reference

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `version` | `number` | Yes | -- | Schema version. Currently `1` |
| `scan_path` | `string` | Yes | -- | Default directory to scan (e.g., `"src"`, `"frontend/src"`) |
| `file_extensions` | `string[]` | No | `["ts","tsx","js","jsx","css","md"]` | File extensions to process |
| `css_var_map` | `object` | Yes | -- | Maps `--pencil-*` CSS var names to your design system tokens |
| `tailwind_literal_map` | `object` | No | `{}` | Maps raw Tailwind classes (e.g., `bg-white`) to tokenized equivalents |
| `shadow_policy` | `object` | No | -- | Shadow handling configuration |
| `z_index_map` | `object` | No | `{}` | Maps Tailwind z-index classes to design system z-index tokens |
| `copy_fixes` | `object` | No | `{}` | Regex pattern to replacement for copy/text regression fixes |
| `extra_scan_patterns` | `object` | No | `{}` | Additional ripgrep patterns for `scan.sh` to check |

## Field details

### css_var_map

Maps Pencil-generated CSS custom properties to your project's design tokens.

```json
{
  "--pencil-accent": "--your-accent-token",
  "--pencil-bg": "--your-surface-token"
}
```

### tailwind_literal_map

Maps hardcoded Tailwind utility classes to tokenized equivalents using CSS variable references.

```json
{
  "bg-white": "bg-[var(--your-surface-token)]",
  "text-gray-900": "text-[var(--your-text-primary)]"
}
```

### z_index_map

Maps arbitrary or default Tailwind z-index classes to design system z-index tokens.

```json
{
  "z-[9999]": "z-[var(--z-modal)]",
  "z-50": "z-[var(--z-header)]"
}
```

### copy_fixes

Maps regex patterns to replacement strings for fixing copy/text regressions introduced by Pencil exports.

```json
{
  "Untitled Document": "My App Name"
}
```

### extra_scan_patterns

Defines additional ripgrep patterns that `scan.sh` will check during its audit pass. Keys are human-readable labels; values are regex patterns.

```json
{
  "hardcoded-opacity": "opacity-\\d+"
}
```

## Ordered passes

Passes execute in the following order. Do not reorder.

1. **Pass 1 -- CSS variable rewrites** (`css_var_map`): Replaces all `--pencil-*` CSS custom properties with your design system tokens.
2. **Pass 2 -- Tailwind literal replacements** (`tailwind_literal_map`): Swaps hardcoded Tailwind utility classes for tokenized equivalents.
3. **Pass 3 -- Shadow cleanup** (opt-in via `--fix-shadows`): Removes Pencil-generated shadow classes.
4. **Pass 4 -- Z-index normalization** (opt-in via `--fix-z`, reads `z_index_map`): Replaces arbitrary z-index values with design system tokens.
5. **Pass 5 -- Copy regression fixes** (opt-in via `--fix-copy`, reads `copy_fixes`): Applies regex-based text replacements.
6. **Report + warnings**: Summarizes changes made and flags remaining issues.

## Notes

- The `--strict` flag enables passes 3-5 simultaneously.
- Shadow removal uses a hardcoded regex matching the universal Pencil shadow pattern. It is not config-driven.
- `className` whitespace is auto-collapsed after shadow removal to prevent double-space artifacts.
