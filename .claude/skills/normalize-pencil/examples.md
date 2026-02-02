# examples

## Example: simple token rewrite

Before:
`className="bg-white text-gray-900 border border-gray-200"`

After:
`className="bg-[var(--surface-level-1)] text-[var(--foreground-primary)] border border-[color:var(--border-default)]"`

## Example: pencil var rewrite

Before:
`text-[var(--pencil-text-muted)]`

After:
`text-[var(--foreground-muted)]`

## Example: allowed shadow

Before:
`className="shadow-lg"`

After:
`style={{ boxShadow: "0 8px 24px -12px rgba(0,0,0,0.18)" }}`
