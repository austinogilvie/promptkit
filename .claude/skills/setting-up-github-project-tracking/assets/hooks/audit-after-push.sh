#!/bin/bash
# PostToolUse hook on Bash: after a `git push` of the default branch, the tracker's audit runs (issue.sh check:
# kind labels, hierarchy, board state against issue state) and its findings go back to Claude. A commit whose
# message says `Closes #n` closes the issue when it reaches the default branch, so in a repo that lands work as
# commits rather than pull requests the push is when the tracker drifts: an issue left open, a board row still
# In Progress. A push of any other branch is left alone. Read-only. The hook acts on the command in command
# position, not on the words inside a heredoc or a quoted string. Conventions: .claude/skills/issues/SKILL.md.

input=$(cat)
cmd=$(jq -r '.tool_input.command // empty' <<<"$input")
grep -qE '(^|[;&|(]|\$\()[[:space:]]*git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?push([[:space:]]|$)' <<<"$cmd" || exit 0
root=${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}
DEFAULT_BRANCH=main
# shellcheck disable=SC1091 # the issues skill's config: the repo's default branch
[ -f "$root/.claude/skills/issues/board.env" ] && . "$root/.claude/skills/issues/board.env"
[ "$(git -C "$root" rev-parse --abbrev-ref HEAD 2>/dev/null)" = "${DEFAULT_BRANCH:-main}" ] || exit 0
sleep 5 # the board's Done automation lands a few seconds after the push closes the issue
report=$(bash "$root/.claude/skills/issues/scripts/issue.sh" check 2>&1 | tail -20)
jq -cn --arg r "$report" \
    '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: ("Issue tracker audit after the push (issue.sh check):\n" + $r)}}'
