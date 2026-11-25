---
name: setting-up-github-project-tracking
description: Sets up GitHub issue tracking for a repo - the kind labels (epic, spec, feature, bug, task), a GitHub Projects board with Status and Priority, an issues skill with its issue.sh script, guard hooks, and issue templates. Use when the user asks to set up project tracking, a project board, a roadmap board, issue tracking or a backlog for a repo, or runs /setting-up-github-project-tracking. Stops without changing anything when the repo already has a project board.
argument-hint: "[--repo=PATH] [--flow=pr|main] [--title=BOARD TITLE] [--dry-run]"
disable-model-invocation: true
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/bootstrap.sh *)
---

# Setting up GitHub project tracking

Gives a repo the tracking system described in `assets/skills/issues/SKILL.md.tmpl`: GitHub Issues with exactly
one kind label each, a project board that holds status and priority, a script (`issue.sh`) that files, links
and audits issues, and hooks that repair raw `gh` commands.

All the work is done by one script, a step at a time. Your job is to run the steps in order, read each
result, and talk to the person at the two points that need them.

```bash
B="${CLAUDE_SKILL_DIR}/scripts/bootstrap.sh"   # the folder holding this file, when the variable is not expanded
```

## Arguments

`$ARGUMENTS` may hold:

- `--repo=PATH`: the repo to set up. Default: the current directory.
- `--flow=pr|main`: how work lands. `pr` (default) also installs a pull request template. `main` is for a repo
  where a change is a commit on the default branch; it leaves the template out. If the repo's README or
  CLAUDE.md says which it is, use that; if it is unclear, ask.
- `--title=...`: the board's title. Default: `<repo> Roadmap`.
- `--dry-run`: run steps 1 to 3 with `--dry-run`, show what would happen, and stop.

Pass `--repo` to every step. Pass `--title` to `preflight` and `github`, `--flow` to `files`.

## Reading a step's result

Each step prints one JSON object on stdout (`state`, `project`, `did`, `skipped`, `conflicts`, `todo`,
`unverified`, `next`) and a log on stderr. Act on the exit code:

| exit | meaning | do |
|---|---|---|
| 0 | the step is done, or was already | go on to the next step |
| 10 | the repo already has a project board; nothing was changed | tell the person which board (`project.url`) and stop. This is a normal ending, not an error |
| 11 | a person must decide something | show them `todo` in plain words, and rerun with the flag it names |
| 12 | steps in GitHub's web UI are outstanding | show the checklist (step 4), wait, run `verify` again |
| 3 | a precondition failed | relay the one-line fix in `todo` and stop |
| 1 | something unexpected | show the log; rerunning the step is safe |

Every step is idempotent and works out where things stand from GitHub, so after any interruption, start
again at step 1: `preflight` says in `next` which step to resume at.

## Steps

1. **Preflight** (read-only).

   ```bash
   "$B" preflight --repo PATH
   ```

   On exit 10, stop. Otherwise tell the person in two or three lines what is about to be created (the board's
   title and owner, the labels, the files) before going on. If the log warns about open issues filed before
   the board, pass that on.

2. **GitHub**: labels, the project, its fields, the link to the repo.

   ```bash
   "$B" github --repo PATH --dry-run    # show the "would" lines first
   "$B" github --repo PATH
   ```

3. **Files**: the issues skill, hooks, templates, `board.env`, and the hook wiring in `.claude/settings.json`.

   ```bash
   "$B" files --repo PATH --flow pr|main --dry-run
   "$B" files --repo PATH --flow pr|main
   ```

   An existing `settings.json` is merged, never replaced. A file that exists with other content is a conflict
   (exit 11): nothing is written until the person decides.

   **A repo that already has a board and files from an earlier, hand-made copy of this system.** `preflight`
   exits 10 because the board is not marked as this skill's. Only when the person asks to move that repo onto
   this skill: `github --adopt N` (N is the board's number; it rewrites the board's short description as the
   marker), then `files --force` on a clean working tree, which replaces the differing tracked files.

   **Updating a repo that already has the system.** `preflight` exits 10 ("already set up") when the repo's
   files match this skill's current ones, and exits 0 with `next: files` when they are out of date. Running
   `files` there replaces the skill's own files with the current ones (`did` says "updated ...") and leaves
   everything else alone. A file with an uncommitted change is not replaced (exit 11). Show the dry run first.

4. **The person's part in GitHub's web UI.** The board's built-in workflows cannot be set through the API.
   Read `references/github-ui-steps.md` and give the person its checklist with the real URL
   (`project.workflows_url`) and the repo's name filled in. Then wait for them to say it is done.

5. **Verify.** Ask first whether to run the smoke test: it files one real issue in the repo, titled
   "Set up issue tracking and project board", cycles it through the board and leaves it closed as the record
   of the setup. It is the only way to check what the workflows actually do.

   ```bash
   "$B" verify --repo PATH --smoke      # takes up to 4 minutes: give the Bash call a 300000 ms timeout
   "$B" verify --repo PATH              # without the issue: checks only that the workflows are switched on
   ```

   On exit 12, `todo` names the workflow to fix; show that item of the checklist again and rerun. Without
   `--smoke`, say plainly what `unverified` lists and that the first real issue will be the test.

6. **Hand over.** Show `git -C PATH status --short`. Say:
   - the files are not committed: this skill never commits. Offer to commit them.
   - hooks load when a session starts, so a session already open in that repo must be restarted to get them.
   - how to use it from here: the `issues` skill in that repo, and `.claude/skills/issues/scripts/issue.sh`.

## Bundled files

- `scripts/bootstrap.sh`: every step above. Its header documents the options and exit codes.
- `references/github-ui-steps.md`: the checklist for step 4, and what each workflow is for. Read it before
  step 4 and whenever `verify` exits 12.
- `references/maintaining.md`: how the bundled files relate to the repo they were generalised from, and the
  tests to run after changing anything under `assets/` or `scripts/`. Read it before editing this skill.
- `assets/`: what gets installed. `skills/issues/` (the installed skill: `SKILL.md.tmpl` is rendered with the
  repo's names, `scripts/issue.sh` is copied as it is), `hooks/` (five hook scripts), `github/` (issue
  templates and the pull request template), `settings.hooks.json` (the hook wiring that is merged in).
