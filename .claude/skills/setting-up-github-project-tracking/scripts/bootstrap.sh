#!/usr/bin/env bash
# bootstrap.sh: set up GitHub issue tracking and a project board for one repo, a step at a time.
#
#   bootstrap.sh preflight [--repo PATH] [--title T] [--adopt N]
#   bootstrap.sh github    [--repo PATH] [--title T] [--adopt N] [--dry-run]
#   bootstrap.sh files     [--repo PATH] [--flow pr|main] [--force] [--dry-run]
#   bootstrap.sh verify    [--repo PATH] [--smoke]
#   bootstrap.sh render    --config FILE --dest DIR [--flow pr|main]
#
# preflight  read-only: the repo, the login, and whether the repo already has a board
# github     the kind labels, the project, its Status and Priority fields, the link to the repo
# files      the issues skill, the hooks, the issue templates, board.env and the hook wiring in .claude/settings.json
# verify     the board's workflows (set by a person in GitHub's web UI), and with --smoke one real issue cycled
#            through the board
# render     the files step into any directory from a board.env, with no GitHub call: the offline test
#
# Every step takes the repo's path and works the rest out from GitHub, so a rerun, in this session or another,
# resumes where the last one stopped. Each step is idempotent. stdout is one JSON object (step, state, repo,
# project, did, skipped, conflicts, todo, unverified); stderr is the log, one line per action.
#
# Exit codes: 0 the step is done (or was already); 10 the repo already has a board, nothing changed;
# 11 a person must decide something (todo says what); 12 steps in GitHub's web UI are outstanding (verify);
# 3 a precondition failed (a tool, the login, a scope, a permission); 2 usage; 1 anything else, safe to rerun.
#
# Needs git, gh (scopes repo and project) and jq. Written for bash 3.2, which macOS ships.

set -euo pipefail

SKILL_DIR=$(cd "$(dirname "$0")/.." && pwd)
ASSETS=$SKILL_DIR/assets
MARKER_TAG="(setting-up-github-project-tracking)"
SMOKE_TITLE="Set up issue tracking and project board"
REQUIRED_WORKFLOWS="Auto-add to project
Item closed
Item reopened"

# ---------------------------------------------------------------- output

STEP="" STATE="" REPO="" OWNER="" NAME="" OWNER_TYPE="" OWNER_ID="" REPO_ID="" DEFAULT_BRANCH=""
PROJECT_ID="" PROJECT_NUMBER="" PROJECT_URL="" PROJECT_TITLE="" PROJECT_LINKED="" NEXT=""
DID="" SKIPPED="" CONFLICTS="" TODO="" UNVERIFIED=""

add() { eval "$1=\${$1:+\$$1\$'\\n'}\$2"; } # append a line to the named list
did() { add DID "$1"; echo "did   $1" >&2; }
skip() { add SKIPPED "$1"; echo "skip  $1" >&2; }
would() { add DID "would: $1"; echo "would $1" >&2; }
warn() { echo "warn  $1" >&2; }
ok() { echo "ok    $1" >&2; }
todo() { add TODO "$1"; echo "todo  $1" >&2; }
conflict() { add CONFLICTS "$1"; echo "conflict $1" >&2; }
unverified() { add UNVERIFIED "$1"; echo "unverified $1" >&2; }

finish() { # exit code -> the JSON object on stdout, then exit
    jq -n --arg step "$STEP" --arg state "$STATE" --arg repo "$REPO" --arg owner "$OWNER" --arg owner_type "$OWNER_TYPE" \
        --arg number "$PROJECT_NUMBER" --arg id "$PROJECT_ID" --arg url "$PROJECT_URL" --arg title "$PROJECT_TITLE" \
        --arg next "$NEXT" --arg did "$DID" --arg skipped "$SKIPPED" --arg conflicts "$CONFLICTS" --arg todo "$TODO" \
        --arg unverified "$UNVERIFIED" --argjson code "$1" '
        def lines: split("\n") | map(select(. != ""));
        { step: $step, state: $state, exit: $code, repo: $repo, owner: $owner, owner_type: $owner_type,
          project: (if $id == "" then null else
              { number: ($number | tonumber? // null), id: $id, title: $title, url: $url,
                workflows_url: (if $url == "" then null else $url + "/workflows" end) } end),
          next: (if $next == "" then null else $next end),
          did: ($did | lines), skipped: ($skipped | lines), conflicts: ($conflicts | lines),
          todo: ($todo | lines), unverified: ($unverified | lines) }'
    exit "$1"
}
blocked() { STATE=blocked; todo "$1"; finish 3; }       # a precondition failed
decide() { STATE=needs-decision; todo "$1"; finish 11; } # a person must choose
usage() { sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//' >&2; exit 2; }
trap 'echo "bootstrap.sh: failed at line $LINENO; rerunning the step is safe" >&2' ERR

gql() { # query, variables as JSON -> the response; gh exits non-zero on a GraphQL error
    jq -n --arg q "$1" --argjson v "${2:-{\}}" '{query: $q, variables: $v}' | gh api graphql --input -
}

# ---------------------------------------------------------------- options

[ $# -ge 1 ] || usage
STEP=$1; shift
REPO_PATH=. REMOTE=origin TITLE="" FLOW=pr ADOPT="" FORCE="" SMOKE="" DRY="" CONFIG_FILE="" DEST=""
while [ $# -gt 0 ]; do
    case $1 in
        --repo=* | --remote=* | --title=* | --flow=* | --adopt=* | --config=* | --dest=*)
            set -- "${1%%=*}" "${1#*=}" "${@:2}" ;;
        --repo) REPO_PATH=${2:?}; shift 2 ;;
        --remote) REMOTE=${2:?}; shift 2 ;;
        --title) TITLE=${2:?}; shift 2 ;;
        --flow) FLOW=${2:?}; shift 2 ;;
        --adopt) ADOPT=${2:?}; shift 2 ;;
        --config) CONFIG_FILE=${2:?}; shift 2 ;;
        --dest) DEST=${2:?}; shift 2 ;;
        --force) FORCE=1; shift ;;
        --smoke) SMOKE=1; shift ;;
        --dry-run) DRY=1; shift ;;
        -h | --help) usage ;;
        *) echo "bootstrap.sh: unknown option $1" >&2; usage ;;
    esac
done
case $FLOW in pr | main) ;; *) echo "bootstrap.sh: --flow is pr or main" >&2; exit 2 ;; esac
REPO_PATH=${REPO_PATH/#\~/$HOME}

# ---------------------------------------------------------------- the repo and the login

resolve_repo() { # REPO_PATH -> ROOT, REPO, OWNER, NAME, OWNER_TYPE, OWNER_ID, REPO_ID, DEFAULT_BRANCH; or blocked/decide
    local tool
    for tool in git gh jq; do
        command -v "$tool" >/dev/null 2>&1 || blocked "$tool is not installed (brew install $tool)"
    done
    ROOT=$(git -C "$REPO_PATH" rev-parse --show-toplevel 2>/dev/null) || blocked "$REPO_PATH is not a git repository"
    local url
    url=$(git -C "$ROOT" remote get-url "$REMOTE" 2>/dev/null) \
        || blocked "$ROOT has no remote named $REMOTE; add the GitHub remote, or pass --remote <name>"
    if [[ $url =~ github\.com[:/]([^/]+)/([^/]+)$ ]]; then
        OWNER=${BASH_REMATCH[1]}; NAME=${BASH_REMATCH[2]%.git}
    else
        blocked "the remote $REMOTE ($url) is not a github.com repository"
    fi
    gh auth status >/dev/null 2>&1 || blocked "gh is not logged in: run gh auth login"
    local scopes
    scopes=$(gh api -i user 2>/dev/null | tr -d '\r' | awk -F': ' 'tolower($1) == "x-oauth-scopes" { print $2 }') || true
    if [ -n "$scopes" ]; then
        [[ ", $scopes," == *", project,"* ]] || blocked "the gh token lacks the project scope: run gh auth refresh -s project"
    else
        warn "could not read the token's scopes (a fine-grained token has none to list); it needs to read and write projects"
    fi
    local r
    r=$(gh repo view "$OWNER/$NAME" --json id,nameWithOwner,isFork,isArchived,hasIssuesEnabled,viewerPermission,defaultBranchRef 2>/dev/null) \
        || blocked "gh cannot see $OWNER/$NAME: check the remote and your access"
    REPO=$(jq -r .nameWithOwner <<<"$r"); OWNER=${REPO%%/*}; NAME=${REPO#*/}
    REPO_ID=$(jq -r .id <<<"$r"); DEFAULT_BRANCH=$(jq -r '.defaultBranchRef.name // "main"' <<<"$r")
    [ "$(jq -r .isArchived <<<"$r")" = false ] || blocked "$REPO is archived"
    case $(jq -r .viewerPermission <<<"$r") in
        ADMIN | MAINTAIN | WRITE) ;;
        *) blocked "you need write access to $REPO to label issues and commit the hooks" ;;
    esac
    [ "$(jq -r .isFork <<<"$r")" = false ] || decide "$REPO is a fork; issue tracking belongs on the repo you own. Run this in the repo that should hold the issues"
    [ "$(jq -r .hasIssuesEnabled <<<"$r")" = true ] || decide "issues are switched off on $REPO; switch them on (gh repo edit $REPO --enable-issues) and run this again"
    local o
    o=$(gql 'query($l:String!){ repositoryOwner(login:$l){ __typename id } viewer { login } }' "$(jq -n --arg l "$OWNER" '{l: $l}')")
    OWNER_TYPE=$(jq -r .data.repositoryOwner.__typename <<<"$o"); OWNER_ID=$(jq -r .data.repositoryOwner.id <<<"$o")
    if [ "$OWNER_TYPE" = User ] && [ "$(jq -r .data.viewer.login <<<"$o")" != "$OWNER" ]; then
        blocked "$REPO belongs to the user $OWNER; only $OWNER can create a project board for it"
    fi
    [ -n "$TITLE" ] || TITLE="$NAME Roadmap"
    MARKER="Issue tracking for $REPO $MARKER_TAG"
    ok "$REPO ($OWNER_TYPE-owned, default branch $DEFAULT_BRANCH) at $ROOT"
}

# ---------------------------------------------------------------- the project

PROJECT_FIELDS='id number title url closed shortDescription'

take_project() { # a project node as JSON -> the PROJECT_* variables
    PROJECT_ID=$(jq -r .id <<<"$1"); PROJECT_NUMBER=$(jq -r .number <<<"$1")
    PROJECT_URL=$(jq -r .url <<<"$1"); PROJECT_TITLE=$(jq -r .title <<<"$1")
}

find_project() { # -> BOARD: foreign | ours | none, and for ours PROJECT_* and PROJECT_LINKED; or decide
    local linked owned mine
    linked=$(gql "query(\$o:String!,\$n:String!){ repository(owner:\$o,name:\$n){ projectsV2(first:20){ nodes { $PROJECT_FIELDS } } } }" \
        "$(jq -n --arg o "$OWNER" --arg n "$NAME" '{o: $o, n: $n}')" | jq -c '[.data.repository.projectsV2.nodes[]]')
    mine=$(jq -c --arg m "$MARKER" '[.[] | select(.shortDescription == $m)] | first // empty' <<<"$linked")
    if [ -n "$mine" ]; then
        take_project "$mine"; PROJECT_LINKED=1; BOARD=ours; return
    fi
    if [ -n "$ADOPT" ]; then
        mine=$(jq -c --argjson n "$ADOPT" '[.[] | select(.number == $n)] | first // empty' <<<"$linked")
        if [ -n "$mine" ]; then take_project "$mine"; PROJECT_LINKED=1; BOARD=ours; return; fi
    fi
    if [ "$(jq length <<<"$linked")" -gt 0 ]; then
        take_project "$(jq -c 'first' <<<"$linked")"; PROJECT_LINKED=1; BOARD=foreign; return
    fi
    owned=$(gql "query(\$l:String!){ repositoryOwner(login:\$l){ ... on ProjectV2Owner { projectsV2(first:100){ nodes { $PROJECT_FIELDS } } } } }" \
        "$(jq -n --arg l "$OWNER" '{l: $l}')" | jq -c '[.data.repositoryOwner.projectsV2.nodes[]]')
    mine=$(jq -c --arg m "$MARKER" '[.[] | select(.shortDescription == $m)] | first // empty' <<<"$owned")
    if [ -z "$mine" ] && [ -n "$ADOPT" ]; then
        mine=$(jq -c --argjson n "$ADOPT" '[.[] | select(.number == $n)] | first // empty' <<<"$owned")
        [ -n "$mine" ] || decide "$OWNER has no project number $ADOPT to adopt"
    fi
    if [ -n "$mine" ]; then take_project "$mine"; PROJECT_LINKED=""; BOARD=ours; return; fi
    mine=$(jq -c --arg t "$TITLE" '[.[] | select(.title == $t)] | first // empty' <<<"$owned")
    if [ -n "$mine" ]; then
        take_project "$mine"
        decide "$OWNER already has a project titled \"$TITLE\" ($PROJECT_URL) that is not linked to $REPO. To use it, run again with --adopt $PROJECT_NUMBER; to leave it alone and make a new board, run again with --title \"<another title>\""
    fi
    BOARD=none
}

single_selects() { # -> the project's single-select fields as JSON: [{id, name, options: [{id, name, color, description}]}]
    gql 'query($p:ID!){ node(id:$p){ ... on ProjectV2 { fields(first:50){ nodes {
        __typename ... on ProjectV2FieldCommon { id name } ... on ProjectV2SingleSelectField { options { id name color description } } } } } } }' \
        "$(jq -n --arg p "$PROJECT_ID" '{p: $p}')" | jq -c '[.data.node.fields.nodes[]]'
}

WANT_STATUS='[{"name":"Backlog","color":"GRAY","description":"Filed, not yet planned"},
 {"name":"Todo","color":"BLUE","description":"Planned, not started"},
 {"name":"In Progress","color":"YELLOW","description":"Being worked on"},
 {"name":"Done","color":"GREEN","description":"Closed or merged"}]'
WANT_PRIORITY='[{"name":"P0","color":"RED","description":"Critical"},
 {"name":"P1","color":"ORANGE","description":"High"},
 {"name":"P2","color":"YELLOW","description":"Medium"},
 {"name":"P3","color":"GRAY","description":"Low"}]'

missing_options() { # fields JSON, field name, wanted options JSON -> the wanted names the field lacks, comma-separated
    jq -r --arg f "$2" --argjson want "$3" \
        '([.[] | select(.name == $f) | (.options // [])[] | .name]) as $have | [$want[] | .name | select(. as $n | $have | index($n) | not)] | join(", ")' <<<"$1"
}

merged_options() { # fields JSON, field name, wanted options JSON -> the full option list to send: wanted first, in
    # order, each keeping its id where the field has that name already; then the field's other options, as they are.
    # An option sent with its id keeps its identity, so no item loses its value.
    jq -c --arg f "$2" --argjson want "$3" '
        ([.[] | select(.name == $f) | (.options // [])[]]) as $have
        | [ $want[] | . as $w | ([$have[] | select(.name == $w.name) | .id] | first) as $id
            | if $id then $w + {id: $id} else $w end ]
          + [ $have[] | select(.name as $n | [$want[].name] | index($n) | not) | {id, name, color, description} ]' <<<"$1"
}

fields_ready() { # whether Status and Priority carry every option the system uses
    local f; f=$(single_selects)
    [ -z "$(missing_options "$f" Status "$WANT_STATUS")" ] \
        && [ -n "$(jq -r '.[] | select(.name == "Priority") | .id' <<<"$f")" ] \
        && [ -z "$(missing_options "$f" Priority "$WANT_PRIORITY")" ]
}

workflows() { # -> the project's workflows as JSON: [{name, number, enabled}]
    gql 'query($p:ID!){ node(id:$p){ ... on ProjectV2 { workflows(first:30){ nodes { name number enabled } } } } }' \
        "$(jq -n --arg p "$PROJECT_ID" '{p: $p}')" | jq -c '[.data.node.workflows.nodes[]]'
}

workflows_missing() { # -> the required workflows that are absent or off, one per line
    local w name; w=$(workflows)
    while IFS= read -r name; do
        [ "$(jq -r --arg n "$name" '[.[] | select(.name == $n and .enabled)] | length' <<<"$w")" -gt 0 ] || echo "$name"
    done <<<"$REQUIRED_WORKFLOWS"
}

# ---------------------------------------------------------------- the files

file_plan() { # flow -> one line per file to place: mode|source under assets/|destination under the repo
    # same  the file is ours and identical in every repo: placed, and a different one already there is a conflict
    # keep  the file is a starting point: placed when absent, and one already there is kept
    cat <<EOF
same|skills/issues/scripts/issue.sh|.claude/skills/issues/scripts/issue.sh
same|hooks/guard-gh-issue-create.sh|.claude/hooks/guard-gh-issue-create.sh
same|hooks/guard-gh-pr-create.sh|.claude/hooks/guard-gh-pr-create.sh
same|hooks/board-new-issue.sh|.claude/hooks/board-new-issue.sh
same|hooks/audit-after-merge.sh|.claude/hooks/audit-after-merge.sh
same|hooks/audit-after-push.sh|.claude/hooks/audit-after-push.sh
same|github/ISSUE_TEMPLATE/epic.yml|.github/ISSUE_TEMPLATE/epic.yml
same|github/ISSUE_TEMPLATE/spec.yml|.github/ISSUE_TEMPLATE/spec.yml
same|github/ISSUE_TEMPLATE/feature.yml|.github/ISSUE_TEMPLATE/feature.yml
same|github/ISSUE_TEMPLATE/bug.yml|.github/ISSUE_TEMPLATE/bug.yml
keep|github/ISSUE_TEMPLATE/config.yml|.github/ISSUE_TEMPLATE/config.yml
EOF
    [ "$1" = main ] || echo "keep|github/pull_request_template.md|.github/pull_request_template.md"
}

render_skill() { # -> the installed SKILL.md on stdout, the template with this repo's names in it
    jq -Rr --arg repo "$REPO" --arg name "$NAME" --arg title "$PROJECT_TITLE" --arg url "$PROJECT_URL" '
        split("{{REPO}}") | join($repo) | split("{{NAME}}") | join($name)
        | split("{{PROJECT_TITLE}}") | join($title) | split("{{PROJECT_URL}}") | join($url)' \
        "$ASSETS/skills/issues/SKILL.md.tmpl"
}

merged_settings() { # the current settings.json (or {}) on stdin -> it with the hook wiring and the allow rule added.
    # Nothing already there is changed or removed. A hook is added to the event's group with the same matcher (or
    # as a new group) only when its command is not already wired for that event, so a second merge changes nothing.
    jq --slurpfile add "$ASSETS/settings.hooks.json" '
        $add[0] as $a
        | (.permissions.allow // []) as $have
        | .permissions.allow = $have + [ $a.permissions.allow[] | select(. as $x | $have | index($x) | not) ]
        | reduce ($a.hooks | to_entries[]) as $ev (.;
            reduce $ev.value[] as $grp (.;
                (.hooks[$ev.key] // []) as $groups
                | [ $groups[] | (.hooks // [])[] | .command ] as $wired
                | [ $grp.hooks[] | select(.command as $c | $wired | index($c) | not) ] as $new
                | ($groups | map(.matcher) | index($grp.matcher)) as $i
                | if ($new | length) == 0 then .
                  elif $i == null then .hooks[$ev.key] = $groups + [$grp + {hooks: $new}]
                  else .hooks[$ev.key][$i].hooks += $new end))'
}

place_files() { # destination root, flow -> the files placed (or, under --dry-run, said); conflicts stop it first
    local dest=$1 flow=$2 mode src to rendered settings cur new
    rendered=$(mktemp); render_skill >"$rendered"
    # 1. what is already there and differs: said before anything is written
    while IFS='|' read -r mode src to; do
        [ "$mode" = same ] && [ -f "$dest/$to" ] && ! cmp -s "$ASSETS/$src" "$dest/$to" || continue
        replaceable "$dest" "$to" || conflict "$to exists and differs from the one this skill installs"
    done <<<"$(file_plan "$flow")"
    to=.claude/skills/issues/SKILL.md
    if [ -f "$dest/$to" ] && ! cmp -s "$rendered" "$dest/$to"; then
        replaceable "$dest" "$to" || conflict "$to exists and differs from the one this skill installs"
    fi
    settings=$dest/.claude/settings.json
    if [ -f "$settings" ]; then
        jq -e . "$settings" >/dev/null 2>&1 || { rm -f "$rendered"; blocked ".claude/settings.json is not valid JSON; fix it and run this again (it was not touched)"; }
        cur=$(cat "$settings")
    else
        cur='{}'
    fi
    if [ -n "$CONFLICTS" ]; then
        rm -f "$rendered"
        decide "these files already exist with other content. Move them aside, or commit them and run again with --force to replace the ones git can restore"
    fi
    # 2. place
    while IFS='|' read -r mode src to; do
        if [ -f "$dest/$to" ] && { [ "$mode" = keep ] || cmp -s "$ASSETS/$src" "$dest/$to"; }; then
            if [ "$mode" = keep ] && ! cmp -s "$ASSETS/$src" "$dest/$to"; then skip "$to (yours is kept)"; else skip "$to (already in place)"; fi
            continue
        fi
        if [ -n "$DRY" ]; then would "write $to"; continue; fi
        mkdir -p "$(dirname "$dest/$to")"
        cp "$ASSETS/$src" "$dest/$to"
        case $to in *.sh) chmod 755 "$dest/$to" ;; esac
        did "wrote $to"
    done <<<"$(file_plan "$flow")"
    to=.claude/skills/issues/SKILL.md
    if [ -f "$dest/$to" ] && cmp -s "$rendered" "$dest/$to"; then skip "$to (already in place)"
    elif [ -n "$DRY" ]; then would "write $to"
    else mkdir -p "$(dirname "$dest/$to")"; cp "$rendered" "$dest/$to"; did "wrote $to"; fi
    rm -f "$rendered"
    # 3. the hook wiring
    new=$(merged_settings <<<"$cur")
    if [ "$(jq -S . <<<"$cur")" = "$(jq -S . <<<"$new")" ]; then skip ".claude/settings.json (hooks already wired)"
    elif [ -n "$DRY" ]; then would "wire the hooks into .claude/settings.json"
    else
        mkdir -p "$dest/.claude"
        printf '%s\n' "$new" >"$settings.tmp.$$"
        jq -e . "$settings.tmp.$$" >/dev/null
        command mv -f "$settings.tmp.$$" "$settings"
        did "wired the hooks into .claude/settings.json"
    fi
}

replaceable() { # root, path -> whether --force may replace the file: git tracks it and it has no uncommitted change
    [ -n "$FORCE" ] || return 1
    git -C "$1" ls-files --error-unmatch -- "$2" >/dev/null 2>&1 && git -C "$1" diff --quiet HEAD -- "$2" 2>/dev/null
}

files_ready() { # whether every file the system needs is in place in ROOT and the hooks are wired
    local mode src to
    while IFS='|' read -r mode src to; do
        [ -f "$ROOT/$to" ] || return 1
        [ "$mode" = keep ] || cmp -s "$ASSETS/$src" "$ROOT/$to" || return 1
    done <<<"$(file_plan main)"
    [ -f "$ROOT/.claude/skills/issues/SKILL.md" ] && [ -f "$ROOT/.claude/skills/issues/board.env" ] || return 1
    grep -q "^PROJECT_ID=$PROJECT_ID\$" "$ROOT/.claude/skills/issues/board.env" || return 1
    [ -f "$ROOT/.claude/settings.json" ] || return 1
    local cur; cur=$(cat "$ROOT/.claude/settings.json")
    [ "$(jq -S . <<<"$cur" 2>/dev/null)" = "$(merged_settings <<<"$cur" 2>/dev/null | jq -S .)" ]
}

write_seed_env() { # file -> a board.env holding what GitHub cannot be asked by project id; issue.sh ids --write fills the rest
    local k
    {
        echo "# The repo and its project board, read by issue.sh and the hooks in .claude/hooks/. Commit this file."
        for k in REPO OWNER NAME DEFAULT_BRANCH PROJECT_ID; do printf '%s=%q\n' "$k" "${!k}"; done
    } >"$1"
}

# ---------------------------------------------------------------- steps

step_preflight() {
    resolve_repo
    find_project
    local open
    case $BOARD in
        foreign)
            STATE=has-board
            ok "$REPO already has a project board: $PROJECT_TITLE ($PROJECT_URL). Nothing to do, nothing changed"
            finish 10 ;;
        none)
            open=$(gh issue list --repo "$REPO" --state open --limit 200 --json number -q length)
            [ "$open" -eq 0 ] || warn "$REPO has $open open issues filed before the board; this setup does not label them or add them to the board, and issue.sh check will list them until someone does"
            STATE=fresh; NEXT=github
            ok "no project board yet; this would create \"$TITLE\" for $OWNER"
            finish 0 ;;
    esac
    if [ -z "$PROJECT_LINKED" ] || ! fields_ready; then
        STATE=resume; NEXT=github; ok "the board $PROJECT_URL was started by this skill and is not finished"; finish 0
    fi
    if ! files_ready; then
        STATE=resume; NEXT=files; ok "the board $PROJECT_URL is ready; the files in the repo are not all in place"; finish 0
    fi
    if [ -n "$(workflows_missing)" ]; then
        STATE=resume; NEXT=verify; ok "the board and the files are ready; the board's workflows are not all switched on"; finish 0
    fi
    STATE=complete
    ok "$REPO is already set up: $PROJECT_TITLE ($PROJECT_URL). Nothing to do, nothing changed"
    finish 10
}

step_github() {
    resolve_repo
    find_project
    if [ "$BOARD" = foreign ]; then
        STATE=has-board; ok "$REPO already has a project board: $PROJECT_TITLE ($PROJECT_URL). Nothing changed"; finish 10
    fi

    # the five kind labels; one already there keeps its colour and description
    local have label color description
    have=$(gh label list --repo "$REPO" --limit 300 --json name -q '.[].name')
    while IFS='|' read -r label color description; do
        if grep -qxF -- "$label" <<<"$have"; then skip "label $label (already there, left as it is)"
        elif [ -n "$DRY" ]; then would "create the label $label"
        else gh label create "$label" --repo "$REPO" --color "$color" --description "$description" >/dev/null; did "created the label $label"; fi
    done <<'EOF'
epic|6f42c1|A multi-spec initiative; specs hang off it, never tasks directly
spec|8250df|A design or plan to refine before building; tasks hang off it
feature|2da44e|A bounded user-facing enhancement that lands in one PR or commit
bug|d73a4a|Something that should work and doesn't
task|bfd4f2|A unit of implementation; usually a child of a spec
EOF

    # the project: created unlinked and marked as ours at once, so a rerun after a crash finds it
    if [ "$BOARD" = none ]; then
        if [ -n "$DRY" ]; then
            would "create the project \"$TITLE\" for $OWNER"
            would "add Backlog to its Status field, create its Priority field (P0 to P3), link it to $REPO"
            STATE=dry-run; finish 0
        fi
        local made
        made=$(gql "mutation(\$o:ID!,\$t:String!){ createProjectV2(input:{ownerId:\$o, title:\$t}){ projectV2 { $PROJECT_FIELDS } } }" \
            "$(jq -n --arg o "$OWNER_ID" --arg t "$TITLE" '{o: $o, t: $t}')")
        take_project "$(jq -c .data.createProjectV2.projectV2 <<<"$made")"
        did "created the project \"$PROJECT_TITLE\" ($PROJECT_URL)"
        PROJECT_LINKED=""
        set_marker
    elif [ -n "$ADOPT" ] && [ -z "$DRY" ]; then
        set_marker
        did "adopted the project \"$PROJECT_TITLE\" ($PROJECT_URL)"
    else
        skip "project \"$PROJECT_TITLE\" (already there: $PROJECT_URL)"
    fi

    # Status: Backlog, Todo, In Progress, Done. A new project has the last three; the others keep their ids
    local fields field_id missing options
    fields=$(single_selects)
    field_id=$(jq -r '.[] | select(.name == "Status") | .id' <<<"$fields")
    [ -n "$field_id" ] || decide "the project has no Status field; add a single-select field named Status on the board and run this again"
    missing=$(missing_options "$fields" Status "$WANT_STATUS")
    if [ -z "$missing" ]; then skip "Status options (all four already there)"
    elif [ -n "$DRY" ]; then would "add the Status options: $missing"
    else
        options=$(merged_options "$fields" Status "$WANT_STATUS")
        gql 'mutation($f:ID!,$o:[ProjectV2SingleSelectFieldOptionInput!]){ updateProjectV2Field(input:{fieldId:$f, singleSelectOptions:$o}){ projectV2Field { ... on ProjectV2SingleSelectField { id } } } }' \
            "$(jq -n --arg f "$field_id" --argjson o "$options" '{f: $f, o: $o}')" >/dev/null
        did "added the Status options: $missing"
    fi

    # Priority: P0 to P3
    field_id=$(jq -r '.[] | select(.name == "Priority") | .id' <<<"$fields")
    if [ -z "$field_id" ]; then
        if [ -n "$DRY" ]; then would "create the Priority field (P0 to P3)"
        else
            gql 'mutation($p:ID!,$o:[ProjectV2SingleSelectFieldOptionInput!]){ createProjectV2Field(input:{projectId:$p, dataType:SINGLE_SELECT, name:"Priority", singleSelectOptions:$o}){ projectV2Field { ... on ProjectV2SingleSelectField { id } } } }' \
                "$(jq -n --arg p "$PROJECT_ID" --argjson o "$WANT_PRIORITY" '{p: $p, o: $o}')" >/dev/null
            did "created the Priority field (P0 to P3)"
        fi
    elif [ "$(jq -r '.[] | select(.name == "Priority") | .__typename' <<<"$fields")" != ProjectV2SingleSelectField ]; then
        decide "the project has a Priority field that is not a single select; rename or remove it on the board and run this again"
    else
        missing=$(missing_options "$fields" Priority "$WANT_PRIORITY")
        if [ -z "$missing" ]; then skip "Priority options (P0 to P3 already there)"
        elif [ -n "$DRY" ]; then would "add the Priority options: $missing"
        else
            options=$(merged_options "$fields" Priority "$WANT_PRIORITY")
            gql 'mutation($f:ID!,$o:[ProjectV2SingleSelectFieldOptionInput!]){ updateProjectV2Field(input:{fieldId:$f, singleSelectOptions:$o}){ projectV2Field { ... on ProjectV2SingleSelectField { id } } } }' \
                "$(jq -n --arg f "$field_id" --argjson o "$options" '{f: $f, o: $o}')" >/dev/null
            did "added the Priority options: $missing"
        fi
    fi

    # the link to the repo, last: until it is there the repo does not show a board, so a half-made one is never
    # mistaken for a board someone else set up
    if [ -n "$PROJECT_LINKED" ]; then skip "link to $REPO (already linked)"
    elif [ -n "$DRY" ]; then would "link the project to $REPO"
    else
        gql 'mutation($p:ID!,$r:ID!){ linkProjectV2ToRepository(input:{projectId:$p, repositoryId:$r}){ repository { id } } }' \
            "$(jq -n --arg p "$PROJECT_ID" --arg r "$REPO_ID" '{p: $p, r: $r}')" >/dev/null
        did "linked the project to $REPO"
    fi
    if [ -n "$DRY" ]; then STATE=dry-run; else STATE="done"; NEXT=files; fi
    finish 0
}

set_marker() { # the project's short description says whose board it is; preflight and a rerun recognise it by this
    gql 'mutation($p:ID!,$d:String!){ updateProjectV2(input:{projectId:$p, shortDescription:$d}){ projectV2 { id } } }' \
        "$(jq -n --arg p "$PROJECT_ID" --arg d "$MARKER" '{p: $p, d: $d}')" >/dev/null
}

step_files() {
    resolve_repo
    find_project
    if [ "$BOARD" = foreign ]; then
        STATE=has-board; ok "$REPO already has a project board: $PROJECT_TITLE ($PROJECT_URL). Nothing changed"; finish 10
    fi
    if [ "$BOARD" = none ]; then
        [ -n "$DRY" ] || { STATE=blocked; todo "there is no board yet: run the github step first"; finish 1; }
        PROJECT_TITLE=$TITLE; PROJECT_URL="(the new board's url)"
    fi
    # a path git ignores would never reach a teammate or another agent
    local ignored
    ignored=$(cd "$ROOT" && git check-ignore .claude/settings.json .claude/hooks/board-new-issue.sh \
        .claude/skills/issues/SKILL.md .claude/skills/issues/board.env .github/ISSUE_TEMPLATE/spec.yml 2>/dev/null | paste -sd' ' - || true)
    [ -z "$ignored" ] || decide "git ignores these paths, so the setup would not reach anyone else: $ignored. Change .gitignore and run this again"

    local env=$ROOT/.claude/skills/issues/board.env
    if [ -f "$env" ] && [ "$BOARD" = ours ] && ! grep -q "^PROJECT_ID=$PROJECT_ID\$" "$env"; then
        replaceable "$ROOT" .claude/skills/issues/board.env \
            || conflict ".claude/skills/issues/board.env points at another project board"
    fi
    place_files "$ROOT" "$FLOW"

    if [ -n "$DRY" ]; then
        would "write .claude/skills/issues/board.env with the board's ids"
        STATE=dry-run; finish 0
    fi
    if [ -f "$env" ] && grep -q "^PROJECT_ID=$PROJECT_ID\$" "$env"; then :; else write_seed_env "$env"; fi
    local report
    if report=$(/bin/bash "$ROOT/.claude/skills/issues/scripts/issue.sh" ids --write 2>&1); then
        if grep -q rewritten <<<"$report"; then did "wrote .claude/skills/issues/board.env with the board's ids"
        else skip ".claude/skills/issues/board.env (ids already right)"; fi
    else
        echo "$report" >&2
        STATE=blocked; todo "the board lacks a field or option the system needs (see the log): run the github step again"; finish 1
    fi
    STATE="done"; NEXT=verify
    finish 0
}

status_of() { # issue number -> its Status on the board, or nothing
    /bin/bash "$ROOT/.claude/skills/issues/scripts/issue.sh" board "$1" 2>/dev/null | sed -n 's/.*Status=\(.*\)$/\1/p'
}

wait_status() { # issue number, wanted status, seconds -> whether the board shows it in time
    local i
    for ((i = 0; i < $3; i += 5)); do
        [ "$(status_of "$1")" = "$2" ] && return 0
        sleep 5
    done
    return 1
}

on_board() { # issue number -> whether the issue is an item of the project (read only: nothing is added)
    gql 'query($o:String!,$n:String!,$i:Int!){ repository(owner:$o,name:$n){ issue(number:$i){ projectItems(first:10){ nodes { project { id } } } } } }' \
        "$(jq -n --arg o "$OWNER" --arg n "$NAME" --argjson i "$1" '{o: $o, n: $n, i: $i}')" \
        | jq -e --arg p "$PROJECT_ID" '[.data.repository.issue.projectItems.nodes[] | select(.project.id == $p)] | length > 0' >/dev/null
}

step_verify() {
    resolve_repo
    find_project
    [ "$BOARD" = ours ] || { STATE=blocked; todo "this repo has no board made by this skill: run preflight"; finish 1; }
    [ -f "$ROOT/.claude/skills/issues/board.env" ] || { STATE=blocked; todo "the files are not in place: run the files step first"; finish 1; }

    local missing name
    missing=$(workflows_missing)
    if [ -n "$missing" ]; then
        while IFS= read -r name; do todo "switch on the workflow \"$name\" at $PROJECT_URL/workflows"; done <<<"$missing"
        STATE=needs-github-ui; finish 12
    fi
    ok "the board's three workflows are switched on"

    if [ -z "$SMOKE" ]; then
        unverified "that new issues in $REPO are added to the board by themselves (the auto-add workflow's repository and filter)"
        unverified "that closing an issue sets Status to Done"
        unverified "that reopening an issue sets Status to Todo"
        STATE=done-unverified; finish 0
    fi

    # one real issue through the board: filed with a plain gh issue create, so only the board's own automation can
    # have added it; it stays, closed, as the record of the setup
    local n body url
    n=$(gh issue list --repo "$REPO" --state all --limit 300 --json number,title -q "[.[] | select(.title == \"$SMOKE_TITLE\") | .number] | first // empty")
    if [ -n "$n" ]; then
        ok "reusing #$n \"$SMOKE_TITLE\""
        [ "$(gh issue view "$n" --repo "$REPO" --json state -q .state)" = OPEN ] || gh issue reopen "$n" --repo "$REPO" >/dev/null
    else
        body=$(mktemp)
        cat >"$body" <<EOF
### Goal

Track work for this repo as GitHub Issues on the project board $PROJECT_URL.

### Steps

1. The kind labels: epic, spec, feature, bug, task.
2. The board "$PROJECT_TITLE", with Status (Backlog, Todo, In Progress, Done) and Priority (P0 to P3).
3. In the repo: the issues skill (\`.claude/skills/issues/\`), the hooks (\`.claude/hooks/\`, wired in \`.claude/settings.json\`) and the issue templates (\`.github/ISSUE_TEMPLATE/\`).
4. On the board: the workflows that add new issues, set Done on close and Todo on reopen.

### Done when

- [x] This issue reached the board by itself, went to Done when closed and to Todo when reopened.
EOF
        url=$(gh issue create --repo "$REPO" --label task --title "$SMOKE_TITLE" --body-file "$body")
        rm -f "$body"; n=${url##*/}
        did "filed #$n \"$SMOKE_TITLE\""
    fi
    local i added=""
    for ((i = 0; i < 90; i += 5)); do
        if on_board "$n"; then added=1; break; fi
        sleep 5
    done
    if [ -z "$added" ]; then
        todo "#$n was not added to the board within 90 seconds: open \"Auto-add to project\" at $PROJECT_URL/workflows, check the repository is $NAME and the filter is is:issue, save and switch it on, then run verify --smoke again"
        STATE=needs-github-ui; finish 12
    fi
    ok "#$n reached the board by itself"
    /bin/bash "$ROOT/.claude/skills/issues/scripts/issue.sh" board "$n" --status Backlog --priority P3 >/dev/null
    ok "#$n set to Backlog, P3 through the installed issue.sh"
    gh issue close "$n" --repo "$REPO" --reason completed >/dev/null
    if ! wait_status "$n" Done 60; then
        todo "closing #$n did not set Status to Done: open \"Item closed\" at $PROJECT_URL/workflows, set Status to Done, save and switch it on, then run verify --smoke again"
        STATE=needs-github-ui; finish 12
    fi
    ok "closing #$n set Status to Done"
    gh issue reopen "$n" --repo "$REPO" >/dev/null
    if ! wait_status "$n" Todo 60; then
        todo "reopening #$n did not set Status to Todo: open \"Item reopened\" at $PROJECT_URL/workflows, set Status to Todo, save and switch it on, then run verify --smoke again"
        STATE=needs-github-ui; finish 12
    fi
    ok "reopening #$n set Status to Todo"
    gh issue close "$n" --repo "$REPO" --reason completed >/dev/null
    wait_status "$n" Done 60 || warn "#$n is closed again but the board does not show Done yet"
    did "cycled #$n through the board: added by itself, Done on close, Todo on reopen"
    local report
    if report=$(/bin/bash "$ROOT/.claude/skills/issues/scripts/issue.sh" check 2>&1); then
        ok "issue.sh check: $(tail -1 <<<"$report")"
    else
        echo "$report" >&2
        unverified "issue.sh check reports failures (see the log); issues filed before the board need a kind label, a priority and a place on the board"
    fi
    STATE="done"; finish 0
}

step_render() { # the files step into DEST from a board.env, offline: what the tests and the golden check run
    [ -n "$CONFIG_FILE" ] && [ -f "$CONFIG_FILE" ] && [ -n "$DEST" ] || usage
    # shellcheck disable=SC1090 # a board.env given on the command line
    . "$CONFIG_FILE"
    : "${REPO:?the config has no REPO}" "${NAME:?the config has no NAME}" "${PROJECT_TITLE:?the config has no PROJECT_TITLE}" "${PROJECT_URL:?the config has no PROJECT_URL}"
    mkdir -p "$DEST"
    place_files "$DEST" "$FLOW"
    mkdir -p "$DEST/.claude/skills/issues"
    cmp -s "$CONFIG_FILE" "$DEST/.claude/skills/issues/board.env" || cp "$CONFIG_FILE" "$DEST/.claude/skills/issues/board.env"
    STATE="done"; finish 0
}

case $STEP in
    preflight) step_preflight ;;
    github) step_github ;;
    files) step_files ;;
    verify) step_verify ;;
    render) step_render ;;
    -h | --help | help) usage ;;
    *) echo "bootstrap.sh: unknown step '$STEP'" >&2; usage ;;
esac
