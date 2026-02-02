#!/usr/bin/env bash
set -euo pipefail

# scan.sh
#
# Fast “Pencilisms” scan using ripgrep.
#
# Usage:
#   ./scan.sh [PATH]
#
# Defaults:
#   PATH = frontend/src
#
# Notes:
# - This script is read-only.
# - Requires: rg (ripgrep)

TARGET="${1:-frontend/src}"

if ! command -v rg >/dev/null 2>&1; then
  echo "error: rg (ripgrep) not found. Install with: brew install ripgrep" >&2
  exit 1
fi

if [[ ! -e "$TARGET" ]]; then
  echo "error: target path not found: $TARGET" >&2
  exit 1
fi

echo "Normalize Pencil — Scan Report"
echo "Target: $TARGET"
echo

print_section () {
  local title="$1"
  local pattern="$2"
  echo "------------------------------------------------------------"
  echo "$title"
  echo "Pattern: $pattern"
  echo
  rg -n --hidden --no-heading --color never "$pattern" "$TARGET" \
    --glob '!**/node_modules/**' \
    --glob '!**/dist/**' \
    --glob '!**/build/**' \
    --glob '!**/.next/**' \
    --glob '!**/coverage/**' \
    --glob '!**/.turbo/**' \
    --glob '!**/.vercel/**' \
    --glob '!**/tmp/**' \
    || true
  echo
  echo "Count:"
  rg -n --hidden --no-heading --color never "$pattern" "$TARGET" \
    --glob '!**/node_modules/**' \
    --glob '!**/dist/**' \
    --glob '!**/build/**' \
    --glob '!**/.next/**' \
    --glob '!**/coverage/**' \
    --glob '!**/.turbo/**' \
    --glob '!**/.vercel/**' \
    --glob '!**/tmp/**' \
    -c || true
  echo
}

print_section "A) Pencil CSS variables" 'var\(--pencil-[a-zA-Z0-9_-]+\)'
print_section "B) Legacy pencil tokens (raw)" '--pencil-[a-zA-Z0-9_-]+'
print_section "C) Tailwind gray/blue literals (common offenders)" '\b(bg|text|border|ring|outline)-(white|black|gray|slate|zinc|neutral|stone|blue|indigo|red|green|amber|yellow)-[0-9]{2,3}\b'
print_section "D) Tailwind shadow classes" '\bshadow(-sm|-md|-lg|-xl|-2xl)?\b'
print_section "E) Arbitrary z-index and high z classes" 'z-\[[0-9]+\]|\bz-(40|50|60|70|80|90|100)\b'
print_section "F) “refresh required” copy regression" '(requires refresh|Refresh detection|refresh detection|Requires refresh)'

echo "------------------------------------------------------------"
echo "Done."
