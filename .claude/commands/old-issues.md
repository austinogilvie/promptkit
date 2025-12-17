---
description: Show status summary of specs and issues in a project
argument-hint: <project-path>
allowed-tools: Read, Glob, Grep
---

Show the current status of specs and issues in a project directory.

**Input:** `$ARGUMENTS` — path to a project directory (e.g., `user-auth/`, `./my-project`)

---

## Resolving the Project Path

1. **If `$ARGUMENTS` is provided:** Use it as the project path
2. **If `$ARGUMENTS` is empty:** Check for session context:
   - Look for `.claude/session/current-project`
   - If file exists: read the path from it and use that
   - If file doesn't exist: ask the user for a path

When using session context, note it in output: `(using active project from /set-project)`

---

## How It Works

### 1. Find the project

Validate that the path exists and contains `specs/` and/or `issues/` subdirectories. If neither exists, report that this doesn't appear to be a project directory.

### 2. Discover files

**Specs:** Find files matching `{project}/specs/SPEC_*.md`

**Issues:** Find files matching `{project}/issues/NNN-*.md` where NNN is a zero-padded number (e.g., `001-setup.md`, `042-refactor.md`)

Files that don't match these patterns are "non-standard" — note them but don't analyze them.

### 3. Determine status from checkboxes

For each spec and issue, **read the file** and count checkboxes:

- `- [x]` or `- [X]` → completed task
- `- [ ]` → incomplete task

**Status logic:**

| Condition | Status |
|-----------|--------|
| All checkboxes checked | **Complete** |
| Some checked, some not | **In Progress** |
| None checked | **Open** |
| No checkboxes at all | **No Tasks** (flag for review) |

**Important:** Status comes only from checkbox state. Never infer status from directory names, file age, or anything else.

### 4. Map relationships

Issues link to specs via their `## Source` section. Group issues under their parent spec.

Issues without a Source section are "unlinked" — still show them, but note the missing link.

---

## Output Format

```markdown
# {project-name}

## SPEC_{name}.md — {status} ({n}/{m} criteria)

| # | Issue | Status | Progress |
|---|-------|--------|----------|
| 001 | setup-oauth | Complete | 5/5 |
| 002 | google-provider | In Progress | 2/4 |
| 003 | github-provider | Open | 0/3 |

## Unlinked Issues

- 099-orphan.md — Complete (3/3) — *missing Source section*

## Summary

- **Specs:** 1 complete, 0 in progress
- **Issues:** 12 complete, 3 in progress, 2 open
- **Next:** `003-github-provider.md` (first open issue)
```

Adapt the format based on what you find:
- If there's only one spec, you can simplify
- If there are no issues, just show specs
- If everything is complete, celebrate 🎉

---

## What This Command Does NOT Do

- Modify any files (read-only)
- Move files to `done/` directories
- Fix broken references (use `/fix-issue-relationships`)
- Reconcile status discrepancies (use `/fix-issue-status`)

This command **observes and reports**. It's the quick-glance view of project status.

---

## Examples

```bash
# Typical usage
/issues user-auth/

# Current directory project
/issues ./

# After creating issues from a spec
/create-issues my-feature/specs/SPEC_my-feature.md
/issues my-feature/
```

---

## Related Tools

| Type | Name | Purpose |
|------|------|---------|
| command | `/set-project` | Set active project (avoids typing path each time) |
| command | `/show-project` | Display the currently active project |
| command | `/clear-project` | Unset the active project |
| command | `/create-spec` | Create a new spec document |
| command | `/create-issues` | Break a spec into issue files |
| command | `/fix-issue-status` | Sync checkbox state with README |
| command | `/fix-issue-relationships` | Fix broken spec/issue references |
| agent | `issues-housekeeper` | Full audit with validation checks |
