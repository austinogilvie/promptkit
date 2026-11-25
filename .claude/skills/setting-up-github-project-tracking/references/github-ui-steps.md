# The steps only GitHub's web UI can do

GitHub's API can create a project board, its fields and its link to a repo. It cannot switch on or configure
the board's built-in workflows; it can only report each workflow's name and whether it is on. So a person
does this part, once per board, and `bootstrap.sh verify` checks it afterwards.

Give the person the checklist below with the two placeholders filled in: `<WORKFLOWS_URL>` is
`project.workflows_url` from the script's output, `<REPO NAME>` is the repo's name without its owner.
Give it only after the `github` step has finished, so the Status options the workflows point at are final.

## The checklist

```text
Three settings on the board that only GitHub's website can change. About two minutes.

Open <WORKFLOWS_URL>
(If that page does not open: open the board, click the "..." menu at the top right, then "Workflows".)

1. Auto-add to project
   - Click "Auto-add to project" in the list on the left, then "Edit" at the top right.
   - Under "Filters", choose the repository <REPO NAME>.
   - Set the filter box to:  is:issue
   - Click "Save and turn on workflow".

2. Item closed
   - Click "Item closed". It should say On, with Status: Done under "Set value".
   - If it is off or says another status: "Edit", set Status to Done, "Save and turn on workflow".

3. Item reopened
   - Click "Item reopened". It should say On, with Status: Todo under "Set value".
   - If it is off or says another status: "Edit", set Status to Todo, "Save and turn on workflow".

Leave everything else as you find it, including "Sync with issue status" at the top of the list.

Tell me when the three are on and I will check them.
```

## What each one is for

| workflow | effect | why the system needs it |
|---|---|---|
| Auto-add to project | every new issue in the repo appears on the board | an issue filed in the web UI or by another tool reaches the board without anyone adding it |
| Item closed → Done | closing an issue (or a commit or PR that says `Closes #n`) moves it to Done | status is never set to Done by hand |
| Item reopened → Todo | reopening an issue moves it out of Done | a reopened issue does not sit in Done |

## Sync with issue status: why a reopened issue may land in Backlog

Since late November 2026 a GitHub issue has a status of its own (Backlog, Todo, In progress, In review, Done,
Not planned, Duplicate), shown in the issue's header, and a new issue starts in Backlog. A board has a
workflow at the top of its list, "Sync with issue status", that keeps an item's Status and its issue's status
the same wherever the names match. New boards have been seen with it on.

With sync on, the page of every built-in workflow says: "For issues, Sync with issue status sets the value
that matches the issue's status instead, when there is one." So:

- a reopened issue goes to the issue's own status, Backlog, even though "Item reopened" says Todo;
- a new issue arrives on the board as Backlog, even when "Item added to project" is on and says Todo.

Both are fine for this system: Backlog is where a new or reopened issue belongs until someone plans it, and
`verify --smoke` accepts Todo or Backlog after a reopen. Do not ask the person to "fix" a reopened issue that
landed in Backlog when "Item reopened" already says Todo; nothing is set wrong.

With sync off (boards made before the feature, or where someone switched it off), "Item reopened" decides,
and "Item added to project" should be off or the hook's Backlog is replaced by Todo for every new issue.

The issue's own status is readable (`gh api repos/<owner>/<repo>/issues/<n> -q .status.name`; the `status`
field of `Issue` in GraphQL). `issue.sh` does not read or set it: it sets the board's Status, and the sync
carries that to the issue.

## Variations

- **Pull requests on the board too.** Only if the person wants PRs as board items: in step 1 use the filter
  `is:issue,pr`. "Pull request merged" with Status Done then matters. Not needed for issues to close: a PR
  that says `Closes #n` closes the issue, and "Item closed" moves it.
- **Plan limits.** An account on GitHub's Free plan gets one auto-add workflow; paid plans get more. If the
  filter cannot be saved, an existing auto-add workflow on another board is using the allowance.
- **The auto-add workflow only sees issues created or updated after it is switched on.** Issues that existed
  before are added with `.claude/skills/issues/scripts/issue.sh board <number> --status Backlog --priority P2`.

## What `verify` can and cannot see

`verify` reads the workflows by name and reports (exit 12) any of the three that is missing from the list or
switched off. "Sync with issue status" is not in the API's list at all, so `verify` cannot tell whether it is on.

The API does not expose what a workflow is set to do: which repository and filter auto-add uses, or which
status "Item closed" and "Item reopened" set. `verify --smoke` covers that by filing one real issue with a
plain `gh issue create` and watching the board: the issue must appear by itself, go to Done when closed and
leave Done (for Todo or Backlog) when reopened. When one of those fails, the script's `todo` names the
workflow to open and what to set. Before passing a failure on to the person, read the status the issue
actually has (`issue.sh board <n>`) and check it against the section above.
