#!/bin/bash
# Good PM Context Injection Hook
# Injects lightweight PM stub on UserPromptSubmit events
#
# Progressive Disclosure (P0):
# - Injects PM_STUB.md (~30 lines) instead of full PM_CONTRACT.md (~270 lines)
# - PM commands auto-load full contract when needed (Decision D1)
# - Reduces per-prompt token overhead by ~90%
#
# Installation: Copied to .claude/hooks/ by /good-pm:setup
#
# Selective Loading:
# - Only injects if .good-pm/ directory exists in current directory
# - Prevents context pollution in non-PM projects
# - Preserves token budget for unrelated tasks

GOODPM_DIR=".good-pm"
STUB="$GOODPM_DIR/context/PM_STUB.md"
SESSION="$GOODPM_DIR/session/current.md"

# Early exit if not in a Good PM project
# This is the core of selective loading - no .good-pm/, no injection
if [ ! -d "$GOODPM_DIR" ]; then
  exit 0
fi

# Inject PM Stub if it exists (lightweight context - full contract loaded on-demand by commands)
if [ -f "$STUB" ]; then
  echo ""
  echo "[Good PM Context]"
  cat "$STUB"
  echo ""
fi

# Inject session context if it exists and has_content frontmatter is true
# Per Decision D4: assumes frontmatter exists (users re-run setup after upgrade)
if [ -f "$SESSION" ]; then
  # Check frontmatter for has_content: true flag
  HAS_CONTENT=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$SESSION" | grep '^has_content:' | grep -c 'true')
  if [[ "$HAS_CONTENT" -gt 0 ]]; then
    echo ""
    echo "[Session Context]"
    cat "$SESSION"
    echo ""
  fi
fi

exit 0
