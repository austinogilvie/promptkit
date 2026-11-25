# Maintaining this skill

## Where the bundled files come from

Everything under `assets/` was generalised from a working setup in the `SixThirty-Ventures/switchyard` repo
(`.claude/skills/issues/`, `.claude/hooks/`, `.github/`). That repo still carries its own, older copy with its
repo and board ids written into the scripts. The differences, which are the whole of the generalisation:

| file | change from the original |
|---|---|
| `skills/issues/scripts/issue.sh` | reads the repo, the board and its ids from `board.env` (`load_config`) instead of constants; finds a board item by project id, not project number; adds to the board with `addProjectV2ItemById`; new `ids [--write]` command; `ROOT` is always worked out from the script's own path |
| `skills/issues/SKILL.md.tmpl` | `{{REPO}}`, `{{NAME}}`, `{{PROJECT_TITLE}}`, `{{PROJECT_URL}}` placeholders; a "Landing work" section covering commits on the default branch as well as pull requests; the ids block points at `board.env`; no repo-specific labels or examples |
| `hooks/board-new-issue.sh` | reads the repo from `board.env`; ignores an issue filed in another repo |
| `hooks/guard-gh-pr-create.sh` | the default branch comes from `board.env`, not the literal `main` |
| `hooks/audit-after-push.sh` | new: the audit after a push of the default branch |
| `hooks/guard-gh-issue-create.sh`, `hooks/audit-after-merge.sh` | none |
| `github/ISSUE_TEMPLATE/feature.yml` | one placeholder sentence no longer names the original repo |
| the other templates | none |
| `settings.hooks.json` | only the hook wiring and the `issue.sh check` allow rule, plus the push audit |

Only `SKILL.md.tmpl` is rendered. Every other installed file is byte-identical in every repo, so
`cmp` against `assets/` says whether a repo's copy is current, and rerunning the `files` step is the update.
The step knows the repo is one of its own when the linked board carries the marker and the repo's `board.env`
names that board; it then replaces its own files that differ, committed or not, except a tracked file with an
uncommitted change (someone's edit in progress), which stops it with exit 11. In a repo it did not set up, a
differing file is a conflict, and `--force` replaces only one git tracks with no uncommitted change.

`board.env` holds everything that differs between repos. `bootstrap.sh files` writes five seed values (repo,
owner, name, default branch, project id) and the installed `issue.sh ids --write` fills in the rest by asking
the board for its fields by name, so there is one place that resolves ids.

## How a rerun knows whose board it is

`bootstrap.sh github` creates the project unlinked, writes a marker into its short description
(`Issue tracking for <owner>/<repo> (setting-up-github-project-tracking)`), builds the fields, and links the
project to the repo last. So:

- a linked project without the marker is someone else's board: exit 10, nothing changed;
- a project with the marker, linked or not, is a run of this skill: resume it;
- an unlinked project with the default title and no marker is ambiguous: exit 11, and `--adopt N` or
  `--title` decides.

Do not change the marker's text: existing boards are recognised by it.

## Tests to run after a change

None of these creates anything on GitHub. `B` is `scripts/bootstrap.sh`, `T` a scratch directory.

1. Syntax and lint, under the bash macOS ships:
   `/bin/bash -n` and `shellcheck -S warning` on `scripts/bootstrap.sh`, `assets/skills/issues/scripts/issue.sh`
   and `assets/hooks/*.sh`.
2. Offline render. Write a `board.env` (the keys are listed in `CONFIG_KEYS` in `issue.sh`) and run
   `$B render --config $T/board.env --dest $T/out`. Expect exit 0, every file in place, the hooks executable,
   no `{{` left in `$T/out/.claude/skills/issues/SKILL.md`. Run it a second time: `did` must be empty.
3. Settings merge. Run the render into a directory holding, in turn: no `.claude/settings.json`; one with
   other hooks under the `Bash` matcher and under other events; one that is not valid JSON. Expect the other
   content untouched, the invalid file refused with exit 3 and not modified, and a second run changing nothing.
4. `issue.sh kind "[Bug] x"` prints `bug` with no `board.env` anywhere (the hooks depend on this).
5. Read-only against a repo that already uses the system: `ISSUES_BOARD_ENV=<its board.env> issue.sh ids`
   reports no drift, and `issue.sh check` runs.
6. Read-only against GitHub: `$B preflight --repo <a repo with a board>` exits 10; `$B preflight`,
   `$B github --dry-run` and `$B files --dry-run` on a repo without one print only `would` lines and leave
   `git status` clean.
7. `python3 ../skill-creator/scripts/quick_validate.py .` from the skill's folder.

## Found on the first live run (sixthirty-aikit, 2026-11-25)

- `status_of` in `bootstrap.sh` read `Status=Done Priority=P3` as the status `Done Priority=P3`, so the smoke
  test could not pass on an issue that had a priority. The offline tests never ran `verify`; nothing but a
  live run reaches it.
- The skill was fixed while the repo's install was still uncommitted, and the `files` step refused to replace
  its own two out-of-date files. The update rule above came from that.
- GitHub's issue statuses and "Sync with issue status" (see `github-ui-steps.md`) put a reopened issue in
  Backlog. The smoke test demanded Todo and blamed the person's "Item reopened" setting, which was right.

## Known limits

- github.com only; a GitHub Enterprise host is refused at preflight.
- A fork is refused: tracking belongs on the repo that owns the issues.
- A repo owned by a user account works only for that user (a user's project can link only to that user's
  repos). The user-owned path has been run read-only (`preflight`), not through a full setup; the first full
  run on a personal repo is its test.
- The board's views are left as GitHub creates them. Grouping a board view by Status is a UI step with no API.
- Issues filed before the setup are not labelled or added to the board; `issue.sh check` lists them.
