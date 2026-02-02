#!/usr/bin/env bash
set -euo pipefail

# scan.sh
#
# Fast "Pencilisms" scan using ripgrep.
#
# Usage:
#   ./scan.sh [--config=<path>] [PATH]
#
# Config discovery:
#   1. --config=<path> flag (explicit)
#   2. Walk upward from CWD to find .pencil-normalize.config.json
#
# Notes:
# - This script is read-only.
# - Requires: rg (ripgrep), python3

# ── Parse arguments ──────────────────────────────────────────────
CONFIG_PATH=""
SCAN_ARG=""
for arg in "$@"; do
  case "$arg" in
    --config=*) CONFIG_PATH="${arg#--config=}" ;;
    *) SCAN_ARG="$arg" ;;
  esac
done

# ── Discover config if not specified ─────────────────────────────
if [[ -z "$CONFIG_PATH" ]]; then
  _dir="$(pwd)"
  while [[ "$_dir" != "/" ]]; do
    if [[ -f "$_dir/.pencil-normalize.config.json" ]]; then
      CONFIG_PATH="$_dir/.pencil-normalize.config.json"
      break
    fi
    _dir="$(dirname "$_dir")"
  done
fi

if [[ -z "$CONFIG_PATH" || ! -f "$CONFIG_PATH" ]]; then
  echo "error: No .pencil-normalize.config.json found. Run /normalizing-pencil to initialize." >&2
  exit 1
fi

# ── Read scan_path from config ───────────────────────────────────
DEFAULT_PATH=$(python3 -c "import json; print(json.load(open('$CONFIG_PATH'))['scan_path'])")
TARGET="${SCAN_ARG:-$DEFAULT_PATH}"

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

# ── Universal Pencil output sections (A–E) ───────────────────────
print_section "A) Pencil CSS variables" 'var\(--pencil-[a-zA-Z0-9_-]+\)'
print_section "B) Legacy pencil tokens (raw)" '--pencil-[a-zA-Z0-9_-]+'
print_section "C) Tailwind gray/blue literals (common offenders)" '\b(bg|text|border|ring|outline)-(white|black|gray|slate|zinc|neutral|stone|blue|indigo|red|green|amber|yellow)-[0-9]{2,3}\b'
print_section "D) Tailwind shadow classes" '\bshadow(-sm|-md|-lg|-xl|-2xl)?\b'
print_section "E) Arbitrary z-index and high z classes" 'z-\[[0-9]+\]|\bz-(40|50|60|70|80|90|100)\b'

# ── Section F: Copy regression patterns (conditional) ────────────
COPY_PATTERNS=$(python3 -c "
import json
cfg = json.load(open('$CONFIG_PATH'))
fixes = cfg.get('copy_fixes', {})
if fixes:
    print('|'.join(fixes.keys()))
" 2>/dev/null || true)

if [[ -n "$COPY_PATTERNS" ]]; then
  print_section "F) Copy regression patterns" "$COPY_PATTERNS"
fi

# ── Extra scan patterns from config ──────────────────────────────
python3 -c "
import json
cfg = json.load(open('$CONFIG_PATH'))
for name, pattern in cfg.get('extra_scan_patterns', {}).items():
    print(f'{name}\t{pattern}')
" 2>/dev/null | while IFS=$'\t' read -r name pattern; do
  print_section "Extra: $name" "$pattern"
done

echo "------------------------------------------------------------"
echo "Done."
