#!/bin/bash
# PreToolUse hook on Bash: a `gh issue create` leaves this hook with exactly one kind label.
#
#   one kind label    passes untouched
#   no kind label     the kind is read off the title by `issue.sh kind` ([Bug], [Spec], [Feature], [Epic]; no prefix
#                     is a task) and `--label <kind>` is added to the command (updatedInput with allow: the command
#                     is the one Claude wrote plus a label). A title the hook cannot read: blocked, with the fix.
#   two or more       blocked: that is a choice, not a repair.
#
# Nothing else is checked; an inline --body is fine. Once the issue exists, board-new-issue.sh places it on the
# board, links its parent and adds the kind label if the rewrite did not stick. The hook acts on the command in
# command position (the start, or after ; & | ( or $( ), not on the words inside a heredoc or a quoted string:
# the body of a heredoc (`<<EOF`, `<<'EOF'`, `<<-EOF`, up to its terminator line) is data fed to a program, so a
# `gh issue create` written into a script by `cat <<'EOF'` is neither detected nor rewritten, and the labels and
# title are read from the command with those bodies removed. One heredoc opener per line is understood.
# Exit 2 blocks the command and sends stderr to Claude. Conventions: .claude/skills/issues/SKILL.md.

input=$(cat)
cmd=$(jq -r '.tool_input.command // empty' <<<"$input")

heredoc_term() { # a line -> the terminator of the heredoc it opens (`-` first when `<<-`), or nothing
    if [[ $1 =~ \<\<(-?)[[:space:]]*[\"\']?([A-Za-z_][A-Za-z0-9_]*) ]]; then
        printf '%s%s\n' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
    fi
}
ends_heredoc() { # a line, the terminator -> whether the line closes the heredoc (leading tabs allowed under `<<-`)
    local line=$1 term=$2
    if [ "${term#-}" != "$term" ]; then term=${term#-}; line=${line#"${line%%[!$'\t']*}"}; fi
    [ "$line" = "$term" ]
}
each_line() { # the command, line by line: `$1 code <line>` outside a heredoc body, `$1 body <line>` inside one
    local line term=""
    while IFS= read -r line || [ -n "$line" ]; do
        if [ -n "$term" ]; then
            "$1" body "$line"
            ends_heredoc "$line" "$term" && term=""
            continue
        fi
        "$1" code "$line"
        term=$(heredoc_term "$line")
    done <<<"$cmd"
}
code_only() { [ "$1" = code ] && printf '%s\n' "$2"; return 0; }
code=$(each_line code_only)                                    # the command without its heredoc bodies
bare=$(sed -E "s/'[^']*'//g; s/\"[^\"]*\"//g" <<<"$code")      # and without its quoted strings, for the detection
grep -qE '(^|[;&|(]|\$\()[[:space:]]*gh[[:space:]]+issue[[:space:]]+create([[:space:]]|$)' <<<"$bare" || exit 0

values() { # every value of the given options (`--label x`, `--label=x`, `-l x`, quoted or not), one per line
    grep -oE -- "(^| )($1)[ =]+(\"[^\"]*\"|'[^']*'|[^ ]+)" <<<"$code" \
        | sed -E "s/^ ?($1)[ =]+//; s/^[\"']//; s/[\"']\$//"
}
block() {
    {
        echo "Blocked: gh issue create does not follow .claude/skills/issues/SKILL.md: $1"
        echo "The skill's script does it right by construction:"
        echo '  .claude/skills/issues/scripts/issue.sh create <kind> --title "..." --body-file body.md [--label <area>] [--parent <n>] [--priority P2]'
    } >&2
    exit 2
}

kinds=$(values '--label|-l' | grep -cxE 'epic|spec|feature|bug|task')
case $kinds in
    1) exit 0 ;;
    0) ;;
    *) block "it carries $kinds kind labels; exactly one of epic, spec, feature, bug, task is required" ;;
esac

title=$(values '--title|-t' | head -1)
if [ -z "$title" ] || [[ "$title" == \$* ]]; then # absent, or a variable the hook cannot see into
    block "it has no kind label and the title is not readable in the command, so the kind cannot be inferred; add --label <epic|spec|feature|bug|task>"
fi
root=${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}
kind=$(bash "$root/.claude/skills/issues/scripts/issue.sh" kind "$title") || kind=task
label_code() { # the rewrite: `--label <kind>` after a `gh issue create` in command position; a heredoc body passes as it is
    if [ "$1" = body ]; then printf '%s\n' "$2"; return; fi
    sed -E "s/(^|[;&|(]|\\$\\()([[:space:]]*gh[[:space:]]+issue[[:space:]]+create)([[:space:]]|$)/\\1\\2 --label $kind\\3/" <<<"$2"
}
updated=$(each_line label_code)
jq -cn --arg c "$updated" --arg k "$kind" --argjson t "$(jq -c '.tool_input' <<<"$input")" '{
    hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "allow",
        updatedInput: ($t + {command: $c}),
        additionalContext: ("The issue hook added --label " + $k + ", read off the title; the board hook places the issue once it exists.")
    }
}'
