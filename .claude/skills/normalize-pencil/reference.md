# normalize-pencil reference

## Token mapping (authoritative)

### CSS variables: `--pencil-*` → Cloakling tokens

- `--pencil-accent` → `--accent-interactive`
- `--pencil-accent-hover` → `--accent-attention`
- `--pencil-text-primary` → `--foreground-primary`
- `--pencil-text-secondary` → `--foreground-secondary`
- `--pencil-text-muted` → `--foreground-muted`
- `--pencil-bg` → `--surface-base`
- `--pencil-surface` → `--surface-level-1`
- `--pencil-surface-muted` → `--surface-level-1`
- `--pencil-border` → `--border-default`
- `--pencil-border-strong` → `--border-strong`

## Tailwind literal replacements (in new code)

- `bg-white` → `bg-[var(--surface-level-1)]`
- `bg-gray-50` → `bg-[var(--surface-level-1)]`
- `text-gray-900` → `text-[var(--foreground-primary)]`
- `text-gray-700` → `text-[var(--foreground-secondary)]`
- `text-gray-500` → `text-[var(--foreground-tertiary)]`
- `text-gray-400` → `text-[var(--foreground-muted)]`
- `border-gray-200` → `border-[color:var(--border-default)]`
- `border-gray-300` → `border-[color:var(--border-strong)]`

## Shadow policy

- Remove all Tailwind `shadow-*`.
- Allowed shadow only on floating surfaces (popover/dropdown/tooltip/modal/toast):
  - `boxShadow: "0 8px 24px -12px rgba(0,0,0,0.18)"`

## Z-index policy

Use ONLY:
- `var(--z-header)`
- `var(--z-sidebars)`
- `var(--z-popover)`
- `var(--z-tooltip)`
- `var(--z-modal)`

No `z-[9999]`.

## Mechanical layout constants

- header: 56px
- sidebars: 304px
- doc max: 820px
- padding: 24px
- gutter: 24px

## Ordered passes (do not reorder)

1. Pass 1: Token rewrites (vars + tailwind literals)
2. Pass 2: Shadow cleanup
3. Pass 3: Z-index cleanup
4. Pass 4: (Optional) Component substitution to UI primitives
5. Pass 5: Report + warnings
