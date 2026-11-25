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
   - Click "Item closed", then "Edit".
   - In the "Set value" box, Status should be Done. Change it if it is not.
   - Click "Save and turn on workflow".

3. Item reopened
   - Click "Item reopened", then "Edit".
   - In the "Set value" box, set Status to Todo.
   - Click "Save and turn on workflow".

Leave the other workflows as they are. In particular leave "Item added to project" off.

Tell me when the three are on and I will check them.
```

## What each one is for

| workflow | effect | why the system needs it |
|---|---|---|
| Auto-add to project | every new issue in the repo appears on the board | an issue filed in the web UI or by another tool reaches the board without anyone adding it |
| Item closed → Done | closing an issue (or a commit or PR that says `Closes #n`) moves it to Done | status is never set to Done by hand |
| Item reopened → Todo | reopening an issue moves it back to Todo | a reopened issue does not sit in Done |

"Item added to project" stays off: a new issue's first status, Backlog, is set by the installed
`issue.sh create` and by the `board-new-issue.sh` hook, which also set the priority. If that workflow were on,
it would put every new issue in Todo.

## Variations

- **Pull requests on the board too.** Only if the person wants PRs as board items: in step 1 use the filter
  `is:issue,pr`, and also turn on "Pull request merged" with Status Done. Not needed for issues to close: a PR
  that says `Closes #n` closes the issue, and "Item closed" moves it.
- **Plan limits.** An account on GitHub's Free plan gets one auto-add workflow; paid plans get more. If the
  filter cannot be saved, an existing auto-add workflow on another board is using the allowance.
- **The auto-add workflow only sees issues created or updated after it is switched on.** Issues that existed
  before are added with `.claude/skills/issues/scripts/issue.sh board <number> --status Backlog --priority P2`.

## What `verify` can and cannot see

`verify` reads the workflows by name and reports (exit 12) any of the three that is missing from the list or
switched off. "Auto-add to project" and "Item reopened" do not appear in the API's list at all until someone
has saved them once.

The API does not expose what a workflow is set to do: which repository and filter auto-add uses, or which
status "Item closed" and "Item reopened" set. `verify --smoke` covers that by filing one real issue with a
plain `gh issue create` and watching the board: the issue must appear by itself, go to Done when closed and to
Todo when reopened. When one of those fails, the script's `todo` names the workflow to open and what to set.
